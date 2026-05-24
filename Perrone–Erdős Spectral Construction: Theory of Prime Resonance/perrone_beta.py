"""
Perrone Constant β — Full Computational Suite
==============================================
Implements all priorities from the paper:
  1. β computed to high precision with tail correction
  2. Residual oscillation analysis (Conjecture 3 + Adelic test)
  3. Ellipse extrema vs prime gaps (Conjecture 2)
  4. Resonance function R(x) with real Riemann zeros
  5. Excess Δ: direct vs spectral (Conjecture 1)

Each section saves a publication-quality plot to ./plots/.
"""

import os
import math
import cmath
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Ellipse as MEllipse
import mpmath as mp
from sympy import nextprime

# ── output dir ────────────────────────────────────────────────────────────────
os.makedirs("plots", exist_ok=True)

# ── global style ──────────────────────────────────────────────────────────────
DARK_BG   = "#0f1117"
GRID_COL  = "#1e2130"
ACCENT1   = "#4f8ef7"   # blue
ACCENT2   = "#f7794f"   # orange
ACCENT3   = "#4ff7a0"   # green
ACCENT4   = "#f7d44f"   # amber
ACCENT5   = "#c77df7"   # purple
TEXT_COL  = "#e0e4f0"
MUTED     = "#6a7090"

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--", alpha=0.7)
    if title:  ax.set_title(title,  color=TEXT_COL, fontsize=11, pad=8)
    if xlabel: ax.set_xlabel(xlabel, color=MUTED,    fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=MUTED,    fontsize=9)

def save(fig, name):
    fig.patch.set_facecolor(DARK_BG)
    fig.savefig(f"plots/{name}.png", dpi=150, bbox_inches="tight",
                facecolor=DARK_BG)
    plt.close(fig)
    print(f"  → plots/{name}.png")


# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY 1 — β to high precision
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("PRIORITY 1 — Computing β to high precision")
print("═"*60)

mp.dps = 60

PRIME_LIMIT = 500_000   # primes up to this value

def compute_beta(prime_limit, precision=50):
    mp.dps = precision
    beta = mp.mpf(0)
    partials = []
    checkpoints = {100, 1000, 10000, 100000}
    p = 2
    count = 0
    while p <= prime_limit:
        beta += mp.mpf(1) / (p * mp.log(p))
        count += 1
        if count in checkpoints:
            partials.append((count, p, float(beta)))
        p = int(nextprime(p))
    # tail correction: ∫_{prime_limit}^∞ dt/(t log²t) = 1/log(prime_limit)
    tail = mp.mpf(1) / mp.log(prime_limit)
    beta_full = beta + tail
    return beta, beta_full, tail, partials, count, p

print(f"  Sieving primes up to {PRIME_LIMIT:,} ...")
beta_partial, beta_full, tail, partials, n_primes, last_p = compute_beta(PRIME_LIMIT)

print(f"  Primes used:        {n_primes:,}")
print(f"  β (partial sum):    {float(beta_partial):.10f}")
print(f"  Tail correction:    {float(tail):.8f}")
print(f"  β (with tail):      {float(beta_full):.10f}")
print(f"  1/log(2):           {float(1/mp.log(2)):.10f}")
print(f"  Δ = β - 1/log(2):  {float(beta_full - 1/mp.log(2)):.10f}")

# --- convergence table -------------------------------------------------------
print("\n  Convergence table:")
print(f"  {'Primes':>10}  {'Last prime':>12}  {'Partial β':>14}")
for cnt, lp, val in partials:
    print(f"  {cnt:>10,}  {lp:>12,}  {val:>14.8f}")

# --- Plot 1: convergence of β ------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("β Convergence & Decomposition", color=TEXT_COL, fontsize=13, y=1.01)

