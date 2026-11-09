# Exp 04 — With realistic mortality on ART, does testing for advanced HIV from 2004 give both early and later ART right?

**Question.** In [exp 03](../03_testing_art/SUMMARY.md), runs matched ART coverage and suppression, but only with a late general testing scale-up (2007-2009) that left almost no men on ART before 2010. Low-CD4 testing was tied to that scale-up, so nobody with advanced HIV was found before it. And once ART coverage was right, AIDS deaths fell far below UNAIDS (best run: 0.10 of them in 2021), because HIVsim's mortality on ART was 5-10 times too low (hivsim_paper analysis 13). If testing for advanced HIV (CD4 < 200) is a programme of its own from the start of ART in 2004, and mortality on ART follows EMOD's IeDEA-SA table, do runs meet the stopping rule (ART coverage, MPHIA's cascade, PLHIV from 2005, prevalence by age) with early ART for men and AIDS deaths closer to UNAIDS? And does limiting first ART starts to Malawi's CD4 thresholds help or hurt?

**What changed since exp 03.**
- STIsim: declared diseases on Starsim v4 rc3, STIsim branch `rs-v4-art-mortality` (PR #613 = #612, ART as its own declared module, plus the fix that makes condoms work for declared STIs, plus the mortality options). Starsim `v4-rs-nov09` (rc3 + starsim#1573). Declared STIsim ignored condoms before the fix; with it, exp 03's best set gives about 8% prevalence 15-49 in 2020, as before.
- `hivsim/malawi.py`: `ss.MaternalNet` → `ss.PrenatalNet`; `art_pars` for `sti.ART`; low-CD4 testing as its own programme (`cd4_test_start`, `cd4_test_prob`); `cd4_elig` with `ARTEligibility`. `hivsim/targetfit.py`: `sim.pop_scale` (rc3), `load_runs()`/`plot()` can select runs and average seeds, and `stopping_rule()`.
- **Mortality on ART:** `sti.ART(art_death_table=sti.ART.emod_death_table)` in every run: HIV deaths on ART by CD4 at the latest ART start and time since it (EMOD's table for men 25-35, × `art_death_age`, × `rel_death_f` for women, × 2 on non-suppressive ART). No `dur_reengage` (people who stop ART can still be restarted at once under the coverage target); that is for exp 05.
- **Testing for advanced HIV:** people with CD4 < 200 who are undiagnosed are tested at an annual probability that rises linearly over 5 years from `cd4_test_start` to `cd4_test_prob`, independently of general testing (which still rises from `test_start` to 2020, men's `test_rel_m` times women's). ANC testing from 2004 as before.
- **Two arms, the same parameter sets and seeds:**
  - `open`: anyone diagnosed can start ART (as in exp 03; the coverage target starts the lowest CD4 first).
  - `elig`: a first ART start needs CD4 below Malawi's threshold of the year: < 200 to 2010, < 350 2011-13, < 500 2014-15, everyone from 2016 (test and treat); pregnant women from Option B+ (2011). Restarts are not limited. The rule is analysis 13's `eligibility` variant. It ignores WHO clinical stage, which made some people with higher CD4 eligible, so it is stricter than the guidelines.

**Parameters and ranges** (uniform unless log; Latin hypercube of 200 sets):

| Parameter | Range | Exp 03 | Why |
|---|---|---|---|
| `hiv.beta_m2f` | 0.003-0.025 (log) | 0.002-0.05 | narrowed to exp 03's best 10% (0.004-0.015), with room for the extra deaths |
| `hiv.rel_init_prev`, network (`prop_f0`, `prop_m0`, `f1_conc`, `m1_conc`, `fsw_shares`, `client_shares`), `test_scale`, `condom_scale`, `test_rel_m`, `test_start` | as exp 03 | | exp 03's good runs spread over the whole ranges |
| `cd4_test_start` | 2002-2008 | (tied to `test_start`) | the ART programme began in 2004 |
| `cd4_test_prob` | 0.1-0.95 per year (log) | (0.8 × `test_scale` × general scale-up) | |

3 seeds per set (the same in both arms) and 10 seeds of the central set per arm: 1,220 runs, 10,000 agents, 1985-2022, about 8 s each.

**Scoring.** As in exp 03: `targetfit.score` (mean squared distance in units of each target's uncertainty, primary and secondary targets) to pick the best run, and `targetfit.plot` for the standard figures, per arm, by run and by set (mean of its 3 seeds). The stopping rule (`targetfit.stopping_rule`, `docs/targets.md`): within 10 points of UNAIDS ART coverage every year 2010-2021; within MPHIA 2020-21's intervals ± 5 points for ART coverage and suppression among PLHIV, both sexes (as exp 03 counted them); within × 1.5 of UNAIDS PLHIV every year from 2005; and prevalence by age in the middle 90% of runs. For the last, two readings are reported: per run, at least 90% of its 84 survey points inside the 5-95% band of all runs of its arm; and for the runs passing the other three, how many of the 84 data points lie inside their 5-95% band. Also reported: AIDS deaths within × 1.5 of UNAIDS from 2005, HIV deaths on ART, men on ART against programme data 2004-2015, and the ART input reached.

**Success.** At least 10 runs (or sets) meet all four criteria in one arm, with men on ART before 2010 near programme data (not a late-testing artefact) and AIDS deaths after 2015 within × 1.5 of UNAIDS more often than exp 03's runs. If the `elig` arm cannot reach the ART input before 2016, the CD4 rule is too strict for HIVsim's CD4 model (latent CD4 flat near 500) and needs WHO stage or a looser rule. If deaths stay low with ART right, the remaining gap is off ART (disengagement, `dur_reengage`), for exp 05.
