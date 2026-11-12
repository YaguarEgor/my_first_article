"""Rebuild article and slides with Tectonic, or XeLaTeX/BibTeX."""
import argparse,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--engine',default='tectonic');args=p.parse_args()
subprocess.run([sys.executable,str(R/'scripts/prepare_results.py')],check=True)
engine=str(Path(shutil.which(args.engine) or args.engine).resolve())
for rel in ('article/main.tex','slides/intermediate.tex','slides/one_slide.tex'):
    path=R/rel
    if Path(engine).name=='tectonic':subprocess.run([engine,'--keep-logs',path.name],cwd=path.parent,check=True)
    else:
        cmd=[engine,'-interaction=nonstopmode','-halt-on-error',path.name]
        subprocess.run(cmd,cwd=path.parent,check=True)
        if rel.startswith('article/'):
            subprocess.run(['bibtex',path.stem],cwd=path.parent,check=True)
        subprocess.run(cmd,cwd=path.parent,check=True);subprocess.run(cmd,cwd=path.parent,check=True)
