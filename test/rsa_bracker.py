import math
from tqdm import tqdm

def perrone_erdos_decoder(N):
    """
    Algoritmo di Fattorizzazione Ellittica di Perrone con TQDM.
    """
    beta = 1.6366
    
    # 1. Puntamento
    sqrt_n = int(math.isqrt(N))
    
    # 2. Correzione di Fase
    if sqrt_n % 2 == 0:
        p = sqrt_n - 1
    else:
        p = sqrt_n
        
    print(f"--- Sistema Perrone in funzione ---")
    print(f"Modulo N: {N}")
    print(f"Sintonizzazione sulla fase: {math.log(sqrt_n):.4f}")

    # 3. Scansione con Barra di Avanzamento
    # Il totale dei passi è circa sqrt(N) / 2
    total_steps = p // 2
    
    with tqdm(total=total_steps, desc="Scansione Nodi", unit="nodo", dynamic_ncols=True) as pbar:
        step = 2
        while p > 1:
            if N % p == 0:
                q = N // p
                pbar.close() # Chiude la barra alla scoperta
                print(f"\n--- Risonanza Trovata! ---")
                print(f"Nodo P: {p}")
                print(f"Nodo Q: {q}")
                return p, q
            
            p -= step
            pbar.update(1) # Incrementa la barra di 1 passo

    return None

# --- ESEMPIO DI DECODIFICA ---
if __name__ == "__main__":
    # Il tuo nuovo Q
    # N_obiettivo = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
    # perrone_erdos_decoder(N_obiettivo)
    import sys
    # N_obiettivo = 123456789012345678901234567891 #sys.argv[0]
    
    # perrone_erdos_decoder(N_obiettivo)
    perrone_erdos_decoder(int(sys.argv[1]))



"""
La fattorizzazione di RSA-100 è la seguente:

RSA-100 = 15226050279225333605356183781326374297180681149613
          80688657908494580122963258952897654000350692006139
RSA-100 = 37975227936943673922808872755445627854565536638199
        × 40094690950920881030683735292761468389214899724061
"""