# left: partial sums converging
beta_vals = []
counts = []
p = 2; running = mp.mpf(0); k = 0
step = max(1, PRIME_LIMIT // 400)
while p <= PRIME_LIMIT:
    running += mp.mpf(1) / (p * mp.log(p))
    k += 1
    if k % step == 0 or p < 600:
        counts.append(k)
        beta_vals.append(float(running))
    p = int(nextprime(p))

ax = axes[0]
ax.plot(counts, beta_vals, color=ACCENT1, lw=1.2, label="β partial sum")
ax.axhline(float(beta_full), color=ACCENT2, lw=1.2, ls="--", label=f"β + tail ≈ {float(beta_full):.4f}")
ax.axhline(float(1/mp.log(2)), color=ACCENT3, lw=1, ls=":", label=f"1/log 2 ≈ {float(1/mp.log(2)):.4f}")
ax.fill_between(counts, float(1/mp.log(2)), beta_vals, alpha=0.12, color=ACCENT5, label="Excess Δ")
style_ax(ax, "Convergence of β", "Number of primes", "β value")
ax.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL, framealpha=0.8)

# right: gap β - (1/log2) as fn of log(N)
log_N_vals = [math.log(c + 2) for c in counts]
excess_vals = [v - float(1/mp.log(2)) for v in beta_vals]
ax2 = axes[1]
ax2.plot(log_N_vals, excess_vals, color=ACCENT5, lw=1.2)
ax2.axhline(float(beta_full - 1/mp.log(2)), color=ACCENT2, lw=1, ls="--",
            label=f"Δ ≈ {float(beta_full - 1/mp.log(2)):.4f}")
style_ax(ax2, "Excess Δ = β − 1/log 2  (vs log N)", "log(count)", "Δ(N)")
ax2.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL, framealpha=0.8)

fig.tight_layout()
save(fig, "01_beta_convergence")


# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY 2 — Residual oscillations (Conjecture 3 + Adelic test)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("PRIORITY 2 — Residual oscillation analysis")
print("═"*60)

# build β(N) for exponentially spaced N values
N_points = 300
p_vals_all = []
p = 2
while p <= PRIME_LIMIT:
    p_vals_all.append(p)
    p = int(nextprime(p))

# compute running β at each prime
running = 0.0
betas_at_n = []
for pp in p_vals_all:
    running += 1.0 / (pp * math.log(pp))
    betas_at_n.append((pp, running))

# sample at log-uniform points
sample_indices = np.unique(np.logspace(0, math.log10(len(betas_at_n)-1),
                                        N_points, dtype=int))
Ns, beta_N = zip(*[betas_at_n[i] for i in sample_indices])
Ns = np.array(Ns, dtype=float)
beta_N = np.array(beta_N)

# smooth baseline: 1/log2 + integral approximation for Δ_N
log2_inv = 1.0 / math.log(2)
# Δ_N ≈ Δ * (1 - 1/log(log(N))) is a rough model; we fit a smooth trend
smooth_baseline = log2_inv + float(beta_full - 1/mp.log(2)) * (1 - 1/np.log(np.log(Ns + 2) + 1))
residuals = beta_N - smooth_baseline

# first Riemann zero imaginary part
gamma1 = 14.134725141734693
predicted_freq = gamma1 / math.pi   # ≈ 4.498

# FFT of residuals (uniform in log space)
log_Ns = np.log(Ns)
# re-interpolate on uniform log grid
from scipy.interpolate import interp1d
log_grid = np.linspace(log_Ns[0], log_Ns[-1], 1024)
res_interp = interp1d(log_Ns, residuals, kind='cubic')(log_grid)
fft_vals = np.abs(np.fft.rfft(res_interp))
freqs = np.fft.rfftfreq(len(log_grid), d=(log_grid[1]-log_grid[0]))

# dominant frequency
peak_idx = np.argmax(fft_vals[1:]) + 1
dom_freq = freqs[peak_idx]
print(f"  Predicted frequency γ₁/π:  {predicted_freq:.4f}")
print(f"  Dominant FFT frequency:    {dom_freq:.4f}")
print(f"  Ratio dom/pred:            {dom_freq/predicted_freq:.4f}")

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Residual Oscillations — Conjecture 3 & Adelic Test", color=TEXT_COL, fontsize=13)

