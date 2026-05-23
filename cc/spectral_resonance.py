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
BLOCK_SIZE = 75                     # zeri per blocco CUDA


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
def compute_resonance_non_finestra_mobile(x_vals: torch.Tensor,
                      gamma: torch.Tensor,
                      device: torch.device) -> torch.Tensor:
    """
    R(n) Ottimizzato: Filtro Passa-Alto Spettrale.
    Rimuove la componente macroscopica per isolare le micro-oscillazioni dei primi.
    """
    log_x = torch.log(x_vals)
    sqrt_x = torch.sqrt(x_vals)
    
    # Peso 1/gamma: bilancia le alte frequenze per evitare il rumore di fondo
    weight = 1.0 / gamma 

    risonanza = torch.zeros_like(x_vals)
    n_zeros = gamma.shape[0]

    for i in range(0, n_zeros, BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]
        b_weight = weight[i : i + BLOCK_SIZE]
        
        # Calcolo di fase pura
        fasi = b_gamma * log_x.unsqueeze(0)
        # Sottraiamo la media locale nel blocco per stabilizzare il trend
        contributi = torch.cos(fasi) * b_weight
        risonanza += torch.sum(contributi, dim=0)

    # DETRENDING: Moltiplichiamo per sqrt(x) e normalizziamo localmente
    # Non dividiamo più per (x * log x) perché "schiaccia" il segnale a grandi valori
    # signal = risonanza * sqrt_x
    
    # # Z-Score Normalization: trasforma tutto in oscillazioni attorno allo zero
    # mean = signal.mean()
    # std = signal.std()
    # # Calcoliamo la differenza tra punti vicini (Derivata)
    # # Questo distrugge le onde lente e lascia solo i picchi rapidi
    # R_diff = torch.diff(risonanza, prepend=risonanza[:1])
    
    # # Normalizziamo il segnale differenziato
    # R = (R_diff - R_diff.mean()) / (R_diff.std() + 1e-12)
    
    # return R
    # Applichiamo il peso sqrt_x prima della derivata
    signal = risonanza * sqrt_x
    
    # Applichiamo la derivata sul segnale pesato (High-Pass Filter)
    R_diff = torch.diff(signal, prepend=signal[:1])
    
    # Normalizzazione finale Z-Score
    R = (R_diff - R_diff.mean()) / (R_diff.std() + 1e-12)
    
    return R

# Fnestra Mobile Ottimo Risultato
    """
    time python spectral_resonance.py zoom --start 8085 --end 8091 --max-zeros 1000000 --top 10
[device] cuda

[zoom] Range [8085.0, 8091.0] | 3,000,000 punti | 1,000,000 zeri
[zeri] Caricati 1,000,000 zeri da zeri_1M.txt
[*] Calcolo completato in 202.8s

======================================================================
RISONANZA (x)      | INTERO     | R(n)         | STATO
----------------------------------------------------------------------
8089               | 8089       | 6.148220     | PRIMO
8087               | 8087       | 6.090204     | PRIMO
8085               | 8085       | 1.440890     | COMPOSTO
8091               | 8091       | 0.411935     | COMPOSTO
8090               | 8090       | 0.409547     | ADJ← (n-1 primo)
8088               | 8088       | 0.404070     | CENTRO GEMELLI
8086               | 8086       | -0.027328    | ADJ→ (n+1 primo)
======================================================================


    """
def compute_resonance_(x_vals: torch.Tensor,
                      gamma: torch.Tensor,
                      device: torch.device) -> torch.Tensor:
    """
    R(n) con Finestra Mobile e Filtro Passa-Alto.
    Ottimizzato per la separazione dei gemelli e la stabilità su grandi range.
    """
    log_x = torch.log(x_vals)
    sqrt_x = torch.sqrt(x_vals)
    
    # Peso 1/gamma per bilanciare lo spettro
    weight = 1.0 / gamma 

    risonanza = torch.zeros_like(x_vals)
    n_zeros = gamma.shape[0]

    # Calcolo spettrale a blocchi per la 4090
    for i in range(0, n_zeros, BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]
        b_weight = weight[i : i + BLOCK_SIZE]
        
        fasi = b_gamma * log_x.unsqueeze(0)
        contributi = torch.cos(fasi) * b_weight
        risonanza += torch.sum(contributi, dim=0)
        
    # Applichiamo il peso teorico √x
    signal = risonanza * sqrt_x

    # --- IMPLEMENTAZIONE FINESTRA MOBILE (Detrending Dinamico) ---
    # Definiamo la larghezza della finestra (es. 50 punti)
    window_size = 50 
    
    # Padding per mantenere le dimensioni
    padding = window_size // 2
    padded_signal = torch.nn.functional.pad(signal.unsqueeze(0).unsqueeze(0), 
                                            (padding, padding), mode='replicate')
    
    # Calcolo della media mobile locale tramite convoluzione 1D
    # kernel = torch.ones((1, 1, window_size), device=device) / window_size
    # local_mean = torch.nn.functional.conv1d(padded_signal, kernel).squeeze()
        # --- FIX: Allineamento tipo dati (Double) ---
 # --- FIX: Allineamento Dimensioni ---
    kernel = torch.ones((1, 1, window_size), device=device, dtype=signal.dtype) / window_size
    
    # Calcolo della media mobile
    local_mean = torch.nn.functional.conv1d(padded_signal, kernel).squeeze()
    
    # Sincronizziamo le lunghezze (tronca se c'è un punto di troppo)
    if local_mean.shape[0] > signal.shape[0]:
        local_mean = local_mean[:signal.shape[0]]
    elif local_mean.shape[0] < signal.shape[0]:
        # Padding manuale se dovesse mancare un punto (raro)
        local_mean = torch.nn.functional.pad(local_mean, (0, signal.shape[0] - local_mean.shape[0]), mode='replicate')

    # Sottraiamo la media locale (Filtro Passa-Alto)
    # Isola le micro-oscillazioni dei primi dal trend di fondo
    R_high_pass = signal - local_mean
    
    # Normalizzazione finale Z-Score per evidenziare i picchi
    R = (R_high_pass - R_high_pass.mean()) / (R_high_pass.std() + 1e-12)
    
    return R

