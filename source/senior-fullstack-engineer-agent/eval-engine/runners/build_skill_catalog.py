#!/usr/bin/env python3
from pathlib import Path
import argparse, json, yaml

def parse_skill(path: Path):
    text=path.read_text(encoding='utf-8')
    end=text.find('\n---\n',4)
    if not text.startswith('---\n') or end<0:
        raise ValueError(f'invalid frontmatter: {path}')
    fm=yaml.safe_load(text[4:end]) or {}
    return {'name':fm['name'],'description':fm['description'],'path':str(path)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--skills-root',required=True)
    ap.add_argument('--output',required=True)
    a=ap.parse_args(); root=Path(a.skills_root).resolve()
    skills=[]
    for p in sorted(root.glob('*/SKILL.md')):
        skills.append(parse_skill(p))
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'skills':skills},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'skills':len(skills),'output':str(out)},indent=2))
if __name__=='__main__': main()
