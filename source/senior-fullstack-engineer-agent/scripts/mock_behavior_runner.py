#!/usr/bin/env python3
"""Transport-only mock for validating the behavior harness. Not a model evaluation."""
from pathlib import Path
import argparse, json
ap=argparse.ArgumentParser()
ap.add_argument('--request',required=True)
ap.add_argument('--response',required=True)
a=ap.parse_args()
req=json.loads(Path(a.request).read_text(encoding='utf-8'))
config=req['configuration']
response={
  'response': f"HARNESS_SELF_TEST configuration={config} case={req['case_id']} skill_paths={len(req.get('skill_paths',[]))}",
  'tool_calls': [],
  'metadata': {'runner':'mock_transport_only','not_a_model_evaluation':True}
}
Path(a.response).write_text(json.dumps(response,ensure_ascii=False,indent=2),encoding='utf-8')
