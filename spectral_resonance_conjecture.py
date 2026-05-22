# # import torch
# # import mpmath as mp
# # import matplotlib.pyplot as plt

# # def dimostrazione_connessione(n_start=100, n_end=200, num_zeri=5000):
# #     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# #     print(f"--- TEST DI DIMOSTRAZIONE ERDŐS-RIEMANN ---")
    
# #     # 1. Calcoliamo la griglia con precisione assoluta
# #     x_vals = torch.arange(n_start, n_end, 0.1, device=device, dtype=torch.float64)
# #     log_x = torch.log(x_vals)
    
# #     # 2. Carichiamo gli zeri reali di Riemann
# #     # (Usiamo mpmath per averli esatti per il test)
# #     zeri = torch.tensor([float(mp.zetazero(i).imag) for i in range(1, num_zeri+1)], device=device)
    
# #     # 3. Funzione di Erdős-Riemann (La tua teoria)
# #     # Somma di cos(gamma * log x) / (1/4 + gamma^2)
# #     risonanza = torch.zeros_like(x_vals)
# #     for gamma in zeri:
# #         risonanza += torch.cos(gamma * log_x) / (0.25 + gamma**2)
    
# #     # 4. Troviamo i picchi di risonanza
# #     # Se la teoria regge, questi picchi devono essere vicini ai numeri primi
# #     picchi_idx = torch.topk(risonanza, 10).indices
# #     picchi_x = x_vals[picchi_idx]
    
# #     print("\nTop 5 punti di risonanza spettrale rilevati:")
# #     for px in sorted(picchi_x.tolist())[:5]:
# #         # Verifichiamo se vicino a quel punto c'è un numero primo
# #         prossimo_intero = round(px)
# #         is_prime = mp.isprime(prossimo_intero)
# #         print(f"Punto: {px:.1f} -> Intero vicino: {prossimo_intero} | È primo? {'SÌ' if is_prime else 'NO'}")

# #     return x_vals.cpu(), risonanza.cpu()

# # if __name__ == "__main__":
# #     x, y = dimostrazione_connessione()
# # import torch
# # import mpmath as mp
# # import time

# # def dimostrazione_connessione_gpu(n_start=100, n_end=1000, num_zeri=10000):
# #     # Forza l'uso della GPU
# #     device = torch.device("cuda")
# #     print(f"--- TEST DIMOSTRAZIONE: SATURAZIONE GPU ---")
# #     print(f"[*] Calcolo su: {torch.cuda.get_device_name(0)}")
    
# #     # 1. Griglia di punti (Aumentiamo il range per dare lavoro alla GPU)
# #     x_vals = torch.arange(n_start, n_end, 0.01, device=device, dtype=torch.float64)
# #     log_x = torch.log(x_vals)
    
# #     # 2. Caricamento Zeri (Vettorizzati)
# #     print(f"[*] Generazione di {num_zeri} zeri reali...")
# #     # Calcoliamo su CPU e spariamo su GPU
# #     zeri_list = [float(mp.zetazero(i).imag) for i in range(1, num_zeri + 1)]
# #     gamma = torch.tensor(zeri_list, device=device, dtype=torch.float64).unsqueeze(1)
    
# #     # 3. IL CUORE: Calcolo Matriciale (MatMul)
# #     # Questa operazione genera una matrice GIGANTE [num_zeri x punti_griglia]
# #     # È qui che la 4090 sprigiona la sua potenza
# #     t0 = time.time()
    
# #     # Calcoliamo la fase: gamma * log_x
# #     # gamma è [num_zeri, 1], log_x è [punti_griglia] -> risultato [num_zeri, punti_griglia]
# #     fasi = torch.matmul(gamma, log_x.unsqueeze(0))
    
# #     # Applichiamo cos(fase) / (0.25 + gamma^2)
# #     denominatore = 0.25 + gamma**2
# #     contributi = torch.cos(fasi) / denominatore
    
# #     # Sommiamo tutto lungo la dimensione degli zeri per ottenere la risonanza finale
# #     risonanza = torch.sum(contributi, dim=0)
    
