#!/usr/bin/env python3
"""
spectral_resonance.py — Risonanza Spettrale di Erdős-Riemann
Autore: Mirko Perrone

Modalità:
  zoom      Zoom ad alta risoluzione su un range ristretto (comportamento originale)
  validate  Validazione statistica cieca su range ignoto → precision/recall/F1
  sweep     Sweep multi-range per evidenza su larga scala

Uso:
    python spectral_resonance.py zoom     --start 8080 --end 8100
    python spectral_resonance.py validate --start 1000000 --end 1001000 --zeros zeri_1M.txt
    python spectral_resonance.py sweep    --ranges ranges.txt --zeros zeri_1M.txt
"""

import argparse
import os
import time
import math

import torch
from sympy import isprime

# ── Costanti ───────────────────────────────────────────────────────────────────
DEFAULT_ZEROS_FILE = "zeri_1M.txt"
DEFAULT_SAMPLE_DENSITY = 5_000_00   # 5_000_000 punti per unità intera (modalità zoom)
DEFAULT_VALIDATE_POINTS = 10_00    # 10_000 punti per unità intera (modalità validate)
BLOCK_SIZE = 500                     # zeri per blocco CUDA


# ── Caricamento zeri ───────────────────────────────────────────────────────────
def load_zeros(path: str, max_zeros: int, device: torch.device) -> torch.Tensor:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File zeri non trovato: {path}\n"
            f"Genera gli zeri con: python generate_zeros.py --count 10000"
        )
    with open(path) as f:
        gammas = [float(l.strip()) for l in f if l.strip()]
    gammas = gammas[:max_zeros]
    print(f"[zeri] Caricati {len(gammas):,} zeri da {path}")
    return torch.tensor(gammas, dtype=torch.float64, device=device).unsqueeze(1)


# ── Motore R(n) ────────────────────────────────────────────────────────────────
def compute_resonance(x_vals: torch.Tensor,
                      gamma: torch.Tensor,
                      device: torch.device) -> torch.Tensor:
    """
    R(n) = (1/n·ln n) · (n − 2·Σ [√n · cos(γ·ln n) / |ρ|²])
    con |ρ|² = 1/4 + γ²
    """
    log_x = torch.log(x_vals)                              # (M,)
    sqrt_x = torch.sqrt(x_vals)                            # (M,)
    weight = 1.0 / (0.25 + gamma ** 2)                     # (K, 1)

    risonanza = torch.zeros_like(x_vals)
    n_zeros = gamma.shape[0]

    for i in range(0, n_zeros, BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]                # (B, 1)
        b_weight = weight[i : i + BLOCK_SIZE]              # (B, 1)
        fasi = b_gamma * log_x.unsqueeze(0)                # (B, M)
        contributi = torch.cos(fasi) * b_weight            # (B, M)
        risonanza += sqrt_x * torch.sum(contributi, dim=0) # (M,)

    harmonic = x_vals * log_x
    # Evita log(1) = 0 o x <= 1
    harmonic = torch.clamp(harmonic, min=1e-12)
    R = (x_vals - 2.0 * risonanza) / harmonic
    return R


# ── Classificazione interi ─────────────────────────────────────────────────────
def classify(n: int) -> str:
    if isprime(n):
        return "PRIMO"
    if isprime(n - 1) and isprime(n + 1):
        return "CENTRO GEMELLI"
    if isprime(n - 1):
        return "ADJ← (n-1 primo)"
    if isprime(n + 1):
        return "ADJ→ (n+1 primo)"
    return "COMPOSTO"


