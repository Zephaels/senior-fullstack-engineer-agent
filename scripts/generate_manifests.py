#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
from release_content import canonical_bytes
ROOT=Path(__file__).resolve().parents[1]; VERSION=(ROOT/'VERSION').read_text(encoding='utf-8').strip(); NAME='senior-fullstack-engineer-agent'
EXCLUDED_DIRS={'dist','.git','__pycache__','.pytest_cache','.mypy_cache','qualification-results','release-evidence','validation'}
def iter_files(base,skip_names):
 for p in sorted(base.rglob('*')):
  if not p.is_file() or any(part in EXCLUDED_DIRS for part in p.parts) or p.suffix in {'.pyc','.pyo'} or p.name in skip_names: continue
  yield p
def build(base,manifest_path,kind,root_name=None):
 rows=[]
 for p in iter_files(base,{'MANIFEST.json','SBOM.spdx.json'}):
  b=canonical_bytes(p); rows.append({'path':p.relative_to(base).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
 data={'schema_version':'1.0','kind':kind,'version':VERSION,'root':root_name or base.name,'file_count':len(rows),'files':rows}
 manifest_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); return data
def sbom(base,path,package_name):
 files=[]
 for p in iter_files(base,{'MANIFEST.json','SBOM.spdx.json'}):
  b=canonical_bytes(p); files.append({'fileName':'./'+p.relative_to(base).as_posix(),'checksums':[{'algorithm':'SHA256','checksumValue':hashlib.sha256(b).hexdigest()}]})
 data={'spdxVersion':'SPDX-2.3','dataLicense':'CC0-1.0','SPDXID':'SPDXRef-DOCUMENT','name':f'{package_name}-{VERSION}','documentNamespace':f'https://example.invalid/spdx/{package_name}/{VERSION}','creationInfo':{'creators':['Tool: sfse-manifest-generator'],'created':'2026-07-30T00:00:00Z'},'packages':[{'name':package_name,'SPDXID':'SPDXRef-Package','versionInfo':VERSION,'downloadLocation':'NOASSERTION','filesAnalyzed':True,'licenseConcluded':'Apache-2.0','licenseDeclared':'Apache-2.0'}],'files':files,'relationships':[{'spdxElementId':'SPDXRef-DOCUMENT','relationshipType':'DESCRIBES','relatedSpdxElement':'SPDXRef-Package'}]}
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=ROOT/'source'/NAME; plugin=ROOT/'plugins'/NAME
build(source,source/'MANIFEST.json','skill-source'); sbom(source,source/'SBOM.spdx.json',NAME+'-source')
build(plugin,plugin/'MANIFEST.json','codex-plugin'); sbom(plugin,plugin/'SBOM.spdx.json',NAME+'-plugin')
build(ROOT,ROOT/'MANIFEST.json','release-repository',f'{NAME}-{VERSION}'); sbom(ROOT,ROOT/'SBOM.spdx.json',NAME+'-release')
print(json.dumps({'ok':True,'version':VERSION},indent=2))
