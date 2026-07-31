#!/usr/bin/env python3
from pathlib import Path
import datetime as dt, hashlib, json, os, stat, zipfile
from release_content import canonical_bytes
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'; OUT.mkdir(exist_ok=True); VERSION=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
EPOCH=max(int(os.environ.get('SOURCE_DATE_EPOCH','315532800')),315532800); DT=dt.datetime.fromtimestamp(EPOCH,dt.timezone.utc); ZIP_DT=(DT.year,DT.month,DT.day,DT.hour,DT.minute,DT.second)
EXCLUDE={
 'dist','.git','.venv','venv','env','node_modules','.tox','.nox',
 '__pycache__','.pytest_cache','.mypy_cache','qualification-results',
 'release-evidence','validation'
}
def excluded(p):
 return any(part in EXCLUDE for part in p.parts) or p.name=='.env' or p.name.startswith('.env.')
def files(source):
 for p in sorted(source.rglob('*')):
  if not p.is_file() or excluded(p) or p.suffix in {'.pyc','.pyo'}: continue
  yield p
def make(path,source,arc_root):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files(source):
   content=canonical_bytes(p); arc=(Path(arc_root)/p.relative_to(source)).as_posix(); info=zipfile.ZipInfo(arc,ZIP_DT); info.compress_type=zipfile.ZIP_DEFLATED; mode=0o755 if p.suffix=='.py' and content.startswith(b'#!') else 0o644; info.external_attr=((stat.S_IFREG|mode)<<16); info.create_system=3; z.writestr(info,content)
 return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'entries':len(zipfile.ZipFile(path).infolist())}
for p in OUT.iterdir():
 if p.is_file(): p.unlink()
packages=[]
packages.append(make(OUT/f'Senior-FullStack-Engineer-Agent-{VERSION}-Plugin.zip',ROOT/'plugins/senior-fullstack-engineer-agent','senior-fullstack-engineer-agent'))
packages.append(make(OUT/f'Senior-FullStack-Engineer-Agent-{VERSION}-Skill-Source.zip',ROOT/'source/senior-fullstack-engineer-agent','senior-fullstack-engineer-agent'))
packages.append(make(OUT/f'Senior-FullStack-Engineer-Agent-{VERSION}-Complete-Source.zip',ROOT,f'senior-fullstack-engineer-agent-{VERSION}'))
(OUT/'release-packages.json').write_text(json.dumps({'version':VERSION,'source_date_epoch':EPOCH,'packages':packages},indent=2)+'\n',encoding='utf-8')
(OUT/'CHECKSUMS.sha256').write_text(''.join(f"{x['sha256']}  {Path(x['path']).name}\n" for x in packages),encoding='utf-8')
print(json.dumps({'ok':True,'version':VERSION,'packages':packages},indent=2))