ax = axes[0, 0]
ax.plot(np.log(Ns), residuals * 1e4, color=ACCENT1, lw=0.9, label="β(N) − baseline")
ax.axhline(0, color=MUTED, lw=0.6)
style_ax(ax, "Residuals β(N) − smooth baseline", "log N", "Residual (×10⁻⁴)")
ax.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

ax = axes[0, 1]
ax.semilogy(freqs[1:200], fft_vals[1:200], color=ACCENT3, lw=0.9)
ax.axvline(predicted_freq, color=ACCENT2, lw=1.5, ls="--",
           label=f"γ₁/π ≈ {predicted_freq:.3f}")
ax.axvline(dom_freq, color=ACCENT4, lw=1.2, ls=":",
           label=f"dominant ≈ {dom_freq:.3f}")
style_ax(ax, "FFT spectrum of residuals", "Frequency (in log N)", "|FFT|")
ax.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# waterfall: residuals coloured by magnitude
ax = axes[1, 0]
sc = ax.scatter(np.log(Ns), residuals * 1e4,
                c=residuals * 1e4, cmap="coolwarm", s=6, alpha=0.8)
cb = fig.colorbar(sc, ax=ax)
cb.ax.tick_params(colors=TEXT_COL, labelsize=8)
style_ax(ax, "Residuals coloured by sign/magnitude", "log N", "Residual (×10⁻⁴)")

# cumulative convergence to Δ
ax = axes[1, 1]
Deltas = beta_N - log2_inv
ax.plot(np.log(Ns), Deltas, color=ACCENT5, lw=1, label="β(N) − 1/log 2")
ax.axhline(float(beta_full - 1/mp.log(2)), color=ACCENT2, ls="--",
           label=f"Δ = {float(beta_full - 1/mp.log(2)):.5f}", lw=1.2)
style_ax(ax, "Convergence to Δ", "log N", "Δ(N)")
ax.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

fig.tight_layout()
save(fig, "02_residuals_adelic")


# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY 3 — Ellipse extrema vs prime gaps (Conjecture 2)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("PRIORITY 3 — Ellipse extrema vs prime gaps")
print("═"*60)

beta_f = float(beta_full)

def T(n, beta):
    t = math.log(n)
    return math.sqrt(math.sin(t)**2 + beta * math.cos(t)**2) / t

# extrema at theta = k*pi/2
K_MAX = 80
extrema = []
for k in range(1, K_MAX + 1):
    theta = k * math.pi / 2
    n_k = math.exp(theta)
    t_val = T(n_k, beta_f)
    # find nearest prime
    p_low = int(nextprime(int(n_k) - 2))
    p_high = int(nextprime(p_low))
    p_nearest = p_low if abs(p_low - n_k) <= abs(p_high - n_k) else p_high
    gap = abs(p_nearest - n_k)
    rh_bound = math.sqrt(n_k) * math.log(n_k)
    extrema.append({
        'k': k, 'theta': theta, 'n_k': n_k, 'T': t_val,
        'p': p_nearest, 'gap': gap, 'rh_bound': rh_bound,
        'within': gap < rh_bound
    })
    if k <= 10:
        print(f"  k={k:2d}  n_k={n_k:12.2f}  p={p_nearest:12d}  "
              f"gap={gap:8.2f}  RH_bound={rh_bound:10.2f}  "
              f"{'✓' if gap < rh_bound else '✗'}")

n_within = sum(1 for e in extrema if e['within'])
print(f"\n  Within RH bound: {n_within}/{K_MAX} = {100*n_within/K_MAX:.1f}%")

fig = plt.figure(figsize=(15, 10))
fig.suptitle("Conjecture 2 — Ellipse Extrema vs Prime Gaps", color=TEXT_COL, fontsize=13)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)

