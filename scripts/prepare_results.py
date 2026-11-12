"""Regenerate display tables from the public, checked measurement snapshot."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
v=json.loads((R/'data/results.json').read_text());rows=v['results']
native,kd=rows[1],rows[2]
assert all(x['n_samples']==10000 and x['status']=='complete' for x in rows)
assert native['whole_dit_bpp']==kd['whole_dit_bpp'] and v['training']['changed_assignments']==0
gain=100*(native['fid']-kd['fid'])/native['fid']
macros={'FPFID':f"{rows[0]['fid']:.2f}",'NativeFID':f"{native['fid']:.2f}",'KDFID':f"{kd['fid']:.2f}",
 'FIDGain':f'{gain:.1f}','WholeBpp':f"{kd['whole_dit_bpp']:.2f}",'FPGap':f"{kd['fid']-rows[0]['fid']:.2f}"}
article=[];slides=[];primary=[];auxiliary=[]
for i,x in enumerate(rows):
 label=['Full-precision reference','VQDM, layerwise only','VQDM + output calibration'][i]
 fields=[label,'32' if i==0 else f"{x['whole_dit_bpp']:.4f}",f"{x['fid']:.3f}",f"{x['sfid']:.3f}",f"{x['inception_score']:.3f}",f"{x['precision']:.4f}",f"{x['recall']:.4f}"]
 article.append(' & '.join(fields)+r' \\')
 name=['FP reference','Layerwise VQDM','VQDM + output calibration'][i]
 fields=[name,'IN256 / 10k','32' if i==0 else f"{x['whole_dit_bpp']:.4f}",f"{x['fid']:.3f}",f"{x['sfid']:.3f}"]
 primary.append(' & '.join(fields)+r' \\')
 fields=[name,f"{x['inception_score']:.3f}",f"{x['precision']:.4f}",f"{x['recall']:.4f}"]
 auxiliary.append(' & '.join(fields)+r' \\')
 fields=[['Исходная DiT','Послойный VQDM','VQDM + выход сети'][i],'32' if i==0 else f"{x['whole_dit_bpp']:.2f}".replace('.',','),f"{x['fid']:.2f}".replace('.',','),f"{x['sfid']:.2f}".replace('.',',')]
 if i==2:fields=['\\textbf{'+f+'}' for f in fields]
 slides.append(' & '.join(fields)+r' \\')
macros['ArticleRows']='\n'.join(article);macros['SlideRows']='\n'.join(slides)
macros['PrimaryRows']='\n'.join(primary);macros['AuxiliaryRows']='\n'.join(auxiliary)
temporal=json.loads((R/'data/temporal_results.json').read_text())
assert temporal['protocol']['steps']==50 and temporal['protocol']['n_samples']==10000
assert all(x['codebook_sets']*x['updates_per_set']==1000 for x in temporal['results'])
temporal_rows=[]
for x in temporal['results']:
 label='Один общий' if x['codebook_sets']==1 else 'Пять временных'
 updates='1\\,000' if x['codebook_sets']==1 else r'$5\times200$'
 fields=[label,updates,f"{x['whole_dit_bpp']:.3f}".replace('.',','),f"{x['fid']:.3f}".replace('.',',')]
 temporal_rows.append(' & '.join(fields)+r' \\')
macros['TemporalRows']='\n'.join(temporal_rows)
plot='position fid label\n'+''.join(f"{i} {x['fid']} {x['fid']:.2f}\n".replace(f"{x['fid']:.2f}\n",f"{x['fid']:.2f}".replace('.',',')+'\n') for i,x in enumerate(rows))
(R/'data/fid_plot.dat').write_text(plot)
text='% Generated from data/results.json and data/temporal_results.json.\n'
text+='\n'.join('\\newcommand{\\'+k+'}{'+x+'}' for k,x in macros.items())+'\n'
(R/'data/numbers.tex').write_text(text)
with (R/'data/results.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['model','whole_dit_bpp','n_samples','fid','sfid','inception_score','precision','recall']);w.writeheader()
 for x in rows:w.writerow({k:x[k] for k in w.fieldnames})
print(f'FID reduction: {gain:.4f}%; fixed whole-DiT storage: {kd["whole_dit_bpp"]:.8f} bpp')
