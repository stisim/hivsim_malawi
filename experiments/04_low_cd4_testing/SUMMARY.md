# Exp 04 — With realistic mortality on ART, does testing for advanced HIV from 2004 give both early and later ART right?

**DRAFT, awaiting Robyn's approval.** Not merged.

**Date:** 2026-11-09. STIsim `rs-v4-art-mortality` (PR #613, ebbc8e7), Starsim `/tmp/ss-nov09` (rc3 + starsim#1573), env `hp_rc3`.

**Question.** After [exp 03](../03_testing_art/SUMMARY.md), can runs meet the stopping rule (ART coverage, MPHIA's cascade, PLHIV from 2005, prevalence by age) with early ART for men and AIDS deaths closer to UNAIDS? Two changes: testing for advanced HIV (CD4 < 200) as a programme of its own from 2002-2008, and mortality on ART from EMOD's table (`art_death_table=sti.ART.emod_death_table`) in every run. Two arms use the same 200 parameter sets × 3 seeds: `open` (anyone diagnosed can start ART) and `elig` (first starts limited to Malawi's CD4 thresholds by year). See `README.md`.

**Result.** The stopping rule is not met. In `open`, 2 of 600 runs meet all four criteria, and they are two seeds of different parameter sets. In `elig`, none do. No parameter set meets them on the mean of its 3 seeds. Mortality on ART is now about right after 2010. In the best runs, AIDS deaths are 0.8-0.95× UNAIDS in 2010-2015 and 0.4-0.8× in 2018-2021 (exp 03 best: 0.10× in 2021). Testing for advanced HIV from 2004 gives men some ART early: in the best `open` run, men on ART are 0.4-0.75 of programme data in 2005-2015 (exp 03 best: zero before 2009). But women's are 1.5-2.3× the data in 2004-2008. Three things limit the fit:
- PLHIV before 2010 are too low (0.65-0.85× UNAIDS in 2000-2010). The ART input is a number of people, so ART coverage in 2010-2015 comes out too high.
- The CD4 rule cannot fill the ART input before 2014.
- At 10,000 agents, whether a run is within MPHIA ± 5 points depends on its seed.

![ART coverage (UNAIDS) and the MPHIA 2020-21 cascade by sex, `open` arm, 600 runs and the best run](figures/coverage_art_suppression_open.png)

![PLHIV, new infections, AIDS deaths, FSW prevalence, incidence and numbers on ART by sex, `open` arm](figures/coverage_time_series_open.png)

![Prevalence by sex and age for the five surveys, `open` arm](figures/coverage_prevalence_by_age_open.png)

![ART coverage and MPHIA cascade, `elig` arm](figures/coverage_art_suppression_elig.png)

Figures for `elig` and for the seed means (`*_seedmean.png`) are in `figures/`. Per-run checks with parameters are in `outputs/stopping_rule_*.csv`, and counts in `outputs/stopping_rule_summary.csv`.

## Scorecard

Exp 03's 200 runs are rescored with `targetfit.stopping_rule`, which reproduces its SUMMARY's counts. Exp 04 counts are runs out of 600 (200 sets × 3 seeds). In brackets: parameter sets out of 200, on the mean of their seeds.

| | Exp 03 (of 200) | Exp 04 `open` (of 600 [200]) | Exp 04 `elig` (of 600 [200]) |
|---|---|---|---|
| ART coverage within 10 points of UNAIDS, every year 2010-21 | 12 | 29 [8] | 27 [10] |
| MPHIA ART coverage and suppression, both sexes, within interval ± 5 points | 23 | 61 [24] | 66 [22] |
| PLHIV within × 1.5 of UNAIDS every year from 2005 | 27 | 138 [44] | 104 [28] |
| Prevalence by age: ≥ 90% of the run's 84 points in the runs' 5-95% band | 166 | 480 [158] | 487 [163] |
| **All four** | 2 | **2 [0]** | **0 [0]** |
| ART coverage and PLHIV (and MPHIA) | 2 (2) | 15 (2) | 2 (0) |
| AIDS deaths within × 1.5 of UNAIDS every year from 2005 (check) | 3 | 4 [3] | 3 [1] |
| Median AIDS deaths / UNAIDS, 2015 / 2021 (all runs) | 0.56 / 0.56 | 0.65 / 0.76 | 0.69 / 0.91 |
| Men on ART / programme data, median 2004-15: median run / ART-coverage-passing runs | 0.23 / 0.02 | 0.30 / 0.14 | 0.22 / 0.20 |
| ART input reached, median run, 2010 / 2020 | — / 0.95 | 0.98 / 0.69 | 0.31 / 0.78 |
| Best score (median) | 5.7 | 3.95 (26.6) | 4.04 (28.4) |

## Observations

1. **The best run is better than exp 03's on everything but ART coverage in 2010-2016.** The best run in both arms comes from the same parameter set: set 164, with `beta_m2f` 0.0075, `test_start` 2003, `test_scale` 2.3, `test_rel_m` 1.05, `cd4_test_start` 2006 and `cd4_test_prob` 0.12. Best `open` run (score 3.95):
   - MPHIA 2020-21, all six cascade points within 2.1 points: on ART, men 83.3% against 82.8%, women 90.8% against 88.7%; suppressed, men 81.4% against 80.1%, women 87.3% against 86.0%.
   - PLHIV 0.83-0.93× UNAIDS from 2005.
   - AIDS deaths 0.80 / 0.92 / 0.80 / 0.89 / 0.51× UNAIDS in 2010 / 2013 / 2015 / 2018 / 2021.
   - ART coverage 9-16 points *above* UNAIDS in 2011-2016, so it fails that criterion; it is within 4-5 points from 2018.
   - Prevalence: 45 of 84 survey points are inside the data's 95% interval. 15-49 prevalence is 0.65-0.9 of the surveys for men, and 0.8-1.1 for women.
2. **ART coverage in 2010-2016 is mostly PLHIV.** The ART input is a number of people, so a run with 15% too few PLHIV in 2010-2015 has about 15% too high a coverage. Across runs, reaching the ART input correlates with `beta_m2f` (Spearman 0.79 in 2020). When PLHIV are too low, testing can't find enough people to reach the input. In the median run, the input is reached only to 0.69 in 2020, and ART coverage falls 18 points below UNAIDS by 2021. The PLHIV gap goes back to the early epidemic: the best run is at 0.65× UNAIDS in 2000, and the median run at 0.49×. Every experiment since exp 02 has had this.
3. **Separate low-CD4 testing helps early ART for men, but ANC fills the early places with women.** In the best `open` run, men on ART are 0.97 / 0.52 / 0.45 / 0.48 of programme data in 2004 / 2005 / 2009 / 2010, against zero before 2009 in exp 03's best. Women are 2.3× the data in 2004-2005 and 1.5× in 2008. ANC testing (90% visit probability from 2004) diagnoses pregnant women before any CD4 testing, and the coverage target fills the places from them. Runs pass the ART coverage criterion with low `cd4_test_prob` (median 0.30 per year). Their men are still at 0.14 of the data, because the sex split comes from who is diagnosed.
4. **Malawi's CD4 rule, as modelled, is too strict for HIVsim's CD4 model before 2014.** In `elig`, the median run reaches 0.31 of the ART input in 2010, and 0.16 in 2005. The best `elig` run is 15 / 9 / 9 points below UNAIDS ART coverage in 2010 / 2012 / 2013, then within 4 points from 2014 (threshold 500, then test and treat). HIVsim's latent CD4 is flat near 500, and the decline through 200-350 takes under a year, so few people are below 200 at any time. The rule also leaves out WHO stage 3/4, which made many people eligible above CD4 200. With fewer people on ART, `elig` has more PLHIV (best run 0.93-1.07× UNAIDS from 2010) and more deaths (median 0.91× UNAIDS in 2021).
5. **Mortality on ART: deaths after 2010 are now in range.** The median run's share of HIV deaths on ART is 0.47 in 2020. In the best runs, deaths from 2010 are 0.4-0.95× UNAIDS. Single years swing by about 0.3 between seeds: 2020 is 0.43 and 2021 is 0.51 in one seed, but the seed mean gives 0.65 and 0.46. Deaths before 2005 stay low (0.47-0.55× in 2000-2005) because the early epidemic is too small. Nobody is yet off ART after stopping (no `dur_reengage`).
6. **Noise decides the MPHIA criterion.** Seeds of one set often split on it. For example, set 81's seeds give women on ART 86.7% and 80.4%, against the cutoff of 82.1%. Seed spread is 0.10 of the parameter spread for ART coverage and suppression, and 0.13 for PLHIV, but MPHIA ± 5 points is about two seed SDs at 10,000 agents. On seed means, fewer sets pass than single runs would suggest (8 for ART coverage, against 29 runs).
7. **The prevalence criterion is weak as read here.** Per run (≥ 90% of points in the runs' 5-95% band), 80% of runs pass. The other reading (data inside the passing runs' 5-95% band) can't be judged with only 2 passing runs: 16 of 84 points are inside. The criterion needs a definition that ties it to the data, e.g. a share of points within the survey intervals, or a prevalence-only score threshold.

## Interpretation for the stopping rule

The stopping rule fails jointly, not on any one criterion. ART coverage needs the right PLHIV in 2010-2015, and PLHIV from 2005 needs the 1990s epidemic, which has been too small since exp 02. More tuning of testing won't fix that. The parameter space where both hold is small: 15 of 600 `open` runs pass ART coverage and PLHIV together, and 2 of those also pass MPHIA.

## STIsim / Starsim friction (not edited)

- `stisim/interventions/hiv_interventions.py:626` (`ART.ready`): `sti.ART` has no eligibility for starting ART (e.g. a CD4 threshold by year, or pregnancy). Exp 04 subclasses `ready()` (`hivsim/malawi.py`, `ARTEligibility`), as analysis 13 did. A `start_eligibility` callable on ART, like `HIVTest`'s `eligibility`, would avoid the subclass.
- Starsim rc3 (`starsim/sim.py:101`): `sim.pars.pop_scale` is gone, and it is now `sim.pop_scale`. `targetfit.py` was updated.
- `hivsim/malawi.py` needed only `ss.MaternalNet` → `ss.PrenatalNet`. The rest of the old `sti.ART`/`HIVTest` interface still works on #613.

## Next (proposed exp 05)

- **The early epidemic, with mortality on ART fixed.** Open `beta_m2f` upward (about 0.006-0.02), and try a time-varying transmission or risk factor before 1995 (or an earlier start, or a larger seed in 1985), so that PLHIV is within × 1.5 from 1995-2000. This is now the main thing standing between runs and the ART coverage criterion.
- **Early ART by sex:** start ANC testing with PMTCT scale-up (Option B+ in 2011, earlier at low coverage) rather than at 90% in 2004. Or let the coverage target split places by sex (`n_art` by sex from the programme data). Men on ART are a check, not a target, so this is for Robyn to decide.
- **Eligibility:** drop the strict CD4 rule, or replace it with CD4 < 200 *or* WHO stage 3/4. HIVsim's `falling` stage could stand in for stage 3/4, i.e. eligible before 2011 if CD4 < 200 or in `falling`.
- **Off ART:** `dur_reengage` (e.g. `ss.expon(ss.years(1-3))`) with `rate_art_dropout`, so that disengagement and re-presentation with advanced HIV can show in deaths (analysis 13 §3-4). This was exp 05 in exp 03's plan, but deaths after 2010 are already in range, so it is lower priority than the early epidemic.
- **Noise and the rule:** score parameter sets on the mean of their seeds, or use 30,000 agents for runs near passing. And define the prevalence criterion against the survey intervals (point 7).