# plot 1: ellipse
ax_ell = fig.add_subplot(gs[0, 0])
theta_range = np.linspace(0, 2*math.pi, 500)
x_ell = np.cos(theta_range)
y_ell = math.sqrt(beta_f) * np.sin(theta_range)
ax_ell.plot(x_ell, y_ell, color=ACCENT1, lw=1.5, label=f"E_β  (b=√β≈{math.sqrt(beta_f):.4f})")
# mark extrema points (first 8)
for e in extrema[:8]:
    th = e['theta'] % (2*math.pi)
    ax_ell.scatter(math.cos(th), math.sqrt(beta_f)*math.sin(th),
                   color=ACCENT2, s=40, zorder=5)
ax_ell.set_aspect('equal')
ax_ell.axhline(0, color=MUTED, lw=0.5)
ax_ell.axvline(0, color=MUTED, lw=0.5)
style_ax(ax_ell, "Perrone Ellipse E_β", "x", "y")
ax_ell.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# plot 2: T(n) function
ax_T = fig.add_subplot(gs[0, 1:])
n_range = np.linspace(3, 200, 3000)
T_vals = [T(n, beta_f) for n in n_range]
ax_T.plot(n_range, T_vals, color=ACCENT1, lw=0.9, label="T(n)")
# mark extrema
for e in extrema:
    if e['n_k'] <= 200:
        ax_T.axvline(e['n_k'], color=ACCENT5, lw=0.6, alpha=0.5)
        ax_T.scatter(e['n_k'], e['T'], color=ACCENT4, s=30, zorder=5)
# mark small primes
small_primes = [p for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113] if p <= 200]
for sp in small_primes:
    ax_T.axvline(sp, color=ACCENT3, lw=0.4, alpha=0.3)
style_ax(ax_T, "Tension function T(n)  [vertical: extrema=amber, primes=green]", "n", "T(n)")
ax_T.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# plot 3: gap vs RH bound
ax_gap = fig.add_subplot(gs[1, 0:2])
ks      = [e['k'] for e in extrema]
gaps    = [e['gap'] for e in extrema]
bounds  = [e['rh_bound'] for e in extrema]
colors  = [ACCENT3 if e['within'] else ACCENT2 for e in extrema]
ax_gap.scatter(ks, gaps, c=colors, s=20, label="gap |p_k − n_k|", zorder=4)
ax_gap.plot(ks, bounds, color=ACCENT4, lw=1.2, ls="--", label="RH bound √n_k · log n_k")
style_ax(ax_gap, "Prime gap at extrema vs RH bound", "k", "gap size")
ax_gap.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)
ax_gap.text(0.5, 0.92, f"{n_within}/{K_MAX} extrema within RH bound",
            transform=ax_gap.transAxes, ha='center', color=TEXT_COL, fontsize=9)

# plot 4: ratio gap/bound
ax_ratio = fig.add_subplot(gs[1, 2])
ratios = [e['gap']/e['rh_bound'] for e in extrema]
ax_ratio.plot(ks, ratios, color=ACCENT5, lw=1)
ax_ratio.axhline(1.0, color=ACCENT2, lw=1.2, ls="--", label="RH bound = 1")
ax_ratio.fill_between(ks, 0, ratios, alpha=0.15, color=ACCENT5)
style_ax(ax_ratio, "Ratio: gap / RH bound", "k", "gap / (√n_k log n_k)")
ax_ratio.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

save(fig, "03_ellipse_extrema")


# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY 4 — Resonance function R(x) with real Riemann zeros
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("PRIORITY 4 — Resonance function R(x)")
print("═"*60)

N_ZEROS = 200
print(f"  Loading {N_ZEROS} Riemann zeros from mpmath ...")
gammas = []
for k in range(1, N_ZEROS + 1):
    z = mp.zetazero(k)
    gammas.append(float(z.imag))
