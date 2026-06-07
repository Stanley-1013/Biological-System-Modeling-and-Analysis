"""Part 2, Question (d): VACCINATION vs SAFE-SEX EDUCATION + CONDOMS.

Built on the VERIFIED sIC core in ``sic.py`` (NOT modified). Compares two control
strategies against the no-intervention baseline over a multi-decade horizon, with
all conclusions framed in terms of the reproduction number / threshold behavior.

Strategies
  * BASELINE      : no intervention (nu = 0).
  * VACCINATION   : nu = 0.65/yr, l = 0.1/yr (take-with-waning Protected
                    compartment). Reported for the CORRECTED DEFAULT model
                    (count_p_in_denominator = True: P, being uninfected and
                    sexually active, is a legitimate partner and stays in the
                    frequency-dependent pool, so vaccinees dilute it). The WRONG
                    P-excluded convention is shown only as a documented caveat.
  * CONDOMS       : halve the transmission probabilities
                    (beta_fm 0.075 -> 0.0375, beta_mf 0.2 -> 0.1), which
                    multiplies R0 by 0.5 because R0 ∝ sqrt(beta_mf * beta_fm).

Outputs compared: prevalence trajectories, peak prevalence, infections averted,
time-to-decline, R0 / R_eff per strategy, and (vaccination only) program cost.

================================================================================
MODELING ASSUMPTION (stated in the results file)
================================================================================
gamma = 0.1/yr (mean ~10 yr HIV->AIDS; within the textbook's 1-10 yr range),
giving R0 = c*sqrt(beta_mf*beta_fm)/(mu+gamma) ~= 2.35. The literal Table-15.2
gamma = 1.16/yr gives R0 < 1 (no epidemic) -- the verified core's documented
finding. Epidemic seeded with infectious males I_m2 = 5.

All units: time YEARS, state INDIVIDUALS, cost USD ($10/vaccination).

Run:  python3 q_d_vax_vs_condoms.py
Writes figures to figures/ and a report to results/qd_results.md.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass

import numpy as np

import sic

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")
RES_DIR = os.path.join(HERE, "results")

GAMMA_CALIBRATED = 0.1
L_WANING = 0.1
NU_STD = 0.65
SEED_I_M2 = 5.0

HORIZON_YEARS = 80.0
N_EVAL = 4000

# Condom scenario: halve betas
BETA_FM_CONDOM = 0.0375
BETA_MF_CONDOM = 0.1

# Invasion-test settings (operational R_eff sign)
INV_DF_YEARS = 80.0
INV_DF_N = 200
INV_SEED = 1.0
INV_YEARS = 15.0
INV_N = 400
INV_FIT_LO, INV_FIT_HI = 0.5, 5.0


# ---------------------------------------------------------------------------
def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 140,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "font.size": 10,
        }
    )
    return plt


def R0_of(p: sic.Params) -> float:
    dur = 1.0 / (p.mu + p.gamma)
    return p.c * math.sqrt(p.beta_mf * p.beta_fm) * dur


def invasion_growth_rate(p: sic.Params, count_p: bool) -> float:
    """Early exponential growth rate of total infection seeded into the
    intervention's disease-free state (sign = sign of R_eff - 1)."""
    pp = p.with_(count_p_in_denominator=count_p)
    res_df = sic.simulate(sic.initial_conditions(0.0, 0.0), INV_DF_YEARS, pp,
                          n_eval=INV_DF_N)
    yss = res_df.y[:, -1].copy()
    yss[sic.IDX["I_m2"]] += INV_SEED
    res = sic.simulate(yss, INV_YEARS, pp, n_eval=INV_N)
    wv = sic.total_with_virus(res.y)
    t = res.t
    m = (t >= INV_FIT_LO) & (t <= INV_FIT_HI) & (wv > 0)
    return float(np.polyfit(t[m], np.log(wv[m]), 1)[0])


def cumulative_infections(res: sic.SimResult) -> float:
    return float(np.trapezoid(sic.incidence(res.y, res.params), res.t))


def time_to_peak_then_decline(t, prev):
    """Time of the prevalence peak (first local max), or nan if monotone."""
    if len(prev) < 3:
        return float("nan")
    k = int(np.argmax(prev))
    if k == 0 or k == len(prev) - 1:
        return float("nan")
    return float(t[k])


