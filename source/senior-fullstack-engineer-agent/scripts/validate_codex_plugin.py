#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
PLUGIN=Path('/mnt/data/senior-fullstack-engineer-plugin')
errors=[]
manifest_path=PLUGIN/'.codex-plugin'/'plugin.json'
if not manifest_path.exists(): errors.append('missing .codex-plugin/plugin.json')
else:
    try: m=json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'invalid plugin.json: {e}'); m={}
    for k in ['name','version','description','author','license','skills','interface']:
        if not m.get(k): errors.append(f'manifest missing {k}')
    if m.get('skills')!='./skills/': errors.append('skills path must be ./skills/')
    if (PLUGIN/'.codex-plugin').exists():
        extra=[p.name for p in (PLUGIN/'.codex-plugin').iterdir() if p.name!='plugin.json']
        if extra: errors.append(f'extra files in .codex-plugin: {extra}')
    iface=m.get('interface',{})
    for k in ['displayName','shortDescription','longDescription','developerName','category','capabilities','defaultPrompt']:
        if not iface.get(k): errors.append(f'interface missing {k}')
skills_dir=PLUGIN/'skills'
if not skills_dir.is_dir(): errors.append('missing skills directory')
skill_count=0; links=0
for p in sorted(skills_dir.glob('*/SKILL.md')) if skills_dir.exists() else []:
    skill_count+=1; text=p.read_text(encoding='utf-8')
    mm=re.match(r'^---\n(.*?)\n---\n',text,re.S)
    if not mm: errors.append(f'missing frontmatter {p}'); continue
    fm=mm.group(1); name=re.search(r'^name:\s*(.+)$',fm,re.M); desc=re.search(r'^description:\s*(.+)$',fm,re.M)
    if not name or name.group(1).strip()!=p.parent.name: errors.append(f'name mismatch {p}')
    if not desc or not 1<=len(desc.group(1).strip())<=1024: errors.append(f'description invalid {p}')
    if len(text.splitlines())>500: errors.append(f'over 500 lines {p}')
    for rel in re.findall(r'\[[^\]]+\]\(([^)]+\.md)\)',text):
        links+=1
        target=(p.parent/rel).resolve()
        if not target.exists(): errors.append(f'broken link {p}: {rel}')
if skill_count<19: errors.append(f'expected at least 19 bundled skills, got {skill_count}')
for f in ['README.md','LICENSE','NOTICE.md','MANIFEST.json']:
    if not (PLUGIN/f).exists(): errors.append(f'missing {f}')
result={'ok':not errors,'errors':errors,'summary':{'skill_count':skill_count,'links':links,'manifest':str(manifest_path)}}
print(json.dumps(result,ensure_ascii=False,indent=2)); sys.exit(0 if not errors else 1)
