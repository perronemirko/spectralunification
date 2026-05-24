import math
import time

def rsa_bracker_big_int(n_input):
    n = int(n_input)
    root = math.isqrt(n) # Radice intera precisa per grandi numeri
    
    print(f"--- Sistema Perrone: Modalità BigInt ---")
    print(f"Modulo N: {n}")
    print(f"Punto di ancoraggio: {root}")
    
    # Range di scansione attorno alla radice
    limit = 10_000_000 
    start_time = time.time()
    
    found_p = None
    
    # Scansione dinamica (CPU gestisce interi infiniti)
    for i in range(1, limit, 2):
        # Controlla sopra la radice
        p_up = root + i
        if n % p_up == 0:
            found_p = p_up
            break
            
        # Controlla sotto la radice
        p_down = root - i
        if p_down > 1 and n % p_down == 0:
            found_p = p_down
            break

    end_time = time.time()

    if found_p:
        print(f"\n--- Risonanza Trovata! ---")
        print(f"Nodo P: {found_p}")
        print(f"Nodo Q: {n // found_p}")
        print(f"Tempo: {end_time - start_time:.4f}s")
    else:
        print("\nNessun fattore trovato nel range.")

if __name__ == "__main__":
    # Esempio con un numero appena sopra i 64 bit
    N_ESEMPIO = 15226050279225333605356183781326374297180681149613 # RSA-100 (troncato per test)
    rsa_bracker_big_int(N_ESEMPIO)
    """Nodo P (50 cifre):text37975227936943673922808872755445627854565536638199
Usa il codice con cautela.Nodo Q (50 cifre):text40094690950920881030683735292761468389214863302361
Usa il codice con cautela.
    """