@dataclass(frozen=True)
class Scenario:
    name: str
    params: sic.Params
    res: sic.SimResult
    aux: dict
    R0: float
    reff_note: str
    cum_inf: float
    infections_averted: float
    peak_prev: float
    end_prev: float
    peak_time: float
    cost_usd: float


# ---------------------------------------------------------------------------
def run_all() -> dict:
    base = sic.Params().with_(gamma=GAMMA_CALIBRATED)
    y0 = sic.initial_conditions(seed_A_m2=0.0, seed_I_m2=SEED_I_M2)

    specs = {
        "baseline": base.with_(nu=0.0),
        "vaccination": base.with_(nu=NU_STD, l=L_WANING),
        "condom": base.with_(beta_fm=BETA_FM_CONDOM, beta_mf=BETA_MF_CONDOM),
    }

    res = {k: sic.simulate(y0, HORIZON_YEARS, p, n_eval=N_EVAL)
           for k, p in specs.items()}
    aux = {k: sic.auxiliaries(res[k]) for k in res}
    baseline_inf = cumulative_infections(res["baseline"])

    # R_eff narratives
    vac = specs["vaccination"]
    reff_vac_pool = R0_of(base) * (1.0 - sic.waning_protection_ceiling(vac))
    inv_vac_default = invasion_growth_rate(vac, count_p=False)
    inv_vac_pool = invasion_growth_rate(vac, count_p=True)
    inv_condom = invasion_growth_rate(specs["condom"], count_p=False)
    inv_base = invasion_growth_rate(specs["baseline"], count_p=False)

    reff_notes = {
        "baseline": f"R0={R0_of(base):.3f}; invasion r={inv_base:+.3f}/yr (>0)",
        "vaccination": (
            f"R_eff={reff_vac_pool:.3f} (corrected default, P in pool); "
            f"invasion r={inv_vac_pool:+.3f}/yr (corrected) vs "
            f"{inv_vac_default:+.3f}/yr (WRONG convention, P excluded)"),
        "condom": (
            f"R0_condom={R0_of(specs['condom']):.3f} (=0.5*R0); "
            f"invasion r={inv_condom:+.3f}/yr"),
    }

    scen = {}
    for k in specs:
        ci = cumulative_infections(res[k])
        scen[k] = Scenario(
            name=k, params=specs[k], res=res[k], aux=aux[k],
            R0=R0_of(specs[k]),
            reff_note=reff_notes[k],
            cum_inf=ci,
            infections_averted=baseline_inf - ci,
            peak_prev=float(np.max(aux[k]["prev_overall"])),
            end_prev=float(aux[k]["prev_overall"][-1]),
            peak_time=time_to_peak_then_decline(res[k].t, aux[k]["prev_overall"]),
            cost_usd=float(sic.total_cost(res[k].y)[-1]),
        )
    return {
        "scen": scen, "baseline_inf": baseline_inf,
        "reff_vac_pool": reff_vac_pool,
        "inv": {"base": inv_base, "vac_default": inv_vac_default,
                "vac_pool": inv_vac_pool, "condom": inv_condom},
    }