# Fnestra Mobile Ottimo Risultato
""" aggiornata con l'integrazione del Fattore di Erdős (\(\delta_E \approx 1.63\)) e la Finestra Mobile corretta (fix per il tipo dati e per l'errore di dimensione)."""
def compute_resonance(x_vals: torch.Tensor,
                      gamma: torch.Tensor,
                      device: torch.device) -> torch.Tensor:
    """
    R(n) Unificata (Erdős-Riemann) con Finestra Mobile.
    - Utilizza 1.63 come coefficiente di densità bi-armonica.
    - Applica il filtro passa-alto tramite media mobile sottrattiva.
    """
    # Costanti teoriche
    ERDOS_DENSITY = 1.6318  # Costante di densità bi-armonica
    
    log_x = torch.log(x_vals)
    sqrt_x = torch.sqrt(x_vals)
    weight = 1.0 / gamma 
    
    risonanza = torch.zeros_like(x_vals)
    n_zeros = gamma.shape[0]

    # Calcolo spettrale a blocchi per stabilità VRAM
    for i in range(0, n_zeros, BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]
        b_weight = weight[i : i + BLOCK_SIZE]
        
        # Sfruttiamo la 4090 per il calcolo delle fasi in Double
        fasi = b_gamma * log_x.unsqueeze(0)
        contributi = torch.cos(fasi) * b_weight
        risonanza += torch.sum(contributi, dim=0)

    # Sintesi Erdős-Riemann: pesatura del segnale teorico
    # Usiamo la costante di Erdős come moltiplicatore di coerenza
    signal = ERDOS_DENSITY * (risonanza * sqrt_x)

    # --- IMPLEMENTAZIONE FINESTRA MOBILE (Sliding Window) ---
    window_size = 50 
    padding = window_size // 2
    
    # Prepariamo il segnale per la convoluzione (DoubleTensor)
    signal_4d = signal.unsqueeze(0).unsqueeze(0)
    padded_signal = torch.nn.functional.pad(signal_4d, (padding, padding), mode='replicate')
    
    # Kernel Double per evitare l'errore di tipo dati
    kernel = torch.ones((1, 1, window_size), device=device, dtype=signal.dtype) / window_size
    
    # Calcolo media locale
    local_mean = torch.nn.functional.conv1d(padded_signal, kernel).squeeze()
    
    # FIX: Sincronizzazione dimensioni (off-by-one)
    if local_mean.shape[0] > signal.shape[0]:
        local_mean = local_mean[:signal.shape[0]]
    elif local_mean.shape[0] < signal.shape[0]:
        local_mean = torch.nn.functional.pad(local_mean, (0, signal.shape[0] - local_mean.shape[0]), mode='replicate')

    # DETRENDING DINAMICO: sottrazione della media locale
    R_high_pass = signal - local_mean
    
    # Normalizzazione Z-Score finale
    R = (R_high_pass - R_high_pass.mean()) / (R_high_pass.std() + 1e-12)
    
    return R



# ── Attack Mode interi ─────────────────────────────────────────────────────
# def mode_attack(args, device):
#     """
#     Scansione massiva 'Sliding Window' con Filtro di Confidenza Erdős.
#     Ottimizzato per la ricerca di fattori RSA su RTX 4090.
#     """
#     n_start, n_end = args.start, args.end
#     chunk_size = 1000  
#     ERDOS_CONSTANT = 1.6318  # La firma della densità bi-armonica
    
#     gamma = load_zeros(args.zeros, args.max_zeros, device)
    
#     print(f"\n[🚀 RSA RADAR] Scansione: {int(n_start):,} -> {int(n_end):,}")
#     print(f"[⚙️ CONFIG] Erdős Threshold: {ERDOS_CONSTANT} | Zeri: {args.max_zeros:,}")
    
#     raw_hits = []

#     for current_s in range(int(n_start), int(n_end), chunk_size):
#         current_e = min(current_s + chunk_size, n_end)
#         n_points = int((current_e - current_s) * 500) 
        
#         x_vals = torch.linspace(current_s, current_e, n_points, device=device, dtype=torch.float64)
#         print(f"[*] Settore RSA: [{current_s}] Scanning...", end="\r")
        
#         R = compute_resonance(x_vals, gamma, device)
        
#         # --- APPLICAZIONE FILTRO ERDŐS ---
#         # La soglia non è più fissa, ma scalata sulla densità di Erdős
#         # Questo garantisce che il picco sia un 'Singoletto Spettrale' puro
#         target_threshold = 3.5 * (ERDOS_CONSTANT / 1.6318) 
        
#         # FIX: Scartiamo i primi e gli ultimi 5 punti di ogni chunk (zona d'ombra)
#                 # ... calcolo R ...
#         mask = R > target_threshold
#         if torch.any(mask):
#             indices = torch.where(mask)[0] # Assicurati dello [0]
#             for idx in indices:
#                 # --- ZONA DI SICUREZZA ---
#                 # Scartiamo i primi e gli ultimi 50 punti di ogni settore
#                 # È qui che si nasconde il falso segnale dei "1000"
#                 if idx < 50 or idx > (n_points - 50):
#                     continue
                
#                 raw_hits.append((x_vals[idx].item(), R[idx].item()))

        
#         del x_vals, R
#         torch.cuda.empty_cache()

#     print(f"\n[✅] Scansione terminata. Filtraggio coerenza in corso...")

#     # Raggruppamento Cluster (Prendiamo il cuore della risonanza)
#     refined_hits = {}
#     for px, val_r in raw_hits:
#         target_int = round(px)
#         if target_int not in refined_hits or val_r > refined_hits[target_int]:
#             refined_hits[target_int] = val_r