# #     durata = time.time() - t0
# #     print(f"[*] Elaborazione GPU completata in {durata:.4f} secondi")

# #     # 4. Verifica dei picchi
# #     val, idx = torch.topk(risonanza, 10)
# #     picchi_x = x_vals[idx]
    
# #     print("\nVerifica dei picchi spettrali (Top 5):")
# #     punti_unici = []
# #     for px in picchi_x.tolist():
# #         intero = round(px)
# #         if intero not in punti_unici:
# #             punti_unici.append(intero)
# #             print(f"Risonanza a {px:.2f} -> {intero} è Primo? {'SÌ' if mp.isprime(intero) else 'NO'}")
# #         if len(punti_unici) >= 5: break

# # if __name__ == "__main__":
# #     dimostrazione_connessione_gpu()
# # import torch
# # import mpmath as mp
# # import time
# # from sympy import isprime # <--- Aggiungi questa riga all'inizio dello script
# # import os
# # # Ottimizzazione per prevenire la frammentazione della memoria
# # os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
# # def satura_4090_erdos_riemann(n_start=100, n_end=10000, num_zeri=500000):
# #     # Forza precisione 64-bit per non perdere la fase
# #     device = torch.device("cuda")
# #     print(f"--- 4090 STRESS TEST: ERDŐS-RIEMANN CONNECTION ---")
# #     print(f"[*] Obiettivo: Saturare 24GB VRAM e dimostrare la risonanza.")

# #     # 1. Caricamento Zeri (Usiamo la stima veloce per non bloccare la CPU)
# #     print(f"[*] Generazione {num_zeri} armoniche spettrali...")
# #     n_idx = torch.arange(1, num_zeri + 1, device=device, dtype=torch.float64)
# #     gamma = (2.0 * 3.141592653589793 * n_idx / torch.log(n_idx + 1.1)).unsqueeze(1)
    
# #     # 2. Creazione Griglia Massiva (10 Milioni di punti)
# #     print(f"[*] Allocazione griglia da 10M punti...")
# #     x_vals = torch.linspace(n_start, n_end, 10000000, device=device, dtype=torch.float64)
# #     log_x = torch.log(x_vals)

# #     # 3. IL CALCOLO MATRICIALE (MATMUL) - Qui la VRAM salirà
# #     print(f"[*] Inizio calcolo spettrale vettorializzato...")
# #     t0 = time.time()
    
# #     # Dividiamo in blocchi per non crashare, ma abbastanza grandi da far sudare la 4090
# #     dim_blocco = 70
# #     risonanza = torch.zeros_like(x_vals)
    
# #     for i in range(0, num_zeri, dim_blocco):
# #         fine = min(i + dim_blocco, num_zeri)
# #         b_gamma = gamma[i:fine]
        
# #         # Questa operazione genera una matrice di 5000 x 10.000.000 (circa 40GB virtuali)
# #         # PyTorch la gestisce ottimizzando i kernel CUDA
# #         fasi = torch.matmul(b_gamma, log_x.unsqueeze(0))
        
# #         denominatore = 0.25 + b_gamma**2
# #         contributi = torch.cos(fasi) / denominatore
        
# #         risonanza += torch.sum(contributi, dim=0)
        
# #         if i % 10000 == 0:
# #             print(f"    -> Progress: {i}/{num_zeri} armoniche calcolate.")
# #             # Controlla nvidia-smi ora: la memoria usata dovrebbe schizzare su!

# #     durata = time.time() - t0
# #     print(f"\n[*] Elaborazione GPU completata in {durata:.4f} secondi.")

# #     # 4. Verifica Scientifica dei Risultati
# #     val, idx = torch.topk(risonanza, 15)
# #     picchi_x = x_vals[idx]
    
# #     print("\n[!!!] RISULTATI DELLA RISONANZA DI ERDŐS:")
# #     trovati = set()
# #     for px in picchi_x.tolist():
# #         intero = round(px)
# #         if intero not in trovati and intero > 1:
# #             trovati.add(intero)
# #             is_prime = isprime(intero)
# #             print(f"Risonanza rilevata a {px:.2f} -> {intero} è Primo? {'SÌ' if is_prime else 'NO'}")
# #         if len(trovati) >= 10: break

