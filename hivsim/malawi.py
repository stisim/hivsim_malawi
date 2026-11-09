"""
HIVsim for Malawi: the uncalibrated skeleton for P3.

Data files go in hivsim/data/ (see the README there). Parameter values
marked "to calibrate" are placeholders until the P3 target set is agreed.

    python malawi.py          # short check run
"""
from pathlib import Path
import numpy as np
import pandas as pd
import sciris as sc
import starsim as ss
import stisim as sti

datadir = Path(__file__).parent / 'data'
location = 'malawi'
start = 1985 # Optima starts in 1990; the comparison is 2000-2020

required = [f'{location}_age_{start}.csv', f'{location}_asfr.csv', f'{location}_deaths.csv', 'init_prev_hiv.csv', 'n_art.csv']
optional = ['condom_use.csv', 'vmmc.csv', 'vls.csv']


def check_data():
    """ Stop with a list of the required data files that are missing """
    missing = [f for f in required if not (datadir/f).exists()]
    if missing:
        raise FileNotFoundError(f'Missing from {datadir}: {", ".join(missing)} (see the README there)')


def read(filename, **kwargs):
    """ Read an optional data file, or return None if it isn't there """
    path = datadir/filename
    return pd.read_csv(path, **kwargs) if path.exists() else None


def make_testing(test_scale=1, test_rel_m=1, test_start=2004, cd4_test_start=None, cd4_test_prob=None):
    """
    HIV testing: general population, people with low CD4, and ANC. General testing scales up linearly from test_start
    to 2020, to a level multiplied by test_scale; men's is test_rel_m times women's. Testing of people with CD4 < 200
    follows the same scale-up (0.8 × test_scale at full), unless cd4_test_start and cd4_test_prob are given: then it
    is a programme of its own (advanced HIV, from the start of the ART programme), rising linearly over 5 years from
    cd4_test_start to an annual probability of cd4_test_prob
    """
    def scaleup(sim):
        return np.clip((sim.t.now('year') - test_start) / (2020 - test_start), 0, 1)

    def general_prob(sim, uids):
        rel = np.where(sim.people.female[uids], 1.0, test_rel_m)
        return np.minimum(0.1 * test_scale * scaleup(sim) * rel, 1)

    def low_cd4_prob(sim, uids):
        if cd4_test_start is None:
            return np.full(len(uids), min(0.8 * test_scale * scaleup(sim), 1))
        return np.full(len(uids), cd4_test_prob * np.clip((sim.t.now('year') - cd4_test_start) / 5, 0, 1))

    undiagnosed = lambda sim: ~sim.diseases.hiv.diagnosed & ~sim.diseases.hiv.on_art
    general = sti.HIVTest(name='general_testing', test_prob_data=general_prob, start=1990, eligibility=undiagnosed)
    low_cd4 = sti.HIVTest(name='low_cd4_testing', test_prob_data=low_cd4_prob, start=1990,
                          eligibility=lambda sim: undiagnosed(sim) & (sim.diseases.hiv.cd4 < 200))
    anc = sti.ANCTest(visit_prob=0.9, start=2004) # Malawi's PMTCT programme; to calibrate
    return [general, low_cd4, anc]


cd4_eligibility = [(2011, 200), (2014, 350), (2016, 500)] # Malawi's CD4 thresholds for starting ART: <200 to 2010, <350 2011-13, <500 2014-15, everyone from 2016 (test and treat)


class ARTEligibility(sti.ART):
    """ sti.ART where a first start needs a CD4 count below Malawi's threshold of the year (cd4_eligibility), or, from
    Option B+ in 2011, pregnancy; restarts are not limited. Diagnosed people who aren't eligible wait until they are """
    def ready(self, uids=None):
        ok = super().ready(uids)
        if uids is None:
            return ok
        year = self.sim.t.now('year')
        limit = next((cd4 for y, cd4 in cd4_eligibility if year < y), np.inf)
        preg = self.sim.demographics.pregnancy.P[uids] if year >= 2011 else np.zeros(len(uids), bool)
        return ok & ((self.hiv.cd4[uids] < limit) | ~self.art_naive[uids] | preg)


def make_sim(seed=1, n_agents=10e3, stop=2021, verbose=1/12, hiv_pars=None, nw_pars=None, art_pars=None, test_scale=1, test_rel_m=1, test_start=2004,
             cd4_test_start=None, cd4_test_prob=None, cd4_elig=False, condom_scale=1, **kwargs):
    """ Make the Malawi sim; hiv_pars, nw_pars and art_pars are parameter values for sti.HIV, sti.StructuredSexual and sti.ART; condom_scale multiplies condom use (at most 1); cd4_elig limits first ART starts to Malawi's CD4 thresholds (ARTEligibility); see make_testing for the others """
    check_data()

    condoms = read('condom_use.csv')
    if condoms is not None:
        condoms = condoms.set_index('partnership').mul(condom_scale).clip(upper=1).reset_index()
    nw = sti.StructuredSexual(condom_data=condoms, **(nw_pars or {}))
    hiv = sti.HIV(**{
        'beta_m2f': 0.01, # To calibrate
        'init_prev_data': read('init_prev_hiv.csv'),
        'age_bins': [0, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 100], # The surveys' age groups
    } | (hiv_pars or {}))

    n_art = read('n_art.csv', index_col='year')
    vmmc = read('vmmc.csv') # Share of men circumcised, by age
    vls = read('vls.csv', index_col='year')
    art = (ARTEligibility if cd4_elig else sti.ART)(coverage=n_art, vls_coverage=vls, **(art_pars or {}))
    intvs = make_testing(test_scale, test_rel_m, test_start, cd4_test_start, cd4_test_prob) + [art]
    if vmmc is not None:
        intvs.append(sti.VMMC(coverage=vmmc))

    sim = sti.Sim(
        n_agents=n_agents,
        start=start,
        stop=stop,
        datafolder=datadir,
        demographics=location,
        diseases=hiv,
        networks=[nw, ss.PrenatalNet()],
        interventions=intvs,
        rand_seed=seed,
        verbose=verbose,
        **kwargs,
    )
    return sim


if __name__ == '__main__':
    sim = make_sim(n_agents=2e3, verbose=0)
    with sc.timer():
        sim.run()
    df = sim.to_df(resample='year', use_years=True, sep='.')
    print(df[['time', 'hiv.prevalence_15_49', 'hiv.on_art']].iloc[::5].to_string())