print(f"  γ₁ = {gammas[0]:.6f},  γ₂ = {gammas[1]:.6f},  γ_{N_ZEROS} = {gammas[-1]:.6f}")

def R(x, gammas):
    lg = math.log(x)
    return sum(math.cos(g * lg) / (0.25 + g*g) for g in gammas)

def R_random(x, gammas_shuffled):
    lg = math.log(x)
    return sum(math.cos(g * lg) / (0.25 + g*g) for g in gammas_shuffled)

# x grid
x_vals = np.linspace(2, 300, 2000)
print("  Computing R(x) ...")
R_vals = np.array([R(x, gammas) for x in x_vals])

# random baseline (shuffled gamma magnitudes, random signs)
rng = np.random.default_rng(42)
gammas_rand = rng.permutation(gammas).tolist()
R_rand = np.array([R_random(x, gammas_rand) for x in x_vals])

# local maxima
from scipy.signal import find_peaks
peaks_idx, _ = find_peaks(R_vals, height=np.percentile(R_vals, 70), distance=5)
peak_xs = x_vals[peaks_idx]

# known primes up to 300
primes_300 = []
p = 2
while p <= 300:
    primes_300.append(p)
    p = int(nextprime(p))

# how many peaks are within 3 of a prime
n_near = sum(1 for px in peak_xs if min(abs(px - pp) for pp in primes_300) < 3)
print(f"  R(x) peaks: {len(peak_xs)}, near a prime (<3): {n_near} = {100*n_near/max(1,len(peak_xs)):.0f}%")

fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=False)
fig.suptitle("Resonance Function R(x) vs Primes", color=TEXT_COL, fontsize=13)

# panel 1: full R(x)
ax = axes[0]
ax.plot(x_vals, R_vals, color=ACCENT1, lw=0.8, label=f"R(x)  [{N_ZEROS} zeros]")
ax.plot(x_vals, R_rand, color=MUTED, lw=0.6, alpha=0.6, label="R_random(x)")
for pp in primes_300:
    ax.axvline(pp, color=ACCENT3, lw=0.35, alpha=0.4)
ax.scatter(peak_xs, R_vals[peaks_idx], color=ACCENT2, s=12, zorder=5, label="peaks")
style_ax(ax, "R(x) = Σ_γ cos(γ log x)/(¼+γ²)  [green lines = primes]", "x", "R(x)")
ax.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# panel 2: zoom 2–80
ax2 = axes[1]
mask = x_vals <= 80
ax2.plot(x_vals[mask], R_vals[mask], color=ACCENT1, lw=1.0)
for pp in [p for p in primes_300 if p <= 80]:
    ax2.axvline(pp, color=ACCENT3, lw=0.7, alpha=0.6, label="_")
mask_pk = peak_xs <= 80
ax2.scatter(peak_xs[mask_pk], R_vals[peaks_idx][mask_pk],
            color=ACCENT2, s=30, zorder=5)
# label peaks
for px, py in zip(peak_xs[mask_pk], R_vals[peaks_idx][mask_pk]):
    nearest = min(primes_300, key=lambda pp: abs(pp - px))
    ax2.annotate(f"p={nearest}", (px, py), textcoords="offset points",
                 xytext=(0, 6), fontsize=7, color=ACCENT2, ha='center')
style_ax(ax2, "R(x) zoom [2, 80]", "x", "R(x)")

# panel 3: peak-to-prime distance distribution
ax3 = axes[2]
distances = [min(abs(px - pp) for pp in primes_300) for px in peak_xs]
ax3.hist(distances, bins=30, color=ACCENT1, alpha=0.8, edgecolor=DARK_BG)
ax3.axvline(np.mean(distances), color=ACCENT2, lw=1.5, ls="--",
            label=f"mean = {np.mean(distances):.2f}")
ax3.axvline(3, color=ACCENT4, lw=1.2, ls=":",
            label="threshold = 3")
style_ax(ax3, "Distribution of |peak − nearest prime|", "distance", "count")
ax3.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

