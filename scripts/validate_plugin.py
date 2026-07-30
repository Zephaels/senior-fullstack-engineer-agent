#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys, yaml
SEMVER=re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$')
ap=argparse.ArgumentParser(); ap.add_argument('plugin'); a=ap.parse_args(); root=Path(a.plugin).resolve(); errors=[]
try: m=json.loads((root/'.codex-plugin/plugin.json').read_text())
except Exception as e: print(f'Plugin validation failed: {e}'); raise SystemExit(1)
allowed={'id','name','version','description','skills','apps','mcpServers','interface','author','homepage','repository','license','keywords'}
errors += [f'unsupported field {k}' for k in sorted(set(m)-allowed)]
for k in ['name','version','description','author','interface']:
 if not m.get(k): errors.append(f'missing {k}')
if m.get('name')!=root.name: errors.append('folder and name mismatch')
if not SEMVER.fullmatch(str(m.get('version',''))): errors.append('version must be strict semver')
if Path(str(m.get('skills',''))).as_posix().rstrip('/') not in {'skills','./skills'}: errors.append('skills must resolve to skills')
if 'apps' in m and not (root/'.app.json').is_file(): errors.append('apps without .app.json')
if 'mcpServers' in m and not (root/'.mcp.json').is_file(): errors.append('mcpServers without .mcp.json')
i=m.get('interface',{}); allowed_i={'displayName','shortDescription','longDescription','developerName','category','capabilities','websiteURL','privacyPolicyURL','termsOfServiceURL','brandColor','composerIcon','logo','logoDark','screenshots','defaultPrompt','default_prompt'}
errors += [f'unsupported interface field {k}' for k in sorted(set(i)-allowed_i)]
for k in ['displayName','shortDescription','longDescription','developerName','category','capabilities']:
 if not i.get(k): errors.append(f'missing interface.{k}')
p=i.get('defaultPrompt') or i.get('default_prompt')
if not isinstance(p,list) or not 1<=len(p)<=3 or any(not isinstance(x,str) or not x.strip() or len(x)>128 for x in p): errors.append('invalid defaultPrompt')
for k in ['composerIcon','logo','logoDark']:
 if k in i:
  q=(root/i[k]).resolve()
  if not q.is_file() or not q.is_relative_to(root): errors.append(f'invalid asset {k}')
for d in sorted((root/'skills').iterdir()):
 if not d.is_dir() or d.name.startswith('.'): continue
 s=d/'SKILL.md'
 if not s.is_file(): errors.append(f'missing SKILL.md {d.name}'); continue
 t=s.read_text(); end=t.find('\n---\n',4)
 if not t.startswith('---\n') or end<0: errors.append(f'frontmatter missing {d.name}'); continue
 try: fm=yaml.safe_load(t[4:end])
 except Exception: errors.append(f'frontmatter invalid {d.name}'); continue
 if fm.get('name')!=d.name: errors.append(f'name mismatch {d.name}')
 if not fm.get('description'): errors.append(f'description missing {d.name}')
print(('Plugin validation passed' if not errors else 'Plugin validation failed')+f': {root}')
for e in errors: print('- '+e)
raise SystemExit(0 if not errors else 1)
