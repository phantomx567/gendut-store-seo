#!/usr/bin/env python3
"""Apply an authenticated private owner withdrawal export locally. Never approves or publishes."""
import argparse,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_selection',ROOT/'scripts/release-selection.py');selection=importlib.util.module_from_spec(spec);spec.loader.exec_module(selection)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--export',type=Path,required=True);p.add_argument('--manifest',type=Path);p.add_argument('--render-output',type=Path);a=p.parse_args();print(json.dumps(selection.withdraw(ROOT,a.export,a.manifest,a.render_output)))
