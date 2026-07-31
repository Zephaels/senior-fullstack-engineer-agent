#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, contextlib, datetime as dt, hashlib, json, os, shutil, tempfile, uuid
PLUGIN_NAME='senior-fullstack-engineer-agent'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def tree_hash(root: Path):
 h=hashlib.sha256()
 for p in sorted(root.rglob('*')):
  if p.is_file(): h.update(p.relative_to(root).as_posix().encode()); h.update(b'\0'); h.update(p.read_bytes())
 return h.hexdigest()
def atomic_json(path: Path,data):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); os.replace(tmp,path)
def validate_plugin(root: Path, *, allow_staging: bool = False):
 p=root/'.codex-plugin/plugin.json'
 if not p.is_file(): raise RuntimeError('missing .codex-plugin/plugin.json')
 m=json.loads(p.read_text(encoding='utf-8'))
 if m.get('name')!=root.name and not allow_staging:
        raise RuntimeError(f"plugin folder/name mismatch: {root.name} != {m.get('name')}")
 skills=root/'skills'
 if not skills.is_dir() or not list(skills.glob('*/SKILL.md')): raise RuntimeError('plugin contains no Skills')
 return m
class Lock:
 def __init__(self,path): self.path=path; self.fd=None
 def __enter__(self):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  try: self.fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(self.fd,str(os.getpid()).encode())
  except FileExistsError: raise RuntimeError(f'installer lock exists: {self.path}')
  return self
 def __exit__(self,*_):
  if self.fd is not None: os.close(self.fd)
  self.path.unlink(missing_ok=True)

def paths(home: Path):
 agents=home/'.agents/plugins'; return {'target':home/'plugins'/PLUGIN_NAME,'marketplace':agents/'marketplace.json','state':agents/'state'/f'{PLUGIN_NAME}.json','lock':agents/'locks'/f'{PLUGIN_NAME}.lock','backups':agents/'backups'/PLUGIN_NAME}
def load_marketplace(path):
 if not path.exists(): return {'name':'personal','interface':{'displayName':'Personal Plugins'},'plugins':[]}
 d=json.loads(path.read_text(encoding='utf-8')); d.setdefault('plugins',[]); return d