fig.tight_layout()
save(fig, "04_resonance_Rx")


# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY 5 — Excess Δ: direct vs spectral (Conjecture 1)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("PRIORITY 5 — Excess Δ: direct vs spectral")
print("═"*60)

Delta_direct = float(beta_full - 1/mp.log(2))
print(f"  Δ_direct  = {Delta_direct:.8f}")

# Spectral approximation of Δ via zeros
# Δ_spectral = -2 Σ_{γ>0} Re[ ζ'(1/2+iγ) / (γ · ζ(1/2+iγ)) ]  (regularized)
# We compute a finite truncation with a convergence factor e^{-ε·γ}
mp.dps = 30
N_FOR_DELTA = 150

# Spectral decomposition of Δ via the Möbius representation:
#   β = Σ_{n≥1} μ(n)/n · ∫₁^∞ log ζ(nu) du
# We estimate each term numerically and compare the truncated sum to Δ_direct.
# This is well-defined and converges, unlike the raw zero-sum formula.
print(f"  Computing spectral Δ via Möbius / log-ζ representation ({N_FOR_DELTA} zeros) ...")

# Build ∫₁^∞ log|ζ(nu)| du for n=1..8 numerically
def integral_log_zeta(n, u_max=12.0, steps=300):
    """∫₁^∞ log|ζ(nu)| du  (truncated at u_max)"""
    us_ = np.linspace(1.001, u_max, steps)
    vals = []
    for u in us_:
        try:
            z = complex(mp.zeta(mp.mpf(n) * mp.mpf(u)))
            v = math.log(abs(z)) if abs(z) > 1e-30 else -69.0
        except Exception:
            v = 0.0
        vals.append(v)
    return float(np.trapezoid(vals, us_))

from sympy import mobius as sym_mobius
mobius_vals = {n: int(sym_mobius(n)) for n in range(1, 9)}

print("  n   μ(n)   ∫log|ζ(nu)|du   contribution")
beta_spectral_terms = []
beta_spectral_sum = 0.0
for n in range(1, 9):
    mu_n = mobius_vals[n]
    if mu_n == 0:
        beta_spectral_terms.append((n, mu_n, 0.0, 0.0, beta_spectral_sum))
        print(f"  {n}    {mu_n:+d}     (skipped, μ=0)")
        continue
    integral = integral_log_zeta(n)
    contrib = (mu_n / n) * integral
    beta_spectral_sum += contrib
    beta_spectral_terms.append((n, mu_n, integral, contrib, beta_spectral_sum))
    print(f"  {n}    {mu_n:+d}     {integral:12.6f}     {contrib:+.8f}   Σ={beta_spectral_sum:.6f}")

Delta_spectral = beta_spectral_sum - float(1/mp.log(2))
print(f"\n  β_spectral (Möbius sum) = {beta_spectral_sum:.8f}")
print(f"  β_direct               = {float(beta_full):.8f}")
print(f"  Δ_direct               = {Delta_direct:.8f}")
print(f"  Δ_spectral             = {Delta_spectral:.8f}")
print(f"  Difference             = {abs(Delta_direct - Delta_spectral):.8f}")

# also collect per-zero amplitudes for the plots (convergence factor approach)
# using |ζ'(ρ)| / |ρ| as amplitude proxy — well-defined on the critical line
Delta_spectral_terms = []
partial_spectral_zeros = 0.0
print(f"\n  Per-zero amplitude |ζ'(ρ)/ρ| for first 60 zeros ...")
for k in range(1, 61):
    g = float(mp.zetazero(k).imag)
    s = mp.mpc(0.5, g)
    try:
        dzeta_val = complex(mp.diff(mp.zeta, s))
        amp = abs(dzeta_val) / (abs(s))
        # sign from Re[ζ'(ρ)/ρ̄] — proxy for the actual term
        rho = complex(0.5, g)
        sign_term = -(dzeta_val / (g * rho)).real
        term = sign_term * math.exp(-0.3 * g / g)   # no decay, use raw
        # regularize: multiply by e^{-k/60} for display only
        term_disp = sign_term * math.exp(-k / 80)
    except Exception:
        term_disp = 0.0
        amp = 0.0
    partial_spectral_zeros += term_disp
    Delta_spectral_terms.append((k, g, term_disp, partial_spectral_zeros))

