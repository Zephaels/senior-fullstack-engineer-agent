#!/usr/bin/env python3
"""Generate the metadata-first evaluation catalog from canonical Skill frontmatter."""
from pathlib import Path
import argparse, json, sys, yaml

ROOT=Path(__file__).resolve().parents[1]
NAME='senior-fullstack-engineer-agent'
SOURCE=ROOT/'source'/NAME
OUTPUT=SOURCE/'eval-engine'/'catalog'/'skill-catalog.json'

def frontmatter(path):
    text=path.read_text(encoding='utf-8'); end=text.find('\n---\n',4)
    if not text.startswith('---\n') or end<0: raise ValueError(f'invalid frontmatter: {path}')
    return yaml.safe_load(text[4:end]) or {}

def build():
    paths=[SOURCE/'SKILL.md']+sorted(SOURCE.glob('workflows/*/SKILL.md'))
    rows=[]
    for path in paths:
        data=frontmatter(path)
        rows.append({'name':data['name'],'description':data['description'],'path':path.relative_to(SOURCE).as_posix()})
    rows.sort(key=lambda row:row['name'])
    return {'skills':rows}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args(); data=build()
    expected=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding='utf-8')!=expected:
            print(f'{OUTPUT} is stale; run generate_skill_catalog.py',file=sys.stderr); return 1
    else:
        OUTPUT.write_text(expected,encoding='utf-8')
    print(f'Skill catalog contains {len(data["skills"])} canonical entries.')
    return 0

if __name__=='__main__': raise SystemExit(main())
