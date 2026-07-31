#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, py_compile, re, subprocess, sys
import yaml
from release_content import canonical_bytes
try: import jsonschema
except Exception: jsonschema=None
ROOT=Path(__file__).resolve().parents[1]; NAME='senior-fullstack-engineer-agent'; VERSION=(ROOT/'VERSION').read_text(encoding='utf-8').strip(); SRC=ROOT/'source'/NAME; PLUGIN=ROOT/'plugins'/NAME
IGNORED_DIRS={'dist','.git','__pycache__','.pytest_cache','.mypy_cache','qualification-results','release-evidence','validation'}
def ignored(path): return any(part in IGNORED_DIRS for part in path.parts)
errors=[]; checks=[]
def ok(n,d=''): checks.append({'name':n,'ok':True,'detail':d})
def bad(n,d): errors.append({'name':n,'detail':d}); checks.append({'name':n,'ok':False,'detail':d})
def parse(path):
 t=path.read_text(encoding='utf-8'); end=t.find('\n---\n',4)
 if not t.startswith('---\n') or end<0: raise ValueError('invalid frontmatter')
 return yaml.safe_load(t[4:end]) or {},t
source_skills=[SRC/'SKILL.md']+sorted(SRC.glob('workflows/*/SKILL.md')); plugin_skills=sorted((PLUGIN/'skills').glob('*/SKILL.md'))
for label,skills in [('source',source_skills),('plugin',plugin_skills)]:
 if len(skills)!=20: bad('skill-count',f'{label}={len(skills)}')
 else: ok('skill-count',f'{label}=20')
 names=[]
 for p in skills:
  try: fm,_=parse(p)
  except Exception as e: bad('skill-frontmatter',f'{p}: {e}'); continue
  if set(fm)!={'name','description'}: bad('frontmatter-fields',f'{p}: {sorted(fm)}')
  if fm.get('name')!=p.parent.name: bad('skill-name',f'{p}: {fm.get("name")}')
  if not isinstance(fm.get('description'),str) or not 20<=len(fm['description'])<=1024: bad('skill-description',str(p))
  names.append(fm.get('name'))
 if len(names)!=len(set(names)): bad('duplicate-skill-name',label)
# Non-root source/plugin skill sync.
for p in sorted(SRC.glob('workflows/*/SKILL.md')):
 q=PLUGIN/'skills'/p.parent.name/'SKILL.md'
 if not q.exists() or p.read_bytes()!=q.read_bytes(): bad('source-plugin-sync',p.parent.name)
ok('source-plugin-sync','specialist skills match') if not any(e['name']=='source-plugin-sync' for e in errors) else None
sync=subprocess.run([sys.executable,str(ROOT/'scripts/sync_skill_references.py'),'--check'],capture_output=True,text=True,encoding='utf-8',errors='replace')
if sync.returncode: bad('self-contained-skill-references',((sync.stdout or '')+(sync.stderr or '')).strip())
else: ok('self-contained-skill-references','specialist references are local and synchronized')
catalog=subprocess.run([sys.executable,str(ROOT/'scripts/generate_skill_catalog.py'),'--check'],capture_output=True,text=True,encoding='utf-8',errors='replace')
if catalog.returncode: bad('skill-catalog-sync',((catalog.stdout or '')+(catalog.stderr or '')).strip())
else: ok('skill-catalog-sync','catalog matches canonical Skill frontmatter')
# openai.yaml exists and parses.
for skill_dir in [PLUGIN/'skills'/p.parent.name for p in plugin_skills]:
 y=skill_dir/'agents/openai.yaml'
 if not y.is_file(): bad('openai-yaml',f'missing {y}'); continue
 try:
  d=yaml.safe_load(y.read_text(encoding='utf-8')) or {}; interface=d.get('interface',{})
  for k in ['display_name','short_description','default_prompt']:
   if not interface.get(k): bad('openai-yaml',f'{y}: missing {k}')
 except Exception as e: bad('openai-yaml',f'{y}: {e}')
# Links.
for p in ROOT.rglob('*.md'):
 if ignored(p): continue
 t=p.read_text(encoding='utf-8')
 for link in re.findall(r'\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)',t):
  target=(p.parent/link.split('#')[0]).resolve()
  if not target.exists(): bad('relative-link',f'{p}: {link}')