# ── MODALITÀ: zoom ─────────────────────────────────────────────────────────────
def mode_zoom(args, device):
    n_start, n_end = args.start, args.end
    n_points = int((n_end - n_start) * DEFAULT_SAMPLE_DENSITY)
    print(f"\n[zoom] Range [{n_start}, {n_end}] | {n_points:,} punti | {args.max_zeros:,} zeri")

    gamma = load_zeros(args.zeros, args.max_zeros, device)
    x_vals = torch.linspace(n_start, n_end, n_points, device=device, dtype=torch.float64)

    t0 = time.time()
    R = compute_resonance(x_vals, gamma, device)
    print(f"[*] Calcolo completato in {time.time()-t0:.1f}s\n")

    # Top picchi distinti per intero
    val_sorted, idx_sorted = torch.sort(R, descending=True)
    trovati: dict[int, float] = {}
    for i in range(len(idx_sorted)):
        px = x_vals[idx_sorted[i]].item()
        n = round(px)
        if n not in trovati and n_start <= n <= n_end:
            trovati[n] = R[idx_sorted[i]].item()
        if len(trovati) >= args.top:
            break

    print("=" * 70)
    print(f"{'RISONANZA (x)':<18} | {'INTERO':<10} | {'R(n)':<12} | STATO")
    print("-" * 70)
    for n, r in sorted(trovati.items(), key=lambda kv: -kv[1]):
        stato = classify(n)
        print(f"{n:<18} | {n:<10} | {r:<12.6f} | {stato}")
    print("=" * 70)


# ── MODALITÀ: validate ─────────────────────────────────────────────────────────
def mode_validate(args, device):
    n_start, n_end = args.start, args.end
    n_points = int((n_end - n_start) * DEFAULT_VALIDATE_POINTS)
    n_points = max(n_points, 10_000)

    print(f"\n[validate] Range [{n_start}, {n_end}] | {n_points:,} punti | {args.max_zeros:,} zeri")
    print("[validate] Validazione CIECA: il range non è stato scelto per i risultati\n")

    gamma = load_zeros(args.zeros, args.max_zeros, device)
    x_vals = torch.linspace(n_start, n_end, n_points, device=device, dtype=torch.float64)

    t0 = time.time()
    R = compute_resonance(x_vals, gamma, device)
    print(f"[*] Calcolo in {time.time()-t0:.1f}s")

    # Ground truth: tutti i primi nel range
    all_integers = list(range(int(math.ceil(n_start)), int(math.floor(n_end)) + 1))
    ground_truth_primes = set(n for n in all_integers if isprime(n))

    # Soglia: top-K picchi dove K = numero di primi attesi
    k = len(ground_truth_primes)
    val_sorted, idx_sorted = torch.sort(R, descending=True)

    predicted: dict[int, float] = {}
    for i in range(len(idx_sorted)):
        px = x_vals[idx_sorted[i]].item()
        n = round(px)
        if n not in predicted and n_start <= n <= n_end:
            predicted[n] = R[idx_sorted[i]].item()
        if len(predicted) >= k:
            break

    predicted_primes = set(predicted.keys())

    # Metriche
    tp = len(predicted_primes & ground_truth_primes)
    fp = len(predicted_primes - ground_truth_primes)
    fn = len(ground_truth_primes - predicted_primes)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)

    print("\n" + "=" * 60)
    print(f"  STATISTICHE DI VALIDAZIONE  (K={k} picchi selezionati)")
    print("=" * 60)
    print(f"  Primi reali nel range  : {len(ground_truth_primes)}")
    print(f"  Picchi predetti        : {len(predicted_primes)}")
    print(f"  True Positives (TP)    : {tp}")
    print(f"  False Positives (FP)   : {fp}")
    print(f"  False Negatives (FN)   : {fn}")
    print(f"  Precision              : {precision:.4f} ({precision*100:.1f}%)")
    print(f"  Recall                 : {recall:.4f} ({recall*100:.1f}%)")
    print(f"  F1 Score               : {f1:.4f}")
    print("=" * 60)

    # Dettaglio errori
    if fp > 0:
        print(f"\n  Falsi positivi (predetti non-primi): {sorted(predicted_primes - ground_truth_primes)[:20]}")
    if fn > 0:
        print(f"  Falsi negativi (primi mancati):      {sorted(ground_truth_primes - predicted_primes)[:20]}")

    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn,
            "range": (n_start, n_end), "zeros": args.max_zeros}