# # if __name__ == "__main__":
# #     try:
# #         satura_4090_erdos_riemann()
# #     except Exception as e:
# #         print(f"Errore: {e}")
# import torch
# import mpmath as mp
# import time
# from sympy import isprime
# import os

# # Ottimizzazione memoria
# os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

# def satura_4090_erdos_riemann(n_start=100, n_end=10000, num_zeri=500000):
#     device = torch.device("cuda")
#     print(f"--- 4090 DEEP SCAN: ERDŐS-RIEMANN SPECTROMETRY ---")
    
#     # 1. Generazione Armoniche (500k per risoluzione laser)
#     n_idx = torch.arange(1, num_zeri + 1, device=device, dtype=torch.float64)
#     gamma = (2.0 * 3.141592653589793 * n_idx / torch.log(n_idx + 1.1)).unsqueeze(1)
    
#     # 2. Griglia Massiva
#     x_vals = torch.linspace(n_start, n_end, 10000000, device=device, dtype=torch.float64)
#     log_x = torch.log(x_vals)

#     # 3. Calcolo
#     risonanza = torch.zeros_like(x_vals)
#     t0 = time.time()
#     dim_blocco = 70
    
#     for i in range(0, num_zeri, dim_blocco):
#         fine = min(i + dim_blocco, num_zeri)
#         b_gamma = gamma[i:fine]
#         fasi = torch.matmul(b_gamma, log_x.unsqueeze(0))
#         contributi = torch.cos(fasi) / (0.25 + b_gamma**2)
#         risonanza += torch.sum(contributi, dim=0)
        
#         if i % 50000 == 0:
#             print(f"    -> Analisi frequenze: {i}/{num_zeri}...")

#     durata = time.time() - t0
#     print(f"[*] Elaborazione completata in {durata:.2f}s")

#     # 4. ANALISI POTENZIATA DEI PICCHI
#     # Prendiamo i primi 100 per trovare almeno 30 candidati unici
#     val, idx = torch.topk(risonanza, 100)
#     picchi_x = x_vals[idx]
    
#     print("\n" + "="*60)
#     print(f"{'RISONANZA':<15} | {'INTERO':<8} | {'STATO':<25}")
#     print("-"*60)
    
#     trovati = set()
#     for px in picchi_x.tolist():
#         intero = round(px)
#         if intero not in trovati and intero > 1:
#             trovati.add(intero)
            
#             # Analisi del vicinato (per identificare gemelli o offset)
#             if isprime(intero):
#                 stato = "✅ PRIMO PURO"
#             elif isprime(intero-1) and isprime(intero+1):
#                 stato = "💎 CENTRO GEMELLI"
#             elif isprime(intero-1):
#                 stato = "⬅️ VICINO A PRIMO (n-1)"
#             elif isprime(intero+1):
#                 stato = "➡️ VICINO A PRIMO (n+1)"
#             else:
#                 stato = "❌ COMPOSTO"
            
#             print(f"{px:<15.2f} | {intero:<8} | {stato}")
            
#         if len(trovati) >= 30: # Stampiamo i primi 30 unici
#             break
#     print("="*60)

# if __name__ == "__main__":
#     satura_4090_erdos_riemann()


# import torch
# import mpmath as mp
# import time
# from sympy import isprime
# import os

# # Ottimizzazione VRAM per 4090 (24GB)
# os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
# # Cambia il range: stringiamo il campo per 'centrare' i gemelli
# def resolution_smasher_4090(n_start=8080, n_end=8100, num_zeri=1000000):
#     # In questo modo, i 100 milioni di punti sono compressi in sole 20 unità.
#     # Ogni numero intero avrà 5 milioni di pixel di risoluzione!
# # def resolution_smasher_4090(n_start=8000, n_end=10000, num_zeri=1000000):
#     device = torch.device("cuda")
#     print(f"--- 4090 RESOLUTION SMASHER: SEPARAZIONE GEMELLI ---")
    
