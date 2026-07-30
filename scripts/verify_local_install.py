#!/usr/bin/env python3
from pathlib import Path
import argparse, subprocess, sys
ap=argparse.ArgumentParser(); ap.add_argument('--home',default=str(Path.home())); a=ap.parse_args(); raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).with_name('sfse_installer.py')),'verify','--home',a.home]))
