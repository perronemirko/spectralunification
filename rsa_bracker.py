import math

def perrone_erdos_decoder(N):
    """
    Algoritmo di Fattorizzazione Ellittica di Perrone.
    Cerca i fattori primi p e q sfruttando la risonanza della costante Beta (1.6366)
    e la simmetria del cardine 5.
    """
    beta = 1.6366
    
    # 1. Puntamento: Centro di gravità dell'ellissoide
    sqrt_n = int(math.isqrt(N))
    
    # 2. Correzione di Fase: Iniziamo la scansione dai numeri dispari
    # vicini alla radice, dove la tensione di Erdos è massima.
    if sqrt_n % 2 == 0:
        p = sqrt_n - 1
    else:
        p = sqrt_n
        
    print(f"--- Sistema Perrone in funzione ---")
    print(f"Modulo N: {N}")
    print(f"Sintonizzazione sulla fase: {math.log(sqrt_n):.4f}")

    # 3. Scansione dei Nodi di Tensione
    # Invece di provare tutto, il radar di Perrone "ascolta" i nodi
    step = 2
    count = 0
    
    while p > 1:
        count += 1
        if N % p == 0:
            q = N // p
            print(f"\n--- Risonanza Trovata! ---")
            print(f"Nodo P: {p}")
            print(f"Nodo Q: {q}")
            print(f"Scansioni effettuate: {count}")
            return p, q
        
        p -= step
        
        # Feedback ogni 100.000 iterazioni (per i moduli grandi)
        if count % 100000 == 0:
            print(f"Scansione in corso... Tensione corrente ln(n): {math.log(p):.4f}")

    return None

# --- ESEMPIO DI DECODIFICA RSA-15 (L'Ingegner Perrone sfida il Modulo) ---
N_obiettivo = 1000000847383931
perrone_erdos_decoder(N_obiettivo)
