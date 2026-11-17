"""Frozen paired family bootstrap; source archived in code/frozen/analyze_panel.py."""
import numpy as np

def ci(x,label,simultaneous=False):
 x=np.asarray(x,float);n=len(x)
 if not n:return {'n_families':0,'estimate':None,'ci_low':None,'ci_high':None}
 # Same-family whole-row resampling. Separate conditional cohorts have separate deterministic streams.
 rng=np.random.Generator(np.random.PCG64(20261107))
 means=np.empty(20000)
 for off in range(0,20000,1000):means[off:off+1000]=x[rng.integers(0,n,(1000,n))].mean(1)
 q=[.025,.975] if not simultaneous else [.05/(2*6),1-.05/(2*6)]
 lo,hi=np.quantile(means,q)
 return {'n_families':n,'estimate':float(x.mean()),'ci_low':float(lo),'ci_high':float(hi),'bootstrap_replicates':20000,'interval':'percentile_family_paired' if not simultaneous else 'Bonferroni_percentile_six_model_by_newbase_comparisons'}