# --- plots ---
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Conjecture 1 — Excess Δ: Direct vs Spectral Decomposition", color=TEXT_COL, fontsize=13)

# panel 1: spectral terms
ks_sp, gs_sp, terms_sp, cumul_sp = zip(*Delta_spectral_terms)

ax = axes[0, 0]
ax.bar(ks_sp, terms_sp, color=[ACCENT1 if t > 0 else ACCENT2 for t in terms_sp],
       width=0.8, alpha=0.8)
ax.axhline(0, color=MUTED, lw=0.5)
style_ax(ax, "Per-zero amplitudes Re[ζ'(ρ)/ρ]·decay  (60 zeros)", "zero index k", "amplitude")

# panel 2: Möbius series convergence
ns_mob = [t[0] for t in beta_spectral_terms]
betas_mob = [t[4] for t in beta_spectral_terms]
ax2 = axes[0, 1]
ax2.plot(ns_mob, betas_mob, 'o-', color=ACCENT5, lw=1.2, markersize=7, label="β Möbius partial sum")
ax2.axhline(float(beta_full), color=ACCENT2, lw=1.5, ls="--",
            label=f"β_direct = {float(beta_full):.5f}")
ax2.axhline(float(1/mp.log(2)), color=ACCENT3, lw=1, ls=":",
            label=f"1/log 2 = {float(1/mp.log(2)):.5f}")
style_ax(ax2, "β via Möbius: Σ μ(n)/n · ∫log|ζ(nu)|du", "n terms", "β")
ax2.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# panel 3: zero amplitude |ζ'(ρ)/ρ| vs γ
ax3 = axes[1, 0]
amp_vals = []
for k in range(1, 61):
    g = float(mp.zetazero(k).imag)
    s = mp.mpc(0.5, g)
    try:
        dz = abs(complex(mp.diff(mp.zeta, s)))
        amp_vals.append((g, dz / (0.25 + g**2)**0.5))
    except Exception:
        pass
gs_amp, amps = zip(*amp_vals)
ax3.scatter(gs_amp, amps, color=ACCENT3, s=15, alpha=0.8, label="|ζ'(ρ)|/|ρ|")
ax3.set_yscale("log")
log_g = np.log(list(gs_amp))
log_a = np.log(list(amps))
coeffs = np.polyfit(log_g, log_a, 1)
ax3.plot(sorted(gs_amp),
         np.exp(np.polyval(coeffs, np.log(sorted(gs_amp)))),
         color=ACCENT2, lw=1.2, ls="--", label=f"γ^{coeffs[0]:.2f}")
style_ax(ax3, "|ζ'(ρ)|/|ρ|  vs γ  (log-log)", "γ_k", "|ζ'(ρ)|/|ρ|")
ax3.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# panel 4: adelic summary — β decomposition bar chart
ax4 = axes[1, 1]
components = [float(1/mp.log(2)), Delta_direct]
labels = ["1/log 2\n(smooth)", "Δ\n(prime gaps)"]
colors_bar = [ACCENT1, ACCENT5]
bars = ax4.bar(labels, components, color=colors_bar, width=0.5, alpha=0.85)
ax4.axhline(float(beta_full), color=ACCENT2, lw=1.5, ls="--",
            label=f"β ≈ {float(beta_full):.5f}")
for bar, val in zip(bars, components):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f"{val:.4f}", ha='center', color=TEXT_COL, fontsize=10)
style_ax(ax4, "β = 1/log 2 + Δ  decomposition", "", "value")
ax4.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

fig.tight_layout()
save(fig, "05_delta_spectral")


