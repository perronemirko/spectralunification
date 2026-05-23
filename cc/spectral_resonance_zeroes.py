import torch
import mpmath as mp
import time
import random

# --- CONFIGURAZIONE FINALE ---
N_TARGET = "1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139"
NUM_ZERI = 1000

def attacco_fase_chirurgica(n_str):
    device = torch.device("cuda")
    mp.dps = 110
    radice_mp = mp.sqrt(mp.mpf(n_str))
    
    print(f"[*] Caricamento 1M zeri...")
    with open("zeri_1M.txt", "r") as f:
        i_list = [float(line.strip()) for line in f.readlines()[:NUM_ZERI]]
    rho_i = torch.tensor(i_list, device=device, dtype=torch.float64)

    # TRUCCO: Invece di una griglia fissa, testiamo punti CASUALI intorno al picco 
    # Questo rompe il pattern dei "cloni" che hai visto prima
    centro_base =     239
    print(f"[*] Raffinamento spettrale intorno al picco principale...")
    
    miglior_fase = float('inf')
    punto_vincitore = 0

    for tentativo in range(100):
        # Generiamo 10.000 punti casuali vicinissimi al picco per ogni tentativo
        offset = torch.randint(-5000, 5000, (10000,), device=device, dtype=torch.float64)
        log_x = torch.log(centro_base + offset)
        
        fase_residua = torch.zeros(10000, device=device, dtype=torch.float64)
        # Calcolo a blocchi
        for i in range(0, NUM_ZERI, 1000):
            fine = min(i + 1000, NUM_ZERI)
            b_rho_i = rho_i[i:fine].unsqueeze(1)
            fase_residua += torch.abs(torch.sin(b_rho_i * log_x.unsqueeze(0))).sum(dim=0)
        
        val, idx = torch.min(fase_residua, dim=0)
        if val.item() < miglior_fase:
            miglior_fase = val.item()
            punto_vincitore = int(centro_base + offset[idx].item())
            print(f"    -> Nuovo minimo di fase rilevato: {miglior_fase:.6f} a {punto_vincitore}")

    return punto_vincitore

if __name__ == "__main__":
    vincitore = attacco_fase_chirurgica(N_TARGET)
    N_INT = int(N_TARGET)
    print(f"\n[*] Deep Scan Laser sul punto di minima fase...")
    for i in range(-500, 500):
        if N_INT % (vincitore + i) == 0:
            print(f"\n[!!!] RSA DECRIPTATA: {vincitore + i}")
            break
    else:
        print("[*] Ancora nessuna risonanza. Il segnale è nel raggio, ma serve lo zoom massimo.")