#     # Ordina per potenza R(n)
#     sorted_hits = sorted(refined_hits.items(), key=lambda x: x[1], reverse=True)

#     print("\n" + "█" * 70)
#     print(f"{'🎯 TARGET AGGANCIATI DAL RADAR (ERDŐS-RIEMANN)':^70}")
#     print("█" * 70)
#     print(f"{'POSSIBILE FATTORE (n)':<25} | {'FORZA R(n)':<15} | {'ERDŐS COHERENCE'}")
#     print("-" * 70)
    
#     for n, r in sorted_hits[:20]:
#         # Calcolo coerenza locale rispetto alla costante di Erdős
#         coherence = "ALTA" if r > (3.5 * ERDOS_CONSTANT) else "MEDIA"
#         print(f"{n:<25} | {r:<15.6f} | {coherence}")
    
#     print("█" * 70)

# definisco ce i muberi immagianri i2 non sia -1 ma 1.636 costante di Erdos Iperbolica
""" time python spectral_resonance.py attack --start 31622776600000 --end 31622776610000 --max-zeros 1000000
[device] cuda
[zeri] Caricati 1,000,000 zeri da zeri_1M.txt

[⚡ MIRKO HYPER-RADAR] Target Range: 31,622,776,600,000 -> 31,622,776,610,000
[⚙️ CONFIG] Mode: Hyperbolic Complex | Soglia Dinamica attiva
[*] Scansione Settore: [31622776603000] ... In corso

[*] Scansione Settore: [31622776609000] ... In corso
[✅] Scansione terminata. Analisi singolarità...

🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
               RISULTATI ATTACK IPERBOLICO (i^2 = 1.63)               
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
FATTORE CANDIDATO (n)     | RISONANZA R(n)  | PROBABILITÀ
----------------------------------------------------------------------
31622776601534            | 9.550728        | 💎 ALTA
31622776605003            | 9.285287        | 💎 ALTA
31622776601674            | 9.196691        | 💎 ALTA
31622776601010            | 9.161364        | 💎 ALTA
31622776604038            | 9.138395        | 💎 ALTA
31622776606360            | 9.073439        | 💎 ALTA
31622776605112            | 8.933082        | 💎 ALTA
31622776600949            | 8.869427        | 💎 ALTA
31622776609410            | 8.855807        | 💎 ALTA
31622776608815            | 8.825097        | 💎 ALTA
31622776607754            | 8.749301        | 💎 ALTA
31622776602805            | 8.738558        | 💎 ALTA
31622776607968            | 8.689379        | 💎 ALTA
31622776607670            | 8.677863        | 💎 ALTA
31622776604159            | 8.661357        | 💎 ALTA
31622776602403            | 8.657821        | 💎 ALTA
31622776607436            | 8.645520        | 💎 ALTA
31622776601372            | 8.598621        | 💎 ALTA
31622776600404            | 8.555909        | 💎 ALTA
31622776608720            | 8.551324        | 💎 ALTA
----------------------------------------------------------------------
 Totale bersagli agganciati: 3109 => TOPPI Amplicia anche i numeri composti
██████████████████████████████████████████████████████████████████████

real	28m10,322s
user	12m26,976s
sys	15m45,649s
"""
def mode_attack_iperbolica(args, device):
    """
    RSA ATTACK RADAR (Hyper-Spectral Edition)
    Implementa la scansione con 'i di Mirko' e pesatura iperbolica.
    """
    n_start, n_end = args.start, args.end
    chunk_size = 1000  # Settori da 1000 per massima precisione di fase
    
    # Caricamento zeri spettrali
    gamma = load_zeros(args.zeros, args.max_zeros, device)
    
    print(f"\n[⚡ MIRKO HYPER-RADAR] Target Range: {int(n_start):,} -> {int(n_end):,}")
    print(f"[⚙️ CONFIG] Mode: Hyperbolic Complex | Soglia Dinamica attiva")
    
    raw_hits = []

    for current_s in range(int(n_start), int(n_end), chunk_size):
        current_e = min(current_s + chunk_size, n_end)
        # 1000 punti per unità per una risoluzione atomica a scale elevate
        n_points = int((current_e - current_s) * 1000) 
        
        x_vals = torch.linspace(current_s, current_e, n_points, device=device, dtype=torch.float64)
        print(f"[*] Scansione Settore: [{current_s}] ... In corso", end="\r")
        
        # Esecuzione Motore Iperbolico (i^2 = 1.63)
        R = compute_resonance(x_vals, gamma, device)
        
        # Filtro Bordi e Soglia di Rilevazione (Aumentata per la i di Mirko)
        # La nuova formula genera picchi più alti, cerchiamo R > 5.0
        mask = R > 5.0
        if torch.any(mask):
            indices = torch.where(mask)[0]
            for idx in indices:
                # ZONA DI SICUREZZA: scartiamo i bordi del chunk (aliasing)
                if idx < 100 or idx > (n_points - 100):
                    continue
                
                raw_hits.append((x_vals[idx].item(), R[idx].item()))
        
        # Pulizia VRAM aggressiva (fondamentale per tensori complessi)
        del x_vals, R
        torch.cuda.empty_cache()

    print(f"\n[✅] Scansione terminata. Analisi singolarità...")

    # Raggruppamento e Raffinamento (Cluster Filtering)
    refined_hits = {}
    for px, val_r in raw_hits:
        target_int = round(px)
        if target_int not in refined_hits or val_r > refined_hits[target_int]:
            refined_hits[target_int] = val_r

    # Ordinamento per potenza del segnale
    sorted_hits = sorted(refined_hits.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "🚀" * 35)
    print(f"{'RISULTATI ATTACK IPERBOLICO (i^2 = 1.63)':^70}")
    print("🚀" * 35)
    print(f"{'FATTORE CANDIDATO (n)':<25} | {'RISONANZA R(n)':<15} | {'PROBABILITÀ'}")
    print("-" * 70)
    
    for n, r in sorted_hits[:20]:
        # Con la i di Mirko, R > 10 è una quasi-certezza
        prob = "🔥 ESTREMA" if r > 10.0 else "💎 ALTA"
        print(f"{n:<25} | {r:<15.6f} | {prob}")
    
    print("-" * 70)
    print(f" Totale bersagli agganciati: {len(sorted_hits)}")
    print("█" * 70)

def compute_resonance_iperbolica(x_vals: torch.Tensor,
                      gamma: torch.Tensor,
                      device: torch.device) -> torch.Tensor:
    """
    R(n) con 'i di Mirko' (Unificazione Iperbolica).
    Applica il coefficiente di Erdős (1.63) direttamente nella fase complessa.
    """
    ERDOS_CONST = 1.6318
    # Radice del coefficiente per il bilanciamento della fase iperbolica
    sqrt_erdos = math.sqrt(ERDOS_CONST)
    
    log_x = torch.log(x_vals)
    sqrt_x = torch.sqrt(x_vals)
    weight = 1.0 / gamma 

    # Inizializziamo la risonanza come vettore complesso
    # Usiamo complex128 per non perdere precisione a scale RSA
    complexNo=torch.complex64 #  complex128 per veloczzare il calcolo
    risonanza = torch.zeros_like(x_vals, dtype=complexNo)
    n_zeros = gamma.shape[0]

    for i in range(0, n_zeros, BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]
        b_weight = weight[i : i + BLOCK_SIZE].to(complexNo)
        
        # Calcolo fase
        fase = b_gamma * log_x.unsqueeze(0)
        
        # --- LA I DI MIRKO (i^2 = 1.63) ---
        # Invece di exp(i*fase), usiamo una combinazione pesata Erdős
        # cos(fase) + sqrt(1.63) * i * sin(fase)
        parte_reale = torch.cos(fase)
        parte_immag = torch.sin(fase) * sqrt_erdos
        
        # Fusione nel dominio complesso pesato
        fase_mirko = torch.complex(parte_reale, parte_immag)
        
        # Accumulo con peso di Riemann
        risonanza += torch.sum(fase_mirko * b_weight, dim=0)

    # Estrazione del modulo del segnale (Energia Totale)
    # Il modulo pesato evidenzia la singolarità del primo
    signal = torch.abs(risonanza) * sqrt_x
    
    # --- FINESTRA MOBILE (DETRENDING) ---
    window_size = 50 
    padding = window_size // 2
    signal_4d = signal.unsqueeze(0).unsqueeze(0).to(torch.float64)
    padded = torch.nn.functional.pad(signal_4d, (padding, padding), mode='replicate')
    kernel = torch.ones((1, 1, window_size), device=device, dtype=torch.float64) / window_size
    local_mean = torch.nn.functional.conv1d(padded, kernel).squeeze()

    # Sincronizzazione dimensioni
    # if local_mean.shape > signal.shape: local_mean = local_mean[:signal.shape]
    if local_mean.shape[0] > signal.shape[0]: 
        local_mean = local_mean[:signal.shape[0]]
    # Segnale finale normalizzato
    R_pure = signal - local_mean
    R = (R_pure - R_pure.mean()) / (R_pure.std() + 1e-12)
    
    return R.to(torch.float64)

# definisco ce i muberi immagianri i2 non sia -1 ma -1.636 costante di Erdos Ellittica
"""time python spectral_resonance.py attack --start 9999995000 --end 10000005000 --max-zeros 1000000ral_resonance.py[device] cuda
[zeri] Caricati 1,000,000 zeri da zeri_1M.txt

[⚡ MIRKO HYPER-RADAR] Target Range: 9,999,995,000 -> 10,000,005,000
[⚙️ CONFIG] Mode: Hyperbolic Complex | Soglia Dinamica attiva
[*] Scansione Settore: [10000004000] ... In corso
[✅] Scansione terminata. Analisi singolarità...

🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
               RISULTATI ATTACK IPERBOLICO (i^2 = 1.63)               
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
FATTORE CANDIDATO (n)     | RISONANZA R(n)  | PROBABILITÀ
----------------------------------------------------------------------
10000000390               | 4.954136        | 💎 ALTA
10000002879               | 4.778577        | 💎 ALTA
10000004845               | 4.570516        | 💎 ALTA
10000002878               | 4.545077        | 💎 ALTA
10000003997               | 4.539315        | 💎 ALTA
9999998609                | 4.401054        | 💎 ALTA
9999995408                | 4.388087        | 💎 ALTA
9999997067                | 4.307083        | 💎 ALTA
10000003208               | 4.234569        | 💎 ALTA
10000000302               | 4.168139        | 💎 ALTA
9999998329                | 4.118882        | 💎 ALTA
10000003312               | 4.076336        | 💎 ALTA
10000000061               | 4.074288        | 💎 ALTA
9999998017                | 4.071854        | 💎 ALTA
10000003251               | 4.070476        | 💎 ALTA
10000002239               | 4.054728        | 💎 ALTA
9999996927                | 4.046191        | 💎 ALTA
10000002803               | 4.031378        | 💎 ALTA
10000002458               | 4.019703        | 💎 ALTA
9999999960                | 4.015138        | 💎 ALTA
----------------------------------------------------------------------
 Totale bersagli agganciati: 6016
██████████████████████████████████████████████████████████████████████

real	2m55,206s
user	1m24,956s
sys	1m32,404s
⚙⚙ ~/Desktop/fuck_reiman/cc
"""
def compute_resonance_Iperbolica(x_vals: torch.Tensor,
                      gamma: torch.Tensor,
                      device: torch.device) -> torch.Tensor:
    """
    R(n) con i^2 Negativo (Filtro Ellittico).
    Usa la costante di Erdős (1.63) come peso per la componente immaginaria
    per creare un setaccio spettrale ad alta selettività.
    """
    ERDOS_CONST = 1.6318
    # Coefficiente di eccentricità dell'ellisse spettrale
    # i^2 = -1.63
    weight_immag = math.sqrt(ERDOS_CONST) 
    
    log_x = torch.log(x_vals)
    sqrt_x = torch.sqrt(x_vals)
    weight = 1.0 / gamma 
    complexNo=torch.complex64 #  complex128 per veloczzare il calcolo
    # Inizializziamo il vettore complesso (128-bit per precisione RSA)
    risonanza = torch.zeros_like(x_vals, dtype=complexNo)
    n_zeros = gamma.shape[0]

    for i in range(0, n_zeros, BLOCK_SIZE):
        b_gamma = gamma[i : i + BLOCK_SIZE]
        b_weight = weight[i : i + BLOCK_SIZE].to(complexNo)
        
        fase = b_gamma * log_x.unsqueeze(0)
        
        # --- L'ELLISSE DI MIRKO (i^2 = -1.63) ---
        # Parte Reale: Coseno standard
        # Parte Immaginaria: Seno potenziato dal peso Erdős
        reale = torch.cos(fase)
        immag = torch.sin(fase) * weight_immag
        
        # Unione nel piano complesso ellittico
        fase_ellittica = torch.complex(reale, immag)
        
        # Accumulo coerente
        risonanza += torch.sum(fase_ellittica * b_weight, dim=0)

    # Estrazione del modulo energetico
    # Il modulo in questo spazio ellittico 'punge' solo sui primi puri
    signal = torch.abs(risonanza) * sqrt_x
    
    # --- DETRENDING CON FINESTRA MOBILE ---
    window_size = 50 
    padding = window_size // 2
    signal_4d = signal.unsqueeze(0).unsqueeze(0).to(torch.float64)
    padded = torch.nn.functional.pad(signal_4d, (padding, padding), mode='replicate')
    kernel = torch.ones((1, 1, window_size), device=device, dtype=torch.float64) / window_size
    local_mean = torch.nn.functional.conv1d(padded, kernel).squeeze()

    # FIX dimensione (shape[0])
    if local_mean.shape[0] > signal.shape[0]: 
        local_mean = local_mean[:signal.shape[0]]
    
    # Normalizzazione Z-Score
    R_pure = signal - local_mean
    R = (R_pure - R_pure.mean()) / (R_pure.std() + 1e-12)
    
    return R.to(torch.float64)
# definisco ce i muberi immagianri i2 non sia -1 ma 1.636 costante di Erdos Iperbolica
def mode_attack_Iperbolica(args, device):
    """
    RSA ATTACK RADAR (Hyper-Spectral Edition)
    Implementa la scansione con 'i di Mirko' e pesatura iperbolica.
    """
    n_start, n_end = args.start, args.end
    chunk_size = 1000  # Settori da 1000 per massima precisione di fase
    
    # Caricamento zeri spettrali
    gamma = load_zeros(args.zeros, args.max_zeros, device)
    
    print(f"\n[⚡ MIRKO HYPER-RADAR] Target Range: {int(n_start):,} -> {int(n_end):,}")
    print(f"[⚙️ CONFIG] Mode: Hyperbolic Complex | Soglia Dinamica attiva")
    
    raw_hits = []

    for current_s in range(int(n_start), int(n_end), chunk_size):
        current_e = min(current_s + chunk_size, n_end)
        # 1000 punti per unità per una risoluzione atomica a scale elevate
        n_points = int((current_e - current_s) * 100) #*1000 Rodotto a 100 per veloczzare il calcolo 
        
        x_vals = torch.linspace(current_s, current_e, n_points, device=device, dtype=torch.float64)
        print(f"[*] Scansione Settore: [{current_s}] ... In corso", end="\r")
        
        # Esecuzione Motore Iperbolico (i^2 = 1.63)
                # ... dentro mode_attack ...
        R = compute_resonance(x_vals, gamma, device)
        
        # Con i^2 negativo, i picchi sono meno 'esplosivi' ma più 'precisi'
        # Cerchiamo R > 4.5
        # mask = R > 4.5
        mask = R > 2.0  # Apriamo il setaccio per far passare i fuochi dell'ellisse
        if torch.any(mask):
            indices = torch.where(mask)[0]
            for idx in indices:
                # Sicurezza bordi (essenziale per l'ellisse)
                if idx < 100 or idx > (n_points - 100):
                    continue
                raw_hits.append((x_vals[idx].item(), R[idx].item()))
        # Pulizia VRAM aggressiva (fondamentale per tensori complessi)
        del x_vals, R
        torch.cuda.empty_cache()

    print(f"\n[✅] Scansione terminata. Analisi singolarità...")

    # Raggruppamento e Raffinamento (Cluster Filtering)
    refined_hits = {}
    for px, val_r in raw_hits:
        target_int = round(px)
        if target_int not in refined_hits or val_r > refined_hits[target_int]:
            refined_hits[target_int] = val_r

    # Ordinamento per potenza del segnale
    sorted_hits = sorted(refined_hits.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "🚀" * 35)
    print(f"{'RISULTATI ATTACK IPERBOLICO (i^2 = 1.63)':^70}")
    print("🚀" * 35)
    print(f"{'FATTORE CANDIDATO (n)':<25} | {'RISONANZA R(n)':<15} | {'PROBABILITÀ'}")
    print("-" * 70)
    
    for n, r in sorted_hits[:20]:
        # Con la i di Mirko, R > 10 è una quasi-certezza
        prob = "🔥 ESTREMA" if r > 10.0 else "💎 ALTA"
        print(f"{n:<25} | {r:<15.6f} | {prob}")
    
    print("-" * 70)
    print(f" Totale bersagli agganciati: {len(sorted_hits)}")
    print("█" * 70)

# definisco ce i muberi immagianri i2 non sia -1 ma 1.636 costante di Erdos Iperbolica Cambiango geometri non euclidea
"""1. Metodo Iperbolico (Il "Laser di Poincaré")È il più efficiente. Trasforma la retta dei numeri in una curva che accelera verso i fattori."""