# ---------------------------------------------------------------------------
def fig_trajectories(plt, scen, reff_vac, path) -> None:
    colors = {"baseline": "#555", "vaccination": "#2471a3", "condom": "#27ae60"}
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for k in ("baseline", "vaccination", "condom"):
        s = scen[k]
        lbl = (f"baseline, R0={s.R0:.2f}" if k == "baseline" else
               (f"vaccination nu=0.65 (R_eff={reff_vac:.2f})" if k == "vaccination"
                else f"condoms (R0={s.R0:.2f})"))
        ax.plot(s.aux["t"], s.aux["prev_overall"], color=colors[k], lw=2.2,
                label=lbl)
    ax.set_xlabel("time (years)")
    ax.set_ylabel("overall prevalence  (I+A)/living")
    ax.set_title("(d) Prevalence trajectories: baseline vs vaccination vs condoms")
    ax.set_xlim(0, HORIZON_YEARS)
    ax.set_ylim(0, max(scen["baseline"].peak_prev * 1.05, 0.05))
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def fig_summary_bars(plt, scen, reff_vac, path) -> None:
    order = ["baseline", "vaccination", "condom"]
    names = ["baseline", "vaccination\n(nu=0.65)", "condoms\n(0.5*betas)"]
    averted = [scen[k].infections_averted for k in order]
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(10.5, 4.6))

    bars = axA.bar(names, averted, color=["#999", "#2471a3", "#27ae60"])
    axA.set_ylabel("infections averted over 80 yr")
    axA.set_title("(d) Infections averted vs baseline")
    for b, v in zip(bars, averted):
        axA.text(b.get_x() + b.get_width() / 2, b.get_height(),
                 f"{v:,.0f}", ha="center", va="bottom", fontsize=9)

    # R0 / R_eff bar
    reff_vals = [scen["baseline"].R0, reff_vac, scen["condom"].R0]
    bars2 = axB.bar(names, reff_vals, color=["#999", "#2471a3", "#27ae60"])
    axB.axhline(1.0, color="#c0392b", lw=1.4, ls="--", label="R = 1 (threshold)")
    axB.set_ylabel("R0 / R_eff")
    axB.set_title("(d) Reproduction number per strategy")
    for b, v in zip(bars2, reff_vals):
        axB.text(b.get_x() + b.get_width() / 2, b.get_height(),
                 f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    axB.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------------------
def write_report(data, figs) -> None:
    scen = data["scen"]
    inv = data["inv"]
    b, v, c = scen["baseline"], scen["vaccination"], scen["condom"]
    fnames = [os.path.basename(f) for f in figs]

    def pk(s):
        return "monotone (no interior peak)" if math.isnan(s.peak_time) \
            else f"{s.peak_time:.0f} yr"

    md = f"""# Part 2 (d) — Vaccination vs Safe-Sex Education + Condoms

## Question
Which intervention more effectively controls the HIV epidemic on the sIC model:
**vaccination** (nu = 0.65/yr, l = 0.1/yr) or **safe-sex education + condoms**
(modeled as halving the transmission probabilities)? Compare over a multi-decade
horizon on prevalence trajectories, infections averted, time-to-decline,
reproduction number, and cost.

## Modeling assumption and R0 (stated explicitly)
- **gamma = {GAMMA_CALIBRATED}/yr** (mean ~10 yr HIV->AIDS; within the textbook's
  1-10 yr range). Literal `gamma = 1.16/yr` gives R0 < 1 (no epidemic) — the
  verified core's documented finding.
- **Baseline R0 = c·sqrt(beta_mf·beta_fm)/(mu+gamma) = {b.R0:.3f}.** Epidemic
  seeded with infectious males `I_m2 = {SEED_I_M2:g}`. Horizon = {HORIZON_YEARS:.0f} yr.
- **Partner-pool convention (corrected default).** The force of infection is
  frequency-dependent, `lambda ~ I/(S+I+P)`. Vaccine-Protected individuals are
  sexually active and uninfected, hence legitimate partners, so they belong in
  the denominator (`count_p_in_denominator = True`). This is the CORRECT
  convention: moving susceptibles into P dilutes the infectious frequency and
  produces genuine herd immunity. (At nu = 0, P = 0, so baseline and condoms are
  unaffected.) The WRONG convention (P excluded) is reported only as a caveat.

## Strategy definitions and reproduction numbers
- **Condoms** halve both transmission probabilities
  (beta_fm 0.075→{BETA_FM_CONDOM}, beta_mf 0.2→{BETA_MF_CONDOM}). Because
  `R0 ∝ sqrt(beta_mf·beta_fm)`, this multiplies R0 by exactly 0.5:
  **R0_condom = {c.R0:.3f}** — just above the threshold R = 1 (invasion growth
  rate {inv['condom']:+.3f}/yr, still slightly positive).
- **Vaccination** (nu = 0.65, l = 0.1, take-with-waning). The equilibrium
  protected fraction is `nu/(nu+l) = 0.867` (ceiling). Under the corrected
  default vaccinees dilute the partner pool, so
  **`R_eff = R0·(1−0.867) = {data['reff_vac_pool']:.3f} < 1`** (below threshold;
  invasion growth rate {inv['vac_pool']:+.3f}/yr — the epidemic decays). nu = 0.65
  is above the herd-immunity threshold nu_c ≈ 0.37/yr found in (c).

| strategy | R0 / R_eff | invasion growth rate r (/yr) | below threshold? |
|---|---|---|---|
| baseline | R0 = {b.R0:.3f} | {inv['base']:+.3f} | no |
| vaccination (nu=0.65, corrected default) | R_eff = {data['reff_vac_pool']:.3f} | {inv['vac_pool']:+.3f} | **yes** |
| condoms (0.5·beta) | R0 = {c.R0:.3f} | {inv['condom']:+.3f} | borderline (just > 1) |
| vaccination (WRONG: P excluded) — caveat | ≈ {b.R0:.3f} | {inv['vac_default']:+.3f} | no (artifact) |

## Trajectory outcomes ({HORIZON_YEARS:.0f}-yr horizon)

| metric | baseline | vaccination (nu=0.65) | condoms (0.5·beta) |
|---|---|---|---|
| peak overall prevalence | {b.peak_prev:.3f} | {v.peak_prev:.3f} | {c.peak_prev:.3f} |
| end-of-horizon prevalence | {b.end_prev:.3f} | {v.end_prev:.3f} | {c.end_prev:.3f} |
| time of prevalence peak | {pk(b)} | {pk(v)} | {pk(c)} |
| cumulative infections (80 yr) | {b.cum_inf:,.0f} | {v.cum_inf:,.0f} | {c.cum_inf:,.0f} |
| infections averted vs baseline | — | {v.infections_averted:,.0f} | {c.infections_averted:,.0f} |
| program cost (USD) | $0 | ${v.cost_usd:,.0f} | $0 (unpriced) |

## Verdict (this model, these assumptions): **BOTH interventions control the epidemic**

Under the corrected frequency-dependent convention, both strategies essentially
control the epidemic, and they do so by **different mechanisms** — so the honest
verdict is a balanced comparison, not a single winner.

- **R_eff (threshold).** Vaccination at nu = 0.65 drives **R_eff = {data['reff_vac_pool']:.3f} < 1**
  (invasion r = {inv['vac_pool']:+.3f}/yr): it genuinely crosses the elimination
  threshold because it removes the protected fraction nu/(nu+l) ≈ 0.867 > p_c =
  {(1.0 - 1.0/b.R0):.3f} from the susceptible mixing pool.
  Condoms put R0 at **{c.R0:.3f}**, still **marginally above 1** (invasion r =
  {inv['condom']:+.3f}/yr) — a 50% beta cut is not quite enough to cross the
  threshold at this R0, though the epidemic is so slow it is effectively
  controlled within the horizon.
- **Infections averted (80 yr).** Vaccination averts **{v.infections_averted:,.0f}**
  and condoms **{c.infections_averted:,.0f}** of the baseline {b.cum_inf:,.0f} —
  nearly identical; vaccination edges ahead because it pushes R_eff strictly below
  1 while condoms hover just above it (leaving a small residual {c.cum_inf:,.0f}
  cumulative infections vs {v.cum_inf:,.0f} for vaccination).
- **Time-to-decline.** Both collapse the epidemic early: peak prevalence falls
  from the baseline {b.peak_prev:.3f} to ~{v.peak_prev:.3f} (vaccination) and
  ~{c.peak_prev:.3f} (condoms), with no large interior peak — the seeded epidemic
  never takes off under either intervention.
- **Cost basis.** This is where they differ sharply. **Vaccination carries an
  explicit ${v.cost_usd:,.0f}** over 80 yr (the $10/vax accumulator), and is
  capped by the waning ceiling nu/(nu+l) = 0.867 (it must re-vaccinate waned
  individuals indefinitely). **Condoms are modeled as a permanent 0.5× cut to
  R0 at no priced cost** — but that cost is *unpriced*, not zero; a real behavior-
  change program has its own (here unmodeled) budget.

**Net read.** At equal-mechanism strength (a 50% beta cut vs the standard
nu = 0.65), the two are **close to a tie on epidemiological outcome** —
vaccination is marginally better because it strictly crosses R_eff < 1, condoms
sit just above threshold — while their cost structures are not comparable as
priced here (explicit vaccine $ + waning ceiling vs unpriced behavioral program).
We deliberately avoid declaring a single winner.

## Fairness caveats (this is a MODEL-BASED comparison, not a policy claim)
1. **Unpriced condom cost.** Condoms carry a real behavioral-program cost this
   model does not price, while vaccination has an explicit ${v.cost_usd:,.0f}. A
   dollar-matched comparison would need a condom-program cost the project does not
   supply; the comparison is at "equal-mechanism strength," not equal cost.
2. **Near-threshold sensitivity.** Condoms leave R0 at {c.R0:.3f}, only ~{100*(c.R0-1):.0f}% above
   1, and vaccination's R_eff = {data['reff_vac_pool']:.3f} also depends on R0
   through p_c. A higher baseline R0 (e.g. higher partner rate c) would push
   condom-R0 clearly above 1 and would raise the vaccination nu_c — both verdicts
   are R0-sensitive near threshold, which is why we report R_eff explicitly.
3. **Vaccine waning + saturation.** Vaccination protects at most nu/(nu+l) = 0.867
   and re-vaccinates waned individuals (ongoing cost), whereas a sustained
   behavioral change lowers R0 for everyone permanently.
4. **Pool convention.** The corrected default (P in the partner pool) is what
   makes vaccination cross R_eff < 1. The WRONG convention (P excluded) would
   leave vaccination unable to cross the threshold at any rate — an artifact of
   dropping uninfected, sexually-active vaccinees from the frequency-dependent
   mixing pool, not a real property of the disease (see (c)).

## Figures
- `{fnames[0]}` — overall prevalence(t) for baseline / vaccination / condoms.
- `{fnames[1]}` — infections averted and reproduction number per strategy.

## Bottom line
Under gamma = 0.1/yr (R0 = {b.R0:.2f}) and the corrected frequency-dependent
convention, **both vaccination (nu = 0.65) and condoms (50% beta cut) control the
epidemic**. Vaccination drives **R_eff = {data['reff_vac_pool']:.2f} < 1** and
averts **{v.infections_averted:,.0f}** infections (residual {v.cum_inf:,.0f});
condoms hold R0 at **{c.R0:.2f}** (just above 1) and avert **{c.infections_averted:,.0f}**
(residual {c.cum_inf:,.0f}) — essentially a tie on epidemiological outcome, with
vaccination marginally ahead for crossing the threshold strictly. They differ on
cost basis: vaccination ${v.cost_usd:,.0f} explicit + a waning ceiling vs condoms'
unpriced behavioral program. The verdict is balanced and **R0-sensitive near
threshold**; we report explicit R_eff and fairness caveats rather than overclaim a
single winner.
"""
    with open(os.path.join(RES_DIR, "qd_results.md"), "w") as fh:
        fh.write(md)


# ---------------------------------------------------------------------------
def main() -> int:
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(RES_DIR, exist_ok=True)
    plt = _plt()

    print("=" * 78)
    print("PART 2 (d): VACCINATION vs CONDOMS")
    print("=" * 78)
    data = run_all()
    scen = data["scen"]
    for k in ("baseline", "vaccination", "condom"):
        s = scen[k]
        print(f"\n{k}:")
        print(f"  R0={s.R0:.3f}  {s.reff_note}")
        print(f"  peak_prev={s.peak_prev:.3f}  end_prev={s.end_prev:.3f}  "
              f"cum_inf={s.cum_inf:,.0f}  averted={s.infections_averted:,.0f}  "
              f"cost=${s.cost_usd:,.0f}")

    reff_vac = data["reff_vac_pool"]
    f_traj = os.path.join(FIG_DIR, "qd_strategy_comparison.png")
    f_bars = os.path.join(FIG_DIR, "qd_averted_and_reff.png")
    fig_trajectories(plt, scen, reff_vac, f_traj)
    fig_summary_bars(plt, scen, reff_vac, f_bars)
    print(f"\nsaved {f_traj}")
    print(f"saved {f_bars}")

    write_report(data, [f_traj, f_bars])
    print(f"saved {os.path.join(RES_DIR, 'qd_results.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