# Structured files and schemas.
ids={}
for p in list(ROOT.rglob('*.json'))+list(ROOT.rglob('*.yaml'))+list(ROOT.rglob('*.yml')):
 if ignored(p): continue
 try: d=json.loads(p.read_text(encoding='utf-8')) if p.suffix=='.json' else yaml.safe_load(p.read_text(encoding='utf-8'))
 except Exception as e: bad('structured-file',f'{p}: {e}'); continue
 if p.suffix=='.json' and p.name.endswith('.schema.json') and jsonschema:
  try: jsonschema.Draft202012Validator.check_schema(d)
  except Exception as e: bad('json-schema',f'{p}: {e}')
 if '/evals/' in p.as_posix() and isinstance(d,dict):
  for c in d.get('cases',[]):
   if 'id' in c:
    if c['id'] in ids: bad('duplicate-eval-id',f"{c['id']}: {ids[c['id']]} and {p}")
    ids[c['id']]=str(p)
# Trigger balance and manifest.
manifest=json.loads((SRC/'evals/trigger/manifest.json').read_text(encoding='utf-8'))
manifest_names={x['skill'] for x in manifest['skills']}
expected={p.parent.name for p in SRC.glob('workflows/*/SKILL.md')}|{NAME}
if manifest_names!=expected: bad('trigger-manifest',f'missing={expected-manifest_names}, extra={manifest_names-expected}')
for skill in expected:
 p=SRC/'evals/trigger/router_trigger_evals.json' if skill==NAME else SRC/'workflows'/skill/'evals/trigger_evals.json'
 cases=json.loads(p.read_text(encoding='utf-8')); pos=sum(bool(c['should_trigger']) for c in cases); neg=len(cases)-pos
 if pos!=neg: bad('trigger-balance',f'{skill}: {pos}/{neg}')
# Versions.
manifest_plugin=json.loads((PLUGIN/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
for label,val in [('plugin',manifest_plugin.get('version')),('source',(SRC/'VERSION').read_text(encoding='utf-8').strip())]:
 if val!=VERSION: bad('version',f'{label}={val}, root={VERSION}')
# Required RC4.1 resources.
for p in [SRC/'core/router-policy.md',SRC/'core/routing-matrix.yaml',SRC/'eval-engine/catalog/skill-catalog.json',SRC/'eval-engine/config/context-map.json',ROOT/'scripts/sfse_installer.py',ROOT/'tests/test_transaction_installer.py']:
 if not p.exists(): bad('required-rc4.1',str(p))
# Python compile; prohibit caches.
for p in ROOT.rglob('*.py'):
 if ignored(p): continue
 try: py_compile.compile(str(p),doraise=True,cfile=str(Path('/tmp')/(hashlib.sha256(str(p).encode()).hexdigest()+'.pyc')))
 except Exception as e: bad('python-compile',f'{p}: {e}')
for p in ROOT.rglob('*'):
 if ignored(p): continue
 if p.name=='__pycache__' or p.suffix in {'.pyc','.pyo'}: bad('generated-cache',str(p))
# Manifest coverage and hashes.
def manifest_expected(base):
 out={}
 for p in sorted(base.rglob('*')):
  if not p.is_file() or ignored(p) or p.suffix in {'.pyc','.pyo'} or p.name in {'MANIFEST.json','SBOM.spdx.json'}: continue
  out[p.relative_to(base).as_posix()]=hashlib.sha256(canonical_bytes(p)).hexdigest()
 return out
for base in [SRC,PLUGIN]:
 mp=base/'MANIFEST.json'
 try:
  md=json.loads(mp.read_text(encoding='utf-8')); actual={x['path']:x['sha256'] for x in md['files']}; expected_files=manifest_expected(base)
  if actual!=expected_files: bad('manifest-coverage',f'{base}: expected {len(expected_files)}, manifest {len(actual)}')
  else: ok('manifest-coverage',f'{base}: {len(actual)} files')
 except Exception as e: bad('manifest-coverage',f'{base}: {e}')

# No misleading GA claims.
for p in [ROOT/'README.md',SRC/'README.md',PLUGIN/'README.md']:
 if p.exists() and re.search(r'\bv1\.0\.0 GA\b|General Availability build',p.read_text(encoding='utf-8'),re.I): bad('misleading-ga-label',str(p))
result={'ok':not errors,'version':VERSION,'checks':checks,'errors':errors,'stats':{'source_skills':len(source_skills),'plugin_skills':len(plugin_skills),'eval_ids':len(ids),'trigger_cases':sum(x['cases'] for x in manifest['skills']),'python_files':len([p for p in ROOT.rglob('*.py') if not ignored(p)])},'eval_ids':len(ids)}; print(json.dumps(result,ensure_ascii=False,indent=2)); raise SystemExit(0 if not errors else 1)