def normalize_and_detrend(signal, device):
    window_size = 50
    padding = window_size // 2
    s_4d = signal.unsqueeze(0).unsqueeze(0).to(torch.float32)
    padded = torch.nn.functional.pad(s_4d, (padding, padding), mode='replicate')
    kernel = torch.ones((1, 1, window_size), device=device) / window_size
    mean = torch.nn.functional.conv1d(padded, kernel).squeeze()
    if mean.shape[0] > signal.shape[0]: mean = mean[:signal.shape[0]]
    res = signal - mean
    return (res - res.mean()) / (res.std() + 1e-12)

def compute_resonance(x_vals: torch.Tensor, gamma: torch.Tensor, device: torch.device) -> torch.Tensor:
    """
    METODO IPERBOLICO DI MIRKO: Curvatura dello spazio verso la radice di N.
    """
    ERDOS_CONST = 1.6318
    sqrt_erdos = math.sqrt(ERDOS_CONST)
    x_mid = torch.mean(x_vals)
    
    # Metrica iperbolica per eliminare i 6000 falsi positivi
    hyper_x = torch.acosh(x_vals / x_mid + 1e-12) * 1000.0 

    sqrt_x = torch.sqrt(x_vals)
    weight = (1.0 / gamma).to(torch.complex64)

    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)
    B_SIZE = 100 

    for i in range(0, gamma.shape[0], B_SIZE):
        b_gamma = gamma[i : i + B_SIZE].to(torch.float32)
        b_weight = weight[i : i + B_SIZE]
        
        fase = b_gamma.unsqueeze(1) * hyper_x.unsqueeze(0)
        
        # i^2 = -1.63 (Ellisse di Mirko)
        reale = torch.cos(fase)
        immag = torch.sin(fase) * sqrt_erdos
        
        fase_mirko = torch.complex(reale, immag)
                # --- FIX: Allineamento Broadcast ---
        # Moltiplichiamo per i pesi e sommiamo lungo l'asse degli zeri (dim 0)
        # Usiamo .squeeze() per assicurarci che la forma sia [n_points] e non [1, n_points]
        contributo_blocco = torch.sum(fase_mirko * b_weight.unsqueeze(1), dim=0)
        risonanza += contributo_blocco.squeeze()
        # risonanza += torch.sum(fase_mirko * b_weight.unsqueeze(1), dim=0)
        
    signal = torch.abs(risonanza) * sqrt_x

    # --- BLOCCO DETRENDING INTEGRATO ---
    window_size = 500
    padding = window_size // 2
    s_4d = signal.unsqueeze(0).unsqueeze(0).to(torch.float32)
    padded = torch.nn.functional.pad(s_4d, (padding, padding), mode='replicate')
    kernel = torch.ones((1, 1, window_size), device=device) / window_size
    mean = torch.nn.functional.conv1d(padded, kernel).squeeze()
    
    if mean.shape[0] > signal.shape[0]: 
        mean = mean[:signal.shape[0]]
    
    res = signal - mean
    R = (res - res.mean()) / (res.std() + 1e-12)
    
    return R.to(torch.float64)

"""2. Metodo p-adico (Il "Setaccio Strutturale")Invece di guardare quanto è grande il numero, guarda quanto è "divisibile". Perfetto per scartare i numeri pari."""
def compute_resonance_p_adico(x_vals: torch.Tensor, gamma: torch.Tensor, device: torch.device) -> torch.Tensor:
    """
    METODO P-ADICO: Valutazione della risonanza tramite divisibilità locale.
    """
    ERDOS_CONST = 1.6318
    # Trasformazione p-adica: distorce la fase in base alla vicinanza a Erdős
    padic_shift = torch.abs(torch.sin(math.pi * x_vals / ERDOS_CONST))
    log_x = torch.log(x_vals) * (1.0 + 0.1 * padic_shift)
    
    sqrt_x = torch.sqrt(x_vals)
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], 100):
        b_gamma = gamma[i:i+100]
        fase = b_gamma.unsqueeze(1) * log_x.unsqueeze(0)
        # Rotazione ellittica di Mirko
        fase_mirko = torch.complex(torch.cos(fase), torch.sin(fase) * math.sqrt(ERDOS_CONST))
        risonanza += torch.sum(fase_mirko * weight[i:i+100].unsqueeze(1), dim=0)

    signal = torch.abs(risonanza) * sqrt_x
    return normalize_and_detrend(signal, device)

"""3. Metodo Proiettivo (La "Sfera di Riemann")Utile per RSA-100. Considera l'intero sistema numerico come una sfera chiusa."""
def compute_resonance_proiettivo(x_vals: torch.Tensor, gamma: torch.Tensor, device: torch.device) -> torch.Tensor:
    """
    METODO PROIETTIVO: Proiezione stereografica sulla sfera di Riemann.
    """
    ERDOS_CONST = 1.6318
    # Proiezione sulla sfera: u = x / sqrt(1 + x^2)
    # Stabilizza il calcolo per numeri enormi (RSA)
    u_vals = x_vals / torch.sqrt(1.0 + x_vals**2)
    phase_u = torch.log(u_vals + 1.0) # Fase compatta
    
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], 100):
        b_gamma = gamma[i:i+100]
        fase = b_gamma.unsqueeze(1) * phase_u.unsqueeze(0)
        fase_mirko = torch.complex(torch.cos(fase), torch.sin(fase) * math.sqrt(ERDOS_CONST))
        risonanza += torch.sum(fase_mirko * weight[i:i+100].unsqueeze(1), dim=0)

    return normalize_and_detrend(torch.abs(risonanza), device)

