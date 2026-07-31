from pathlib import Path
import ctypes, json, os, shlex, subprocess, tempfile, time


def command_arg(value) -> str:
    """Quote one value for backwards-compatible command-template construction."""
    value = str(value)
    return subprocess.list2cmdline([value]) if os.name == "nt" else shlex.quote(value)


def command_argv(template: str, request: Path, response: Path) -> list[str]:
    """Parse a maintainer-supplied runner template without invoking a shell."""
    if not template or not template.strip():
        raise ValueError("runner command template is empty")
    if template.lstrip().startswith("["):
        argv = json.loads(template)
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
            raise ValueError("JSON runner command must be a non-empty string array")
    elif os.name == "nt":
        argc = ctypes.c_int()
        command_line_to_argv = ctypes.windll.shell32.CommandLineToArgvW
        command_line_to_argv.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
        command_line_to_argv.restype = ctypes.POINTER(ctypes.c_wchar_p)
        pointer = command_line_to_argv(template, ctypes.byref(argc))
        if not pointer:
            raise ValueError("unable to parse Windows runner command")
        try:
            argv = [pointer[index] for index in range(argc.value)]
        finally:
            ctypes.windll.kernel32.LocalFree(pointer)
    else:
        argv = shlex.split(template, posix=True)
    rendered = [item.format(request=str(request), response=str(response)) for item in argv]
    if not rendered or any(not item for item in rendered):
        raise ValueError("runner command contains an empty argument")
    return rendered

def invoke_runner(template: str, request: dict, timeout: int=300) -> dict:
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); req=td/'request.json'; resp=td/'response.json'
        req.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
        try:
            cmd=command_argv(template,req,resp)
        except Exception as exc:
            return {'status':'runner_error','error':f'invalid runner command: {exc}'}
        started=time.time(); cp=subprocess.run(cmd,shell=False,text=True,capture_output=True,timeout=timeout)
        rec={'seconds':round(time.time()-started,3),'exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
        if cp.returncode!=0 or not resp.exists():
            rec['status']='runner_error'; return rec
        try: data=json.loads(resp.read_text(encoding='utf-8'))
        except Exception as exc:
            rec['status']='runner_error'; rec['error']=f'invalid response JSON: {exc}'; return rec
        # Preserve an explicit runner status.  A transport adapter can exit
        # successfully after writing structured evidence that all bounded
        # retries were exhausted; treating that as a completed model run would
        # contaminate qualification coverage.
        declared_status=data.get('status')
        rec.update(data); rec['status']=declared_status or 'completed'; return rec
