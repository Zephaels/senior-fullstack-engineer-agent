from pathlib import Path
import ctypes, json, os, shlex, subprocess, tempfile


def command_arg(value) -> str:
    """Quote one value for backwards-compatible command-template construction."""
    value = str(value)
    return subprocess.list2cmdline([value]) if os.name == "nt" else shlex.quote(value)


def command_argv(template: str, request: Path, response: Path) -> list[str]:
    """Parse a maintainer-supplied judge template without invoking a shell."""
    if not template or not template.strip():
        raise ValueError("judge command template is empty")
    if template.lstrip().startswith("["):
        argv = json.loads(template)
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
            raise ValueError("JSON judge command must be a non-empty string array")
    elif os.name == "nt":
        argc = ctypes.c_int()
        command_line_to_argv = ctypes.windll.shell32.CommandLineToArgvW
        command_line_to_argv.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
        command_line_to_argv.restype = ctypes.POINTER(ctypes.c_wchar_p)
        pointer = command_line_to_argv(template, ctypes.byref(argc))
        if not pointer:
            raise ValueError("unable to parse Windows judge command")
        try:
            argv = [pointer[index] for index in range(argc.value)]
        finally:
            ctypes.windll.kernel32.LocalFree(pointer)
    else:
        argv = shlex.split(template, posix=True)
    rendered = [item.format(request=str(request), response=str(response)) for item in argv]
    if not rendered or any(not item for item in rendered):
        raise ValueError("judge command contains an empty argument")
    return rendered

def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def write_json(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def safe_div(a,b): return a/b if b else 0.0

def canonical_skill_name(name):
    """Return the catalog name for either bare or Plugin-namespaced skills."""
    return str(name).rsplit(':',1)[-1]

def canonical_skill_names(names):
    return {canonical_skill_name(name) for name in names}

def invoke_judge(template,request,timeout=300):
    with tempfile.TemporaryDirectory() as td:
        req=Path(td)/'request.json'; resp=Path(td)/'response.json'; req.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
        try:
            cmd=command_argv(template,req,resp)
        except Exception as exc:
            return {'status':'judge_error','error':f'invalid judge command: {exc}'}
        cp=subprocess.run(cmd,shell=False,text=True,capture_output=True,timeout=timeout)
        if cp.returncode!=0 or not resp.exists(): return {'status':'judge_error','exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
        try: data=json.loads(resp.read_text(encoding='utf-8'))
        except Exception as e: return {'status':'judge_error','error':str(e)}
        return {'status':'completed',**data}
