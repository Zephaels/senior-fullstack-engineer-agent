#!/usr/bin/env python3
"""Compatibility entry point for Eval Engine v2.

This file intentionally does not concatenate the full Skill tree. Use the metadata-first,
isolated-context, and real-Plugin runtime runners under eval-engine/runners.
"""
from pathlib import Path
import runpy
TARGET=Path(__file__).resolve().parents[1]/'eval-engine/runners/run_behavior_evals_v2.py'
runpy.run_path(str(TARGET),run_name='__main__')