#     # 1. Caricamento 1 Milione di Zeri Reali (La tua 'musica' reale)
#     if os.path.exists("zeri_1M.txt"):
#         print("[*] Caricamento 1M zeri reali dal database...")
#         with open("zeri_1M.txt", "r") as f:
#             i_list = [float(line.strip()) for line in f.readlines()[:num_zeri]]
#         gamma = torch.tensor(i_list, device=device, dtype=torch.float64).unsqueeze(1)
#     else:
#         print("[!] File zeri_1M.txt non trovato! Uso la stima (Meno precisa).")
#         n_idx = torch.arange(1, num_zeri + 1, device=device, dtype=torch.float64)
#         gamma = (2.0 * 3.141592653589793 * n_idx / torch.log(n_idx + 1.1)).unsqueeze(1)

#     # 2. Griglia ad altissima densità (100 Milioni di punti per separare i gemelli)
#     print(f"[*] Generazione griglia: 100 MILIONI di pixel numerici...")
#     x_vals = torch.linspace(n_start, n_end, 100000000, device=device, dtype=torch.float64)
#     log_x = torch.log(x_vals)

#     # 3. Motore di Calcolo Vettorializzato
#     risonanza = torch.zeros_like(x_vals)
#     t0 = time.time()
    
#     # Blocco piccolissimo per gestire i 100M di punti senza OutOfMemory
#     dim_blocco = 10 
    
#     print(f"[*] Elaborazione 1M armoniche su 100M punti...")
#     for i in range(0, num_zeri, dim_blocco):
#         fine = min(i + dim_blocco, num_zeri)
#         b_gamma = gamma[i:fine]
        
#         # Fase e Risonanza
#         fasi = torch.matmul(b_gamma, log_x.unsqueeze(0))
#         contributi = torch.cos(fasi) / (0.25 + b_gamma**2)
        
#         risonanza += torch.sum(contributi, dim=0)
        
#         if i % 10000 == 0 and i > 0:
#             progresso = (i / num_zeri) * 100
#             print(f"    -> Progresso: {progresso:.1f}% | VRAM: {torch.cuda.memory_allocated() / 1024**2:.0f}MB")
#             torch.cuda.empty_cache()

#     durata = time.time() - t0
#     print(f"\n[*] Calcolo completato in {durata:.2f}s")

#     # 4. Analisi dei Picchi Isolati
#     val, idx = torch.topk(risonanza, 200) # Prendiamo molti punti per scartare i duplicati della griglia
#     picchi_x = x_vals[idx]
    
#     print("\n" + "="*70)
#     print(f"{'RISONANZA':<18} | {'INTERO':<10} | {'STATO'}")
#     print("-"*70)
    
#     trovati = set()
#     for px in picchi_x.tolist():
#         intero = round(px)
#         if intero not in trovati and intero > 1:
#             trovati.add(intero)
            
#             if isprime(intero):
#                 stato = "✅ PRIMO PURO"
#             elif isprime(intero-1) and isprime(intero+1):
#                 stato = "💎 CENTRO GEMELLI"
#             elif isprime(intero-1):
#                 stato = "⬅️ VICINO A PRIMO (n-1)"
#             elif isprime(intero+1):
#                 stato = "➡️ VICINO A PRIMO (n+1)"
#             else:
#                 stato = "❌ COMPOSTO"
            
#             print(f"{px:<18.5f} | {intero:<10} | {stato}")
            
#         if len(trovati) >= 20: break
#     print("="*70)

# if __name__ == "__main__":
#     try:
#         # Scansioniamo la zona del tuo precedente successo (8000-10000)
#         resolution_smasher_4090()
#     except Exception as e:
#         print(f"Errore: {e}")




import torch
import mpmath as mp
import time
from sympy import isprime
import os

# Ottimizzazione VRAM per 4090 (24GB)
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
# Cambia il range: stringiamo il campo per 'centrare' i gemelli
def resolution_smasher_4090(n_start=8080, n_end=8100, num_zeri=1000000):
    # In questo modo, i 100 milioni di punti sono compressi in sole 20 unità.
    # Ogni numero intero avrà 5 milioni di pixel di risoluzione!