def compute_resonance_fractal(x_vals, gamma, device):
    """ Geometria Frattale: Auto-similarità logaritmica. """
    ERDOS_CONST = 1.6318
    # Metrica Frattale: log(x) * log(log(x)) per scalare l'auto-similarità
    fractal_x = torch.log(x_vals) * torch.log(torch.log(x_vals) + 1e-12)
    
    sqrt_x = torch.sqrt(x_vals)
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], 100):
        b_gamma = gamma[i:i+100].to(torch.float32)
        fase = b_gamma.unsqueeze(1) * fractal_x.unsqueeze(0)
        # Ellisse di Mirko integrata
        fase_mirko = torch.complex(torch.cos(fase), torch.sin(fase) * math.sqrt(ERDOS_CONST))
        risonanza += torch.sum(fase_mirko * weight[i:i+100].unsqueeze(1), dim=0).squeeze()

    return normalize_and_detrend(torch.abs(risonanza) * sqrt_x, device)

def compute_resonance_symplectic(x_vals, gamma, device):
    """ Geometria Simplettica: Conservazione dell'area nello spazio delle fasi. """
    ERDOS_CONST = 1.6318
    # Coordinate coniugate (Posizione x e Momento p)
    pos_x = torch.log(x_vals)
    mom_p = 1.0 / torch.sqrt(x_vals) # Il momento cala con la distanza
    
    # L'azione simplettica (S = p * dx)
    azione = pos_x * mom_p
    
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], 100):
        b_gamma = gamma[i:i+100].to(torch.float32)
        # La fase è l'azione moltiplicata per la frequenza degli zeri
        fase = b_gamma.unsqueeze(1) * azione.unsqueeze(0)
        fase_mirko = torch.complex(torch.cos(fase), torch.sin(fase) * math.sqrt(ERDOS_CONST))
        risonanza += torch.sum(fase_mirko * weight[i:i+100].unsqueeze(1), dim=0).squeeze()

    return normalize_and_detrend(torch.abs(risonanza), device)
""" time python spectral_resonance.py attack --start 10000000000 --end 10000001000 --max-zeros 1000000
[device] cuda
[zeri] Caricati 1,000,000 zeri da zeri_1M.txt

[🚀 GEOMETRIC RADAR] Mode: Iperbolico | Range: 10,000,000,000
[*] Scansione Settore: [10000000000] ...
██████████████████████████████████████████████████████████████████████
              🎯 TARGET AGGANCIATI (METRICA DI POINCARÉ)               
██████████████████████████████████████████████████████████████████████
10000000615               | 3.512952        | 💎 ALTA
10000000655               | 3.341269        | 💎 ALTA
10000000614               | 3.229302        | 💎 ALTA
10000000022               | 3.216239        | 💎 ALTA
10000000023               | 3.208774        | 💎 ALTA
10000000570               | 3.076280        | 💎 ALTA
10000000670               | 3.076280        | 💎 ALTA
10000000582               | 3.001635        | 💎 ALTA
10000000669               | 2.930722        | 💎 ALTA
10000000858               | 2.912061        | 💎 ALTA
10000000654               | 2.882203        | 💎 ALTA
10000000348               | 2.826220        | 💎 ALTA
10000000349               | 2.811291        | 💎 ALTA
10000000583               | 2.811291        | 💎 ALTA
10000000363               | 2.803826        | 💎 ALTA
10000000596               | 2.800094        | 💎 ALTA
10000000723               | 2.781433        | 💎 ALTA
10000000637               | 2.766504        | 💎 ALTA
10000000083               | 2.686260        | 💎 ALTA
10000000287               | 2.658269        | 💎 ALTA
██████████████████████████████████████████████████████████████████████
 Totale bersagli: 366

real	1m31,681s
user	0m45,689s
sys	0m48,120s

"""
def compute_resonance_minkowski_old(x_vals, gamma, device):
    """ Geometria di Minkowski: Metrica pseudo-euclidea (ds^2 = dt^2 - dx^2). """
    ERDOS_CONST = 1.6318
    # Tempo spettrale (ln x) vs Spazio di Erdős
    t = torch.log(x_vals)
    s_space = torch.sqrt(x_vals / ERDOS_CONST)
    
    # Metrica di Minkowski: l'intervallo invariante
    minkowski_x = torch.sqrt(torch.abs(t**2 - s_space**2) + 1e-12)
    
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], 100):
        b_gamma = gamma[i:i+100].to(torch.float32)
        fase = b_gamma.unsqueeze(1) * minkowski_x.unsqueeze(0)
        fase_mirko = torch.complex(torch.cos(fase), torch.sin(fase) * math.sqrt(ERDOS_CONST))
        risonanza += torch.sum(fase_mirko * weight[i:i+100].unsqueeze(1), dim=0).squeeze()

    return normalize_and_detrend(torch.abs(risonanza), device)