def update_marketplace(data,installed=True):
 ps=[p for p in data.get('plugins',[]) if p.get('name')!=PLUGIN_NAME]
 if installed: ps.append({'name':PLUGIN_NAME,'source':{'source':'local','path':f'./plugins/{PLUGIN_NAME}'},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Developer Tools'})
 data['plugins']=ps; return data
def failpoint(name):
 if os.environ.get('SFSE_INSTALLER_FAIL_AT')==name: raise RuntimeError(f'injected failure at {name}')
def transaction(source: Path,home: Path,mode:str,dry=False):
 source=source.resolve(); m=validate_plugin(source); P=paths(home); target=P['target']; current=target.exists()
 if mode=='install' and current: raise RuntimeError('plugin already installed; use upgrade')
 if mode=='upgrade' and not current: raise RuntimeError('plugin not installed; use install')
 plan={'mode':mode,'source':str(source),'target':str(target),'version':m.get('version'),'dry_run':dry}
 if dry: return {'ok':True,'plan':plan}
 with Lock(P['lock']):
  txn=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]; P['backups'].mkdir(parents=True,exist_ok=True); target.parent.mkdir(parents=True,exist_ok=True)
  # Keep the transient directory short.  The full plugin name plus a
  # timestamp can push otherwise valid installations past Windows MAX_PATH.
  stage=target.parent/f'.s-{uuid.uuid4().hex[:8]}'; backup=P['backups']/txn/'plugin'; market_backup=P['backups']/txn/'marketplace.json'; had_market=P['marketplace'].exists(); old_hash=tree_hash(target) if current else None
  shutil.copytree(source,stage); validate_plugin(stage,allow_staging=True); staged_hash=tree_hash(stage); failpoint('after-stage')
  if had_market: market_backup.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(P['marketplace'],market_backup)
  switched=False
  try:
   if current: backup.parent.mkdir(parents=True,exist_ok=True); os.replace(target,backup)
   os.replace(stage,target); switched=True; failpoint('after-switch')
   atomic_json(P['marketplace'],update_marketplace(load_marketplace(P['marketplace']),True)); failpoint('after-marketplace')
   verify(home,expected_hash=staged_hash)
   state={'plugin':PLUGIN_NAME,'status':'installed','version':m.get('version'),'installed_at':now(),'target':str(target),'hash':staged_hash,'previous_hash':old_hash,'backup_path':str(backup) if current else None,'marketplace_backup':str(market_backup) if had_market else None,'transaction_id':txn}
   atomic_json(P['state'],state); return {'ok':True,'plan':plan,'state':state}
  except Exception:
   with contextlib.suppress(Exception):
    if switched and target.exists(): shutil.rmtree(target)
    if backup.exists(): os.replace(backup,target)
    if had_market and market_backup.exists(): shutil.copy2(market_backup,P['marketplace'])
    elif not had_market: P['marketplace'].unlink(missing_ok=True)
   raise
  finally:
   if stage.exists(): shutil.rmtree(stage,ignore_errors=True)
def verify(home: Path,expected_hash=None):
 P=paths(home); m=validate_plugin(P['target']); market=load_marketplace(P['marketplace']); entry=next((p for p in market.get('plugins',[]) if p.get('name')==PLUGIN_NAME),None)
 if not entry: raise RuntimeError('marketplace entry missing')
 if entry.get('source',{}).get('path')!=f'./plugins/{PLUGIN_NAME}': raise RuntimeError('marketplace path invalid')
 actual=tree_hash(P['target'])
 if expected_hash and actual!=expected_hash: raise RuntimeError('installed tree hash mismatch')
 return {'ok':True,'version':m.get('version'),'hash':actual,'target':str(P['target']),'marketplace':str(P['marketplace'])}
def rollback(home: Path):
 P=paths(home); state=json.loads(P['state'].read_text(encoding='utf-8')); backup=Path(state.get('backup_path') or '')
 if not backup.is_dir(): raise RuntimeError('no rollback backup available')
 with Lock(P['lock']):
  current_archive=P['backups']/('rollback-from-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))/'plugin'; current_archive.parent.mkdir(parents=True,exist_ok=True)
  if P['target'].exists(): os.replace(P['target'],current_archive)
  os.replace(backup,P['target'])
  mb=state.get('marketplace_backup')
  if mb and Path(mb).exists(): shutil.copy2(mb,P['marketplace'])
  else: atomic_json(P['marketplace'],update_marketplace(load_marketplace(P['marketplace']),True))
  v=verify(home); atomic_json(P['state'],{'plugin':PLUGIN_NAME,'status':'rolled_back','version':v['version'],'rolled_back_at':now(),'target':str(P['target']),'hash':v['hash'],'backup_path':str(current_archive)})
  return v
def uninstall(home: Path):
 P=paths(home)
 if not P['target'].exists(): return {'ok':True,'status':'already_absent'}
 with Lock(P['lock']):
  txn=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]; backup=P['backups']/txn/'plugin'; backup.parent.mkdir(parents=True,exist_ok=True); os.replace(P['target'],backup)
  atomic_json(P['marketplace'],update_marketplace(load_marketplace(P['marketplace']),False)); atomic_json(P['state'],{'plugin':PLUGIN_NAME,'status':'uninstalled','uninstalled_at':now(),'backup_path':str(backup)})
  return {'ok':True,'status':'uninstalled','backup_path':str(backup)}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['install','upgrade','rollback','uninstall','verify']); ap.add_argument('--source'); ap.add_argument('--home',default=str(Path.home())); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--output'); a=ap.parse_args(); home=Path(a.home).resolve()
 try:
  if a.command in {'install','upgrade'}:
   if not a.source: raise RuntimeError('--source is required')
   result=transaction(Path(a.source),home,a.command,a.dry_run)
  elif a.command=='rollback': result=rollback(home)
  elif a.command=='uninstall': result=uninstall(home)
  else: result=verify(home)
 except Exception as e: result={'ok':False,'error':str(e)}
 if a.output: atomic_json(Path(a.output),result)
 print(json.dumps(result,ensure_ascii=False,indent=2)); raise SystemExit(0 if result.get('ok') else 1)
if __name__=='__main__': main()