# def resolution_smasher_4090(n_start=8000, n_end=10000, num_zeri=1000000):
    device = torch.device("cuda")
    print(f"--- 4090 RESOLUTION SMASHER: SEPARAZIONE GEMELLI ---")
    
    # 1. Caricamento 1 Milione di Zeri Reali (La tua 'musica' reale)
    if os.path.exists("zeri_1M.txt"):
        print("[*] Caricamento 1M zeri reali dal database...")
        with open("zeri_1M.txt", "r") as f:
            i_list = [float(line.strip()) for line in f.readlines()[:num_zeri]]
        gamma = torch.tensor(i_list, device=device, dtype=torch.float64).unsqueeze(1)
    else:
        print("[!] File zeri_1M.txt non trovato! Uso la stima (Meno precisa).")
        n_idx = torch.arange(1, num_zeri + 1, device=device, dtype=torch.float64)
        gamma = (2.0 * 3.141592653589793 * n_idx / torch.log(n_idx + 1.1)).unsqueeze(1)

    # 2. Griglia ad altissima densità (100 Milioni di punti per separare i gemelli)
    print(f"[*] Generazione griglia: 100 MILIONI di pixel numerici...")
    x_vals = torch.linspace(n_start, n_end, 100000000, device=device, dtype=torch.float64)
    log_x = torch.log(x_vals)

    # 3. Motore di Calcolo Vettorializzato
    risonanza = torch.zeros_like(x_vals)
    t0 = time.time()
    
    # Blocco piccolissimo per gestire i 100M di punti senza OutOfMemory
    dim_blocco = 10 
    
    print(f"[*] Elaborazione 1M armoniche su 100M punti...")
    for i in range(0, num_zeri, dim_blocco):
        fine = min(i + dim_blocco, num_zeri)
        b_gamma = gamma[i:fine]
        
        # Fase e Risonanza
        fasi = torch.matmul(b_gamma, log_x.unsqueeze(0))
        contributi = torch.cos(fasi) / (0.25 + b_gamma**2)
        
        risonanza += torch.sum(contributi, dim=0)
        
        if i % 10000 == 0 and i > 0:
            progresso = (i / num_zeri) * 100
            print(f"    -> Progresso: {progresso:.1f}% | VRAM: {torch.cuda.memory_allocated() / 1024**2:.0f}MB")
            torch.cuda.empty_cache()

    durata = time.time() - t0
    print(f"\n[*] Calcolo completato in {durata:.2f}s")
    # 4. ANALISI DEI PICCHI MULTIPLI (Modifica questa parte nel tuo script)
     # 4. ANALISI DEI PICCHI DISTINTI (Sostituisci questa sezione)
    print("\n" + "="*70)
    print(f"{'RISONANZA (x)':<18} | {'INTERO':<10} | {'STATO'}")
    print("-"*70)
    
    # Ordiniamo gli indici per intensità decrescente
    val_sorted, idx_sorted = torch.sort(risonanza, descending=True)
    
    trovati = set()
    count = 0
    
    # Scansioniamo i risultati finché non troviamo 15 numeri interi DISTINTI
    for i in range(len(idx_sorted)):
        px = x_vals[idx_sorted[i]].item()
        intero = round(px)
        
        # Se l'intero non è già in lista e rientra nel range
        if intero not in trovati and n_start <= intero <= n_end:
            trovati.add(intero)
            count += 1
            
            if isprime(intero):
                stato = "✅ PRIMO PURO"
            elif isprime(intero-1) and isprime(intero+1):
                stato = "💎 CENTRO GEMELLI"
            elif isprime(intero-1):
                stato = "⬅️ ADIACENTE (n-1)"
            elif isprime(intero+1):
                stato = "➡️ ADIACENTE (n+1)"
            else:
                stato = "❌ COMPOSTO"
            
            print(f"{px:<18.5f} | {intero:<8} | {stato}")
            
        if count >= 15: # Vogliamo i migliori 15 segnali diversi
            break
    print("="*70)


if __name__ == "__main__":
    try:
        # Scansioniamo la zona del tuo precedente successo (8000-10000)
        resolution_smasher_4090()
    except Exception as e:
        print(f"Errore: {e}")
