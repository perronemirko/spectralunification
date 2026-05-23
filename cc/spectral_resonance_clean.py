#!/usr/bin/env python3
import torch
import math
import argparse
import time
import os

# --- COSTANTI GLOBALI ---
ERDOS_CONST = 1.6318
DEFAULT_ZEROS_FILE = "zeri_1M.txt"
BLOCK_SIZE = 100  # Ottimale per VRAM 24GB

# --- MOTORI GEOMETRICI (Scegli quello da usare in compute_resonance) ---

def get_minkowski_metric(x_vals):
    t = torch.log(x_vals)
    s = torch.sqrt(x_vals / ERDOS_CONST)
    return torch.sqrt(torch.abs(t**2 - s**2) + 1e-12)

def get_hyperbolic_metric(x_vals):
    x_mid = torch.mean(x_vals)
    return torch.acosh(x_vals / x_mid + 1e-12)

def get_symplectic_metric(x_vals):
    return torch.log(x_vals) / torch.sqrt(x_vals)

def get_euclidean_metric(x_vals):
    return torch.log(x_vals)

def get_string_metric(x_vals):
    """ Geometria delle Stringhe: Fase come vibrazione di una corda tesa """
    # La fase vibra come una stringa: sin(ln x) + cos(ln x) pesato
    ln_x = torch.log(x_vals)
    # Introduciamo la componente vibrazionale (modo n=1 della stringa)
    vibration = torch.sin(ln_x) * torch.cos(ln_x / ERDOS_CONST)
    return ln_x + vibration

def get_adelic_metric(x_vals):
    """ Geometria Adelic: Fusione di metrica reale e strutturale """
    ln_x = torch.log(x_vals)
    # Componente 'Locale' p-adica (sintonizzata su Erdos)
    local_structure = torch.sin(math.pi * x_vals / ERDOS_CONST)
    return ln_x * (1.0 + 0.05 * local_structure)

# --- CORE ENGINE ---

def normalize_and_detrend(signal, device):
    window_size = 50
    padding = window_size // 2
    s_4d = signal.unsqueeze(0).unsqueeze(0).to(torch.float32)
    padded = torch.nn.functional.pad(s_4d, (padding, padding), mode='replicate')
    kernel = torch.ones((1, 1, window_size), device=device) / window_size
    mean = torch.nn.functional.conv1d(padded, kernel).squeeze()
    
    if mean.dim() > 0 and mean.shape[0] > signal.shape[0]: 
        mean = mean[:signal.shape[0]]
    
    res = signal - mean
    R = (res - res.mean()) / (res.std() + 1e-12)
    return R.to(torch.float64)



def compute_resonance(x_vals, gamma, device, mode="minkowski"):
    sqrt_erdos = math.sqrt(ERDOS_CONST)
    
    # Selezione della Metrica Non-Euclidea
    if mode == "minkowski":
        metric_x = get_minkowski_metric(x_vals)
    elif mode == "hyperbolic":
        metric_x = get_hyperbolic_metric(x_vals)
    elif mode == "symplectic":
        metric_x = get_symplectic_metric(x_vals)
    elif mode == "string":
        metric_x = get_string_metric(x_vals)
    elif mode == "adelic":
        metric_x = get_adelic_metric(x_vals)
    else:
        metric_x = get_euclidean_metric(x_vals)

    
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE].to(torch.float32)
        b_weight = weight[i : i + BLOCK_SIZE]
        
        fase = b_gamma.unsqueeze(1) * metric_x.unsqueeze(0)
        
        # i^2 = -1.63 (Ellisse di Mirko)
        reale = torch.cos(fase)
        immag = torch.sin(fase) * sqrt_erdos
        
        fase_mirko = torch.complex(reale, immag)
        contributo = torch.sum(fase_mirko * b_weight.unsqueeze(1), dim=0)
        risonanza += contributo.squeeze()

    signal = torch.abs(risonanza) * torch.sqrt(x_vals)
    return normalize_and_detrend(signal, device)

# --- MODALITÀ DI ESECUZIONE ---

def load_zeros(filename, max_zeros, device):
    print(f"[*] Caricamento zeri da {filename}...")
    zeros = []
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if i >= max_zeros: break
            zeros.append(float(line.strip()))
    return torch.tensor(zeros, device=device, dtype=torch.float64)

def mode_attack(args, device):
    n_start, n_end = args.start, args.end
    chunk_size = 1000  
    gamma = load_zeros(args.zeros, args.max_zeros, device)

    print(f"\n[🚀 RADAR GEOMETRICO] Mode: {args.geo} | Range: {int(n_start):,}")
    
    raw_hits = []
    for current_s in range(int(n_start), int(n_end), chunk_size):
        current_e = min(current_s + chunk_size, n_end)
        n_points = int((current_e - current_s) * 500) 
        
        x_vals = torch.linspace(current_s, current_e, n_points, device=device, dtype=torch.float64)
        print(f"[*] Scansione Settore: [{current_s}] ...", end="\r")
        
        R = compute_resonance(x_vals, gamma, device, mode=args.geo)
        
        # Soglia di sensibilità
        mask = R > args.threshold
        if torch.any(mask):
            indices = torch.where(mask)[0]
            for idx in indices:
                if idx < 50 or idx > (n_points - 50): continue
                raw_hits.append((x_vals[idx].item(), R[idx].item()))
        
        del x_vals, R
        torch.cuda.empty_cache()

    refined_hits = {}
    for px, val_r in raw_hits:
        target_int = round(px)
        if target_int not in refined_hits or val_r > refined_hits[target_int]:
            refined_hits[target_int] = val_r

    sorted_hits = sorted(refined_hits.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "█" * 70)
    print(f"{'🎯 TARGET AGGANCIATI (' + args.geo.upper() + ')':^70}")
    print("█" * 70)
    for n, r in sorted_hits[:20]:
        prob = "🔥 CRITICO" if r > 5.0 else "💎 ALTA"
        print(f"{n:<25} | {r:<15.6f} | {prob}")
    print("█" * 70)
    print(f" Totale bersagli: {len(sorted_hits)}")

# --- MAIN ---

def main():
    parser = argparse.ArgumentParser(description="Spectral Resonance — Mirko Perrone")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_att = sub.add_parser("attack")
    p_att.add_argument("--start", type=float, required=True)
    p_att.add_argument("--end", type=float, required=True)
    p_att.add_argument("--geo", type=str, choices=['minkowski', 'adelic','string','hyperbolic', 'symplectic', 'euclidean'], default='minkowski')
    p_att.add_argument("--threshold", type=float, default=1.5)
    p_att.add_argument("--zeros", type=str, default=DEFAULT_ZEROS_FILE)
    p_att.add_argument("--max-zeros", type=int, default=1_000_000)

    args = parser.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if args.mode == "attack":
        mode_attack(args, device)

if __name__ == "__main__":
    main()