# ── MODALITÀ: sweep ────────────────────────────────────────────────────────────
def mode_sweep(args, device):
    """
    Sweep su range multipli pre-definiti per raccogliere statistiche aggregate.
    Formato ranges.txt: una riga per range, es: '1000000 1001000'
    Se non esiste, usa range di default scelti in modo non cherry-picked.
    """
    default_ranges = [
        (100_000,   101_000),
        (1_000_000, 1_001_000),
        (10_000_000, 10_001_000),
        (100_000_000, 100_001_000),
    ]

    if args.ranges and os.path.exists(args.ranges):
        with open(args.ranges) as f:
            ranges = [tuple(int(x) for x in l.split()) for l in f if l.strip()]
    else:
        print("[sweep] Nessun file ranges.txt trovato, uso range di default.")
        ranges = default_ranges

    gamma = load_zeros(args.zeros, args.max_zeros, device)

    aggregati = []
    for n_start, n_end in ranges:
        print(f"\n[sweep] Range [{n_start:,}, {n_end:,}]")
        n_points = max(int((n_end - n_start) * DEFAULT_VALIDATE_POINTS), 10_000)
        x_vals = torch.linspace(n_start, n_end, n_points, device=device, dtype=torch.float64)

        R = compute_resonance(x_vals, gamma, device)

        all_integers = list(range(n_start, n_end + 1))
        ground_truth = set(n for n in all_integers if isprime(n))
        k = len(ground_truth)

        val_sorted, idx_sorted = torch.sort(R, descending=True)
        predicted: dict[int, float] = {}
        for i in range(len(idx_sorted)):
            px = x_vals[idx_sorted[i]].item()
            n = round(px)
            if n not in predicted and n_start <= n <= n_end:
                predicted[n] = R[idx_sorted[i]].item()
            if len(predicted) >= k:
                break

        tp = len(set(predicted) & ground_truth)
        fp = len(set(predicted) - ground_truth)
        fn = len(ground_truth - set(predicted))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0

        aggregati.append((n_start, n_end, prec, rec, f1, k))
        print(f"  Precision={prec:.3f} Recall={rec:.3f} F1={f1:.3f} (su {k} primi)")

    # Riepilogo aggregato
    print("\n" + "=" * 75)
    print(f"{'RANGE':<30} {'PRIMI':>6} {'PREC':>7} {'RECALL':>7} {'F1':>7}")
    print("-" * 75)
    for n_start, n_end, p, r, f1, k in aggregati:
        label = f"[{n_start:,}, {n_end:,}]"
        print(f"{label:<30} {k:>6} {p:>7.3f} {r:>7.3f} {f1:>7.3f}")

    avg_f1 = sum(x[4] for x in aggregati) / len(aggregati)
    print("-" * 75)
    print(f"{'MEDIA F1 AGGREGATA':<30} {'':>6} {'':>7} {'':>7} {avg_f1:>7.3f}")
    print("=" * 75)


# ── Entrypoint ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Spectral Resonance — Mirko Perrone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # zoom
    p_zoom = sub.add_parser("zoom", help="Alta risoluzione su range ristretto")
    p_zoom.add_argument("--start",     type=float, default=8080)
    p_zoom.add_argument("--end",       type=float, default=8100)
    p_zoom.add_argument("--zeros",     type=str,   default=DEFAULT_ZEROS_FILE)
    p_zoom.add_argument("--max-zeros", type=int,   default=1_000_000)
    p_zoom.add_argument("--top",       type=int,   default=15)

    # validate
    p_val = sub.add_parser("validate", help="Validazione statistica cieca")
    p_val.add_argument("--start",     type=float, default=1_000_000)
    p_val.add_argument("--end",       type=float, default=1_001_000)
    p_val.add_argument("--zeros",     type=str,   default=DEFAULT_ZEROS_FILE)
    p_val.add_argument("--max-zeros", type=int,   default=1_000_000)

    # sweep
    p_sw = sub.add_parser("sweep", help="Sweep su range multipli")
    p_sw.add_argument("--ranges",    type=str,   default="ranges.txt")
    p_sw.add_argument("--zeros",     type=str,   default=DEFAULT_ZEROS_FILE)
    p_sw.add_argument("--max-zeros", type=int,   default=1_000_000)

    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("[warn] CUDA non disponibile, uso CPU (più lento)")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[device] {device}")

    if args.mode == "zoom":
        mode_zoom(args, device)
    elif args.mode == "validate":
        mode_validate(args, device)
    elif args.mode == "sweep":
        mode_sweep(args, device)


if __name__ == "__main__":
    main()