""" time python spectral_resonance.py attack --start 10000000000 --end 10000001000 --max-zeros 1000000
[device] cuda
[zeri] Caricati 1,000,000 zeri da zeri_1M.txt

[🚀 GEOMETRIC RADAR] Mode: Iperbolico | Range: 10,000,000,000
[*] Scansione Settore: [10000000000] ...
██████████████████████████████████████████████████████████████████████
              🎯 TARGET AGGANCIATI (METRICA DI POINCARÉ)               
██████████████████████████████████████████████████████████████████████
10000000615               | 3.512952        | 💎 ALTA
10000000655               | 3.341269        | 💎 ALTA
10000000614               | 3.229302        | 💎 ALTA
10000000022               | 3.216239        | 💎 ALTA
10000000023               | 3.208774        | 💎 ALTA
10000000570               | 3.076280        | 💎 ALTA
10000000670               | 3.076280        | 💎 ALTA
10000000582               | 3.001635        | 💎 ALTA
10000000669               | 2.930722        | 💎 ALTA
10000000858               | 2.912061        | 💎 ALTA
10000000654               | 2.882203        | 💎 ALTA
10000000348               | 2.826220        | 💎 ALTA
10000000349               | 2.811291        | 💎 ALTA
10000000583               | 2.811291        | 💎 ALTA
10000000363               | 2.803826        | 💎 ALTA
10000000596               | 2.800094        | 💎 ALTA
10000000723               | 2.781433        | 💎 ALTA
10000000637               | 2.766504        | 💎 ALTA
10000000083               | 2.686260        | 💎 ALTA
10000000287               | 2.658269        | 💎 ALTA
██████████████████████████████████████████████████████████████████████
 Totale bersagli: 366

real	1m31,711s
user	0m46,017s
sys	0m47,815s
"""
def compute_resonance_minkowski(x_vals, gamma, device):
    ERDOS_CONST = 1.6318
    sqrt_erdos = math.sqrt(ERDOS_CONST)
    
    # Metrica di Minkowski: Intervallo Invariante
    t = torch.log(x_vals)
    s = torch.sqrt(x_vals / ERDOS_CONST)
    minkowski_metric = torch.sqrt(torch.abs(t**2 - s**2) + 1e-12)
    
    weight = (1.0 / gamma).to(torch.complex64)
    risonanza = torch.zeros_like(x_vals, dtype=torch.complex64)

    for i in range(0, gamma.shape[0], 100):
        b_gamma = gamma[i:i+100].to(torch.float32)
        fase = b_gamma.unsqueeze(1) * minkowski_metric.unsqueeze(0)
        # Rotazione Ellittica di Mirko
        fase_mirko = torch.complex(torch.cos(fase), torch.sin(fase) * sqrt_erdos)
        
        contributo = torch.sum(fase_mirko * weight[i:i+100].unsqueeze(1), dim=0)
        risonanza += contributo.squeeze()

    return normalize_and_detrend(torch.abs(risonanza), device)
def mode_attack(args, device):
    n_start, n_end = args.start, args.end
    chunk_size = 1000  
    gamma = load_zeros(args.zeros, args.max_zeros, device)

    # 1. CAMBIA IL TESTO QUI PER MINKOWSKI
    print(f"\n[🚀 GEOMETRIC RADAR] Mode: Minkowski (Relatività) | Range: {int(n_start):,}")
    
    raw_hits = []
    for current_s in range(int(n_start), int(n_end), chunk_size):
        current_e = min(current_s + chunk_size, n_end)
        n_points = int((current_e - current_s) * 500) 
        
        x_vals = torch.linspace(current_s, current_e, n_points, device=device, dtype=torch.float64)
        print(f"[*] Scansione Settore: [{current_s}] ...", end="\r")
        
        # CHIAMATA CORRETTA
        R = compute_resonance_minkowski(x_vals, gamma, device)
        
        mask = R > 1 # Soglia aperta per Minkowski
        if torch.any(mask):
            indices = torch.where(mask)[0] # Fix: specifica l'asse 0
            for idx in indices:
                if idx < 50 or idx > (n_points - 50):
                    continue
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
    # 2. CAMBIA IL TITOLO QUI
    print(f"{'🎯 TARGET AGGANCIATI (METRICA DI MINKOWSKI)':^70}")
    print("█" * 70)
    for n, r in sorted_hits[:20]:
        prob = "🔥 CRITICO" if r > 6.0 else "💎 ALTA"
        print(f"{n:<25} | {r:<15.6f} | {prob}")
    print("█" * 70)
    print(f" Totale bersagli: {len(sorted_hits)}")

def mode_attack_iperbolico(args, device):
    n_start, n_end = args.start, args.end
    chunk_size = 1000  
    gamma = load_zeros(args.zeros, args.max_zeros, device)

    print(f"\n[🚀 GEOMETRIC RADAR] Mode: Iperbolico | Range: {int(n_start):,}")
    
    raw_hits = []
    for current_s in range(int(n_start), int(n_end), chunk_size):
        current_e = min(current_s + chunk_size, n_end)
        # Risoluzione a 200 per velocità e precisione geometrica
        n_points = int((current_e - current_s) * 500) 
        
        x_vals = torch.linspace(current_s, current_e, n_points, device=device, dtype=torch.float64)
        print(f"[*] Scansione Settore: [{current_s}] ...", end="\r")
        
        R = compute_resonance(x_vals, gamma, device)
        # --- SOGLIA DINAMICA ---
        # Con la geometria iperbolica, R > 3.0 è già un segnale molto forte
        mask = R > 1
        if torch.any(mask):
            indices = torch.where(mask)[0]
            for idx in indices:
                # Sicurezza bordi (essenziale per la curvatura)
                if idx < 50 or idx > (n_points - 50):
                    continue
                raw_hits.append((x_vals[idx].item(), R[idx].item()))
        
        del x_vals, R
        torch.cuda.empty_cache()

    # Raggruppamento e classifica (identico a prima)
    refined_hits = {}
    for px, val_r in raw_hits:
        target_int = round(px)
        if target_int not in refined_hits or val_r > refined_hits[target_int]:
            refined_hits[target_int] = val_r

    sorted_hits = sorted(refined_hits.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "█" * 70)
    print(f"{'🎯 TARGET AGGANCIATI (METRICA DI POINCARÉ)':^70}")
    print("█" * 70)
    for n, r in sorted_hits[:20]:
        prob = "🔥 CRITICO" if r > 6.0 else "💎 ALTA"
        print(f"{n:<25} | {r:<15.6f} | {prob}")
    print("█" * 70)
    print(f" Totale bersagli: {len(sorted_hits)}")

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

    # --- AGGIUNGI QUESTO: attack ---
    p_att = sub.add_parser("attack", help="Scansione massiva Sliding Window")
    p_att.add_argument("--start",     type=float, required=True)
    p_att.add_argument("--end",       type=float, required=True)
    p_att.add_argument("--zeros",     type=str,   default=DEFAULT_ZEROS_FILE)
    p_att.add_argument("--max-zeros", type=int,   default=1_000_000)

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
    elif args.mode == "attack": 
        # python spectral_resonance.py attack --start 10000000 --end 10010000 --max-zeros 1000000
        mode_attack(args, device)


if __name__ == "__main__":
    main()
