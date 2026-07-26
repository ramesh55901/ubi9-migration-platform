from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .analyzer import analyze
from .migrator import migrate
from .failure import analyze_failure, apply_safe_fix
from .report import generate

def dump(x): print(json.dumps(x,indent=2) if not isinstance(x,Path) else x)
def main():
    p=argparse.ArgumentParser(prog="ubi9-agent"); sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("analyze"); a.add_argument("--repo",default="."); a.add_argument("--source")
    m=sub.add_parser("migrate"); m.add_argument("--repo",default="."); m.add_argument("--source",required=True); m.add_argument("--config",default="config/ubi9-migration.yaml"); m.add_argument("--no-ai",action="store_true")
    f=sub.add_parser("analyze-failure"); f.add_argument("--repo",default="."); f.add_argument("--dockerfile",required=True); f.add_argument("--log",required=True); f.add_argument("--config",default="config/ubi9-migration.yaml"); f.add_argument("--no-ai",action="store_true")
    x=sub.add_parser("apply-safe-fix"); x.add_argument("--repo",default="."); x.add_argument("--dockerfile",required=True); x.add_argument("--analysis",default="reports/failure-analysis.json")
    r=sub.add_parser("report"); r.add_argument("--repo",default=".")
    args=p.parse_args()
    if args.cmd=="analyze": dump(analyze(args.repo,args.source))
    elif args.cmd=="migrate": dump(migrate(args.repo,args.source,args.config,args.no_ai))
    elif args.cmd=="analyze-failure": dump(analyze_failure(args.repo,args.dockerfile,args.log,args.config,args.no_ai))
    elif args.cmd=="apply-safe-fix": sys.exit(0 if apply_safe_fix(args.repo,args.dockerfile,args.analysis) else 2)
    elif args.cmd=="report": dump(generate(args.repo))
if __name__=="__main__": main()