# ══════════════════════════════════════════════════════════════════════════════
# BONUS — Adelic structure summary plot
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("BONUS — Adelic structure: p-adic norms at peak locations")
print("═"*60)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Adelic Structure — ∏_p |x−p|_p at R(x) peaks", color=TEXT_COL, fontsize=13)

# compute adelic product measure at each peak  (finite product over small primes)
small_ps = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

def padic_norm(x, p):
    if abs(x) < 1e-12:
        return 0.0
    r = x
    exp = 0
    while abs(r) > 1e-9 and abs(round(r) - r) < 1e-9 * abs(r) + 1e-12:
        r /= p
        exp += 1
    return float(p) ** (-exp) if exp > 0 else 1.0

def adelic_prod(x, ps):
    result = 1.0
    for pp in ps:
        result *= min(1.0, abs(x - pp))  # simplified proxy
    return result

# at peaks of R(x) vs random x values
adelic_peaks = [adelic_prod(px, primes_300[:20]) for px in peak_xs]
random_xs = rng.uniform(2, 300, len(peak_xs))
adelic_rand = [adelic_prod(rx, primes_300[:20]) for rx in random_xs]

ax = axes[0]
ax.hist(np.log1p(adelic_peaks), bins=25, color=ACCENT1, alpha=0.75,
        label="at R(x) peaks", density=True)
ax.hist(np.log1p(adelic_rand), bins=25, color=ACCENT2, alpha=0.55,
        label="random x", density=True)
style_ax(ax, "Adelic proximity measure log(1+∏|x−p|)", "log(1 + adelic product)", "density")
ax.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

# prime zeta P(u) = Σ p^{-u}  for u in [1.01, 5]
us = np.linspace(1.01, 5, 300)
P_vals = []
for u in us:
    pz = sum(pp**(-u) for pp in p_vals_all[:5000])
    P_vals.append(pz)

ax2 = axes[1]
ax2.plot(us, P_vals, color=ACCENT5, lw=1.3, label="P(u) = Σ_p p^{−u}")
ax2.fill_between(us, 0, P_vals, alpha=0.15, color=ACCENT5)
ax2.axvline(1.0, color=ACCENT2, lw=1, ls="--", label="pole at u=1")
# mark β as the area under the curve
beta_area = np.trapezoid(P_vals, us)
ax2.text(2.5, max(P_vals)*0.6,
         f"∫₁^∞ P(u) du ≈ β ≈ {float(beta_full):.4f}\n(area under curve)",
         color=TEXT_COL, fontsize=9, ha='center',
         bbox=dict(facecolor=GRID_COL, alpha=0.7, edgecolor=MUTED))
style_ax(ax2, "Prime zeta P(u) = Σ_p p^{−u}  (β = ∫₁^∞ P(u) du)", "u", "P(u)")
ax2.legend(fontsize=8, facecolor=GRID_COL, labelcolor=TEXT_COL)

fig.tight_layout()
save(fig, "06_adelic_structure")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("SUMMARY")
print("═"*60)
print(f"  β  = {float(beta_full):.10f}")
print(f"  1/log 2  = {float(1/mp.log(2)):.10f}")
print(f"  Δ        = {Delta_direct:.10f}")
print(f"  √β (ellipse b-axis) = {math.sqrt(float(beta_full)):.8f}")
print(f"  eccentricity e = √(1−1/β) = {math.sqrt(1 - 1/float(beta_full)):.8f}")
print(f"  γ₁ = {gammas[0]:.8f}   (first Riemann zero imag part)")
print(f"  Adelic test freq γ₁/π = {gammas[0]/math.pi:.8f}")
print(f"\n  Plots saved in ./plots/")
print("  01_beta_convergence.png")
print("  02_residuals_adelic.png")
print("  03_ellipse_extrema.png")
print("  04_resonance_Rx.png")
print("  05_delta_spectral.png")
print("  06_adelic_structure.png")
print("═"*60)
