"""
Exp 04: run HIVsim Malawi (low-CD4 testing as its own programme, mortality on ART from EMOD's table) over a Latin
hypercube of the ranges in config.yaml, 3 seeds each, in two arms (without and with Malawi's CD4 eligibility for ART),
and 10 seeds of the central set per arm; write each run's target values to outputs/results.jsonl as it finishes; then
plot (hivsim/targetfit.py) and check the stopping rule

    nice python run.py          # Run and analyse
    python run.py analyse       # Analyse only
"""
import sys
import json
import traceback
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import pandas as pd
import sciris as sc
from scipy.stats import qmc
import stisim as sti

here = Path(__file__).parent
sys.path.insert(0, str(here.parents[1] / 'hivsim'))
import malawi
import targetfit

cfg = sc.loadyaml(here / 'config.yaml')
outfile = here / 'outputs' / 'results.jsonl'
art_pars = dict(art_death_table=sti.ART.emod_death_table)


def to_value(u, low, high, scale):
    return float(np.exp(np.log(low) + u*(np.log(high) - np.log(low)))) if scale == 'log' else float(low + u*(high - low))


def run_one(job):
    arm, kind, i, seed, pars = job
    try:
        hiv_pars = {k[4:]: v for k, v in pars.items() if k.startswith('hiv_')}
        nw_pars = {k[3:]: v for k, v in pars.items() if k.startswith('nw_')}
        other = {k: v for k, v in pars.items() if not k.startswith(('hiv_', 'nw_'))}
        T = sc.timer()
        sim = malawi.make_sim(seed=seed, n_agents=cfg['n_agents'], stop=cfg['stop'], verbose=0, analyzers=targetfit.TargetRecorder(),
                              hiv_pars=hiv_pars, nw_pars=nw_pars, art_pars=art_pars, **cfg['arms'][arm], **other).run()
        values = targetfit.measure(sim)
        years = np.asarray(sim.t.yearvec)
        on_art = np.asarray(sim.results.hiv.on_art)
        n_art = malawi.read('n_art.csv', index_col='year').n_art
        art_reached = {int(y): float(on_art[np.argmin(abs(years - y))] / n_art[y]) for y in (2005, 2010, 2015, 2020)}
        yr = lambda key: {int(y): float(np.asarray(key)[(years >= y) & (years < y + 1)].sum()) for y in (2005, 2010, 2015, 2020, 2021)}
        deaths = dict(all=yr(sim.results.hiv.new_deaths), on_art=yr(sim.results.art.new_deaths))
        return dict(arm=arm, kind=kind, i=i, seed=seed, pars=pars, values={int(k): v for k, v in values.items()}, art_reached=art_reached,
                    deaths=deaths, time=T.toc(output=True))
    except Exception:
        return dict(arm=arm, kind=kind, i=i, seed=seed, pars=pars, error=traceback.format_exc())


def jobs():
    names = list(cfg['pars'])
    u = qmc.LatinHypercube(d=len(names), seed=cfg['seed']).random(cfg['n_samples'])
    central = {n: to_value(0.5, *cfg['pars'][n]) for n in names}
    for arm in cfg['arms']:
        for i, row in enumerate(u):
            for s in range(cfg['n_seeds']):
                yield arm, 'sample', i, 1 + cfg['n_seeds']*i + s, {n: to_value(x, *cfg['pars'][n]) for n, x in zip(names, row)}
        for s in range(cfg['n_seeds_central']):
            yield arm, 'central', s, 10000 + s, central


def analyse():
    """ Figures for each arm (runs, and seed means of each parameter set), the stopping rule, and the best runs """
    targets = targetfit.load_targets()
    rows = []
    for arm in cfg['arms']:
        sel = lambda r, arm=arm: r.get('arm') == arm
        for mean_seeds, suffix in [(False, f'_{arm}'), (True, f'_{arm}_seedmean')]:
            targetfit.plot(here, select=sel, mean_seeds=mean_seeds, suffix=suffix)
            pars, vals, recs = targetfit.load_runs(here, sel, mean_seeds)
            rule = targetfit.stopping_rule(vals, targets)
            scores = np.array([targetfit.score(dict(r.dropna()), targets) for _, r in vals.iterrows()])
            rule['score'] = scores
            rule.join(pars).to_csv(here / 'outputs' / f'stopping_rule{suffix}.csv')
            passed = rule.index[rule[['art_unaids', 'mphia', 'plhiv']].all(axis=1)]
            prev = targets[(targets.target == 'prevalence') & (targets.group == 'all')]
            q = vals.loc[passed, prev.index].quantile([0.05, 0.95]) if len(passed) else None
            covered = int(((prev.value >= q.loc[0.05]) & (prev.value <= q.loc[0.95])).sum()) if q is not None else 0
            rows.append(dict(arm=arm, unit='set (mean of 3 seeds)' if mean_seeds else 'run', n=len(vals), **rule[['art_unaids', 'mphia', 'plhiv', 'aids_deaths', 'prev_band', 'all']].sum().to_dict(),
                             art_mphia_plhiv=len(passed), prev_points_in_their_90=f'{covered}/{len(prev)}', best_score=float(np.nanmin(scores)), median_score=float(np.nanmedian(scores))))
    table = pd.DataFrame(rows)
    table.to_csv(here / 'outputs' / 'stopping_rule_summary.csv', index=False)
    print(table.to_string())


if __name__ == '__main__':
    if 'analyse' not in sys.argv:
        outfile.parent.mkdir(exist_ok=True)
        outfile.write_text('')
        alljobs = list(jobs())
        with Pool(min(len(alljobs), 150)) as pool, outfile.open('a') as f:
            for k, res in enumerate(pool.imap_unordered(run_one, alljobs)):
                f.write(json.dumps(res) + '\n')
                f.flush()
                if 'error' in res:
                    print(f'Run {res["arm"]} {res["kind"]} {res["i"]} failed:\n{res["error"]}')
                print(f'{k+1}/{len(alljobs)} done', flush=True)
    analyse()
