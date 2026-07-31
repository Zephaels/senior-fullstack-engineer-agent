#!/usr/bin/env python3
"""Make every specialist Skill self-contained inside Source and Plugin trees."""
from pathlib import Path
import argparse, re, shutil, sys

ROOT=Path(__file__).resolve().parents[1]
NAME='senior-fullstack-engineer-agent'
SOURCE=ROOT/'source'/NAME
PLUGIN=ROOT/'plugins'/NAME
CORE=SOURCE/'core'
CORE_NAMES=(
    'constitution.md',
    'task-classifier.md',
    'decision-policy.md',
    'autonomy-policy.md',
)
CORE_LINK=re.compile(
    r'\((?:\.\./){2}core/(constitution|task-classifier|decision-policy|autonomy-policy)\.md\)'
)
SKILL_LINK=re.compile(r'\[([^\]]+)\]\(\.\./([a-z0-9-]+)/SKILL\.md\)')
CORE_WORKFLOW_LINK=re.compile(r'\[([^\]]+)\]\(\.\./workflows/([a-z0-9-]+)/SKILL\.md\)')
ROOT_CORE_LINK=re.compile(r'\((?:\./)?core/([a-z0-9-]+\.(?:md|yaml))\)')
ROOT_CORE_NAMES=(
    'constitution.md',
    'router-policy.md',
    'routing-matrix.yaml',
    'task-classifier.md',
    'decision-policy.md',
    'autonomy-policy.md',
)
AUTONOMY_SUPPORT=(
    ('templates/autonomy-run-envelope.json','references/templates/autonomy-run-envelope.json'),
    ('templates/autonomy-run-plan.json','references/templates/autonomy-run-plan.json'),
    ('schemas/autonomy-run-envelope.schema.json','references/schemas/autonomy-run-envelope.schema.json'),
    ('schemas/autonomy-run-plan.schema.json','references/schemas/autonomy-run-plan.schema.json'),
    ('scripts/validate_autonomy_envelope.py','scripts/validate_autonomy_envelope.py'),
    ('scripts/validate_autonomy_plan.py','scripts/validate_autonomy_plan.py'),
    ('scripts/autonomy_supervisor.py','scripts/autonomy_supervisor.py'),
)

def rendered(text):
    text=CORE_LINK.sub(lambda m:f'(./references/core/{m.group(1)}.md)',text)
    return SKILL_LINK.sub(lambda m:f'`{m.group(2)}`',text)

def rendered_core(text):
    """Render canonical core guidance for a self-contained specialist Skill.

    Canonical core files may link to sibling workflows from ``core/``. Once a
    core file is copied below ``<skill>/references/core/``, that relative path
    no longer exists. Keep the routing instruction while removing the broken
    repository-layout dependency.
    """
    return CORE_WORKFLOW_LINK.sub(lambda m:f'`{m.group(2)}`',text)

def sync_file(source, target, check, errors):
    expected=source.read_bytes()
    if check:
        if not target.is_file() or target.read_bytes()!=expected:
            errors.append(f'{target}: missing or stale')
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(expected)

def sync_text(text, target, check, errors):
    if check:
        if not target.is_file() or target.read_text(encoding='utf-8')!=text:
            errors.append(f'{target}: missing or stale')
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding='utf-8')

def sync_root_skill(check, errors):
    source_skill=SOURCE/'SKILL.md'
    plugin_dir=PLUGIN/'skills'/NAME
    target_text=ROOT_CORE_LINK.sub(lambda m:f'(./references/core/{m.group(1)})',source_skill.read_text(encoding='utf-8'))
    plugin_skill=plugin_dir/'SKILL.md'
    if check:
        if not plugin_skill.is_file() or plugin_skill.read_text(encoding='utf-8')!=target_text:
            errors.append(f'{plugin_skill}: differs from canonical root Skill')
    else:
        plugin_dir.mkdir(parents=True,exist_ok=True)
        plugin_skill.write_text(target_text,encoding='utf-8')
    for name in ROOT_CORE_NAMES:
        source=CORE/name
        target=plugin_dir/'references'/'core'/name
        if source.suffix=='.md': sync_text(rendered_core(source.read_text(encoding='utf-8')),target,check,errors)
        else: sync_file(source,target,check,errors)
    for source in sorted((SOURCE/'templates').glob('*')):
        if source.is_file(): sync_file(source,plugin_dir/'assets'/'templates'/source.name,check,errors)
    for source in sorted((SOURCE/'schemas').glob('*')):
        if source.is_file(): sync_file(source,plugin_dir/'references'/'schemas'/source.name,check,errors)
    for source_rel,target_rel in AUTONOMY_SUPPORT[-3:]:
        sync_file(SOURCE/source_rel,plugin_dir/target_rel,check,errors)

def sync(check=False):
    errors=[]
    sync_root_skill(check,errors)
    for source_skill in sorted(SOURCE.glob('workflows/*/SKILL.md')):
        skill_name=source_skill.parent.name
        original=source_skill.read_text(encoding='utf-8')
        target_text=rendered(original)
        plugin_dir=PLUGIN/'skills'/skill_name
        plugin_skill=plugin_dir/'SKILL.md'
        needs_core='./references/core/' in target_text
        if check:
            if original!=target_text: errors.append(f'{source_skill}: contains non-self-contained links')
            if not plugin_skill.is_file() or plugin_skill.read_text(encoding='utf-8')!=target_text: errors.append(f'{plugin_skill}: differs from source')
        else:
            source_skill.write_text(target_text,encoding='utf-8')
            plugin_dir.mkdir(parents=True,exist_ok=True)
            plugin_skill.write_text(target_text,encoding='utf-8')
        if needs_core:
            for name in CORE_NAMES:
                canonical=CORE/name
                expected=rendered_core(canonical.read_text(encoding='utf-8'))
                for base in (source_skill.parent,plugin_dir):
                    local=base/'references'/'core'/name
                    if check:
                        if not local.is_file() or local.read_text(encoding='utf-8')!=expected: errors.append(f'{local}: missing or stale')
                    else:
                        local.parent.mkdir(parents=True,exist_ok=True)
                        local.write_text(expected,encoding='utf-8')
        if skill_name=='release-deployment':
            for source_rel,target_rel in AUTONOMY_SUPPORT:
                for base in (source_skill.parent,plugin_dir):
                    sync_file(SOURCE/source_rel,base/target_rel,check,errors)
    return errors

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    errors=sync(args.check)
    if errors:
        print('\n'.join(errors),file=sys.stderr); return 1
    print('Skill references are self-contained and synchronized.')
    return 0

if __name__=='__main__': raise SystemExit(main())
