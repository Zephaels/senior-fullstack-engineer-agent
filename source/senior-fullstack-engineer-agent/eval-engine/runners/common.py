from pathlib import Path
import json, shlex, subprocess, tempfile, time

def invoke_runner(template: str, request: dict, timeout: int=300) -> dict:
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); req=td/'request.json'; resp=td/'response.json'
        req.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
        cmd=template.format(request=shlex.quote(str(req)),response=shlex.quote(str(resp)))
        started=time.time(); cp=subprocess.run(cmd,shell=True,text=True,capture_output=True,timeout=timeout)
        rec={'seconds':round(time.time()-started,3),'exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
        if cp.returncode!=0 or not resp.exists():
            rec['status']='runner_error'; return rec
        try: data=json.loads(resp.read_text(encoding='utf-8'))
        except Exception as exc:
            rec['status']='runner_error'; rec['error']=f'invalid response JSON: {exc}'; return rec
        rec.update(data); rec['status']='completed'; return rec
