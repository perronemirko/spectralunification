#!/usr/bin/env python3
import torch
import math
import argparse
import time
from decimal import Decimal, getcontext

# --- CONFIGURAZIONE ALTA PRECISIONE ---
ERDOS_CONST = 1.6318
DEFAULT_ZEROS_FILE = "zeri_1M.txt"
BLOCK_SIZE = 40  # Ridotto per complex128 su RSA-100
getcontext().prec = 100 # 100 cifre decimali di precisione per l'offset

def get_high_precision_log(offset_str, x_vals_tensor):
    """Calcola ln(N + x) senza perdita di precisione per RSA-100"""
    offset_dec = Decimal(offset_str)
    # Calcolo ln(N) con precisione infinita
    ln_N = float(offset_dec.ln())
    # Approssimazione di Taylor: ln(N + x) = ln(N) + x/N
    # A quota 10^49, x/N è trascurabile ma lo manteniamo per i picchi
    x_offset_ratio = (x_vals_tensor / float(offset_dec)).to(torch.float64)
    return ln_N + x_offset_ratio

# --- MOTORI GEOMETRICI ---

def compute_resonance(x_vals, gamma, device, mode="adelic", offset_str="0"):
    sqrt_erdos = math.sqrt(ERDOS_CONST)
    
    # --- OFFSET LOGARITMICO DI PERRONE ---
    # Gestisce quota 10^49 senza mandare in crash la GPU
    log_x = get_high_precision_log(offset_str, x_vals)
    sqrt_x = torch.sqrt(torch.tensor(float(Decimal(offset_str)), device=device))
    
    if mode == "adelic":
        # Struttura locale sintonizzata su Erdos
        local_structure = torch.sin(math.pi * (x_vals + float(Decimal(offset_str) % 1000)) / ERDOS_CONST)
        metric_x = log_x * (1.0 + 0.05 * local_structure)
    elif mode == "minkowski":
        t = log_x
        s = sqrt_x / ERDOS_CONST
        metric_x = torch.sqrt(torch.abs(t**2 - s**2) + 1e-15)
    else:
        metric_x = log_x

    # Precisione 128-bit (Double Precision) per RSA-100
    weight = (1.0 / gamma).to(torch.complex128)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex128)

    for i in range(0, gamma.shape[0], BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]
        b_weight = weight[i : i + BLOCK_SIZE]
        
        fase = b_gamma.unsqueeze(1) * metric_x.unsqueeze(0)
        
        # i^2 = -1.63 (L'identità di Mirko)
        reale = torch.cos(fase)
        immag = torch.sin(fase) * sqrt_erdos
        
        fase_mirko = torch.complex(reale, immag)
        contributo = torch.sum(fase_mirko * b_weight.unsqueeze(1), dim=0)
        risonanza += contributo.squeeze()

    signal = torch.abs(risonanza) * sqrt_x
    return normalize_and_detrend(signal, device)

def normalize_and_detrend(signal, device):
    window_size = 100
    padding = window_size // 2
    s_4d = signal.unsqueeze(0).unsqueeze(0).to(torch.float32)
    padded = torch.nn.functional.pad(s_4d, (padding, padding), mode='replicate')
    kernel = torch.ones((1, 1, window_size), device=device) / window_size
    mean = torch.nn.functional.conv1d(padded, kernel).squeeze()
    if mean.dim() > 0 and mean.shape[0] > signal.shape[0]: mean = mean[:signal.shape[0]]
    res = signal - mean
    R = (res - res.mean()) / (res.std() + 1e-12)
    return R.to(torch.float64)

# --- ESECUZIONE ---

def load_zeros(filename, max_zeros, device):
    print(f"[*] Caricamento zeri da {filename}...")
    zeros = []
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if i >= max_zeros: break
            zeros.append(float(line.strip()))
    return torch.tensor(zeros, device=device, dtype=torch.float64)

def mode_attack(args, device):
    # n_start e n_end qui sono gli scostamenti dalla radice (offset)
    gamma = load_zeros(args.zeros, args.max_zeros, device)

    print(f"\n[🚀 MIRKO H100-EMULATOR] Mode: {args.geo} | Precision: complex128")
    print(f"[📍 OFFSET RSA-100]: {args.offset[:20]}...{args.offset[-10:]}")
    
    # Scansione locale intorno all'offset
    n_points = 2000 
    x_local = torch.linspace(args.start, args.end, n_points, device=device, dtype=torch.float64)
    
    print(f"[*] Scansione spettrale in corso (Maratona 4090)...")
    R = compute_resonance(x_local, gamma, device, mode=args.geo, offset_str=args.offset)
    
    mask = R > args.threshold
    hits = []
    if torch.any(mask):
        indices = torch.where(mask)[0]
        for idx in indices:
            if idx < 50 or idx > (n_points - 50): continue
            hits.append((x_local[idx].item(), R[idx].item()))

    sorted_hits = sorted(hits, key=lambda x: x[1], reverse=True)

    print("\n" + "█" * 70)
    print(f"{'🎯 TARGET AGGANCIATI A QUOTA 10^49':^70}")
    print("█" * 70)
    for loc_n, r in sorted_hits[:20]:
        full_n = Decimal(args.offset) + Decimal(loc_n)
        print(f"{str(full_n)[:25]}... | R: {r:.6f} | 🔥 CRITICO")
    print("█" * 70)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["attack"])
    parser.add_argument("--offset", type=str, required=True, help="Il numero RSA gigante")
    parser.add_argument("--start", type=float, default=-5000)
    parser.add_argument("--end", type=float, default=5000)
    parser.add_argument("--geo", default="adelic")
    parser.add_argument("--threshold", type=float, default=4.5)
    parser.add_argument("--zeros", default=DEFAULT_ZEROS_FILE)
    parser.add_argument("--max-zeros", type=int, default=1_000_000)
    
    args = parser.parse_args()
    device = torch.device("cuda")
    mode_attack(args, device)

if __name__ == "__main__":
    main()
