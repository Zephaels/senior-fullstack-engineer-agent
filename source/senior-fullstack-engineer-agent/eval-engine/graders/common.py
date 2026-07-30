from pathlib import Path
import json, shlex, subprocess, tempfile

def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def write_json(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def safe_div(a,b): return a/b if b else 0.0

def invoke_judge(template,request,timeout=300):
    with tempfile.TemporaryDirectory() as td:
        req=Path(td)/'request.json'; resp=Path(td)/'response.json'; req.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
        cmd=template.format(request=shlex.quote(str(req)),response=shlex.quote(str(resp)))
        cp=subprocess.run(cmd,shell=True,text=True,capture_output=True,timeout=timeout)
        if cp.returncode!=0 or not resp.exists(): return {'status':'judge_error','exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
        try: data=json.loads(resp.read_text(encoding='utf-8'))
        except Exception as e: return {'status':'judge_error','error':str(e)}
        return {'status':'completed',**data}
