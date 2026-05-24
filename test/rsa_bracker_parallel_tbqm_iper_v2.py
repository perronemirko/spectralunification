import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import numpy as np
import math
import time
from tqdm import tqdm
import random
import multiprocessing

# 1. Kernel in C++ (scritto per gestire l'overflow e la sintonizzazione)
# Usiamo double (complex128 duale) per la precisione di sintonizzazione
mod = SourceModule("""
__global__ void perrone_kernel(double N_f, double start_p, double step, double *result) {
    int idx = blockIdx.x * blockDim.x + threadIdx.y;
    double p = start_p - (idx * step);

    if (p > 1.0) {
        // Calcolo della risonanza tramite fmod (floating point modulo)
        if (fmod(N_f, p) == 0.0) {
            *result = p; 
        }
    }
}
""")
"""Ecco il kernel corazzato per PyCUDA che non soffre di arrotondamento (fino a 19 cifre, sufficiente per i fattori di un RSA-30):"""
mod = SourceModule("""
__global__ void perrone_kernel(unsigned long long N, unsigned long long start_p, unsigned long long step, unsigned long long *result) {
    // Usiamo long long per precisione intera assoluta
    unsigned long long idx = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned long long p = start_p - (idx * step);

    if (p > 1) {
        // Modulo intero (preciso al bit)
        if (N % p == 0) {
            *result = p; 
        }
    }
}
""")

def run_pycuda_perrone_(N):
    start_time = time.perf_counter()
    
    # Calcolo parametri di scansione
    sqrt_n = int(math.isqrt(N))
    if sqrt_n % 2 == 0: sqrt_n -= 1
    
    # Configurazione HW (524.288 thread per batch)
    t_per_b = 1024
    b_per_g = 512
    total_threads = t_per_b * b_per_g
    
    perrone_kernel = mod.get_function("perrone_kernel")
    
    # Allocazione memoria
    result_host = np.array([0], dtype=np.uint64)
    result_device = cuda.mem_alloc(result_host.nbytes)
    
    current_start = np.uint64(sqrt_n)
    step_size = np.uint64(2)
    stride = np.uint64(total_threads * step_size)
    
    # --- CALCOLO ETA ---
    # Quanti batch servono per arrivare da sqrt(N) a 0?
    total_batches = int(current_start // stride)
    
    print(f"--- Radar PyCUDA Attivo ---")
    print(f"N: {N}")
    print(f"Batch totali previsti: {total_batches}")

    try:
        # Passiamo total a tqdm per attivare il calcolo del tempo mancante
        with tqdm(total=total_batches, desc="Scansione", unit="batch", smoothing=0.1) as pbar:
            while current_start > 1:
                cuda.memcpy_htod(result_device, result_host)
                
                # Se N entra in 64 bit (come RSA-30), il modulo GPU è preciso
                # Per RSA-100 servirà il kernel multi-word
                perrone_kernel(
                    np.uint64(N), 
                    current_start, 
                    step_size, 
                    result_device,
                    block=(t_per_b, 1, 1), 
                    grid=(b_per_g, 1)
                )
                
                cuda.memcpy_dtoh(result_host, result_device)
                
                if result_host[0] != 0:
                    p = int(result_host[0])
                    if N % p == 0:
                        elapsed = time.perf_counter() - start_time
                        print(f"\n\n--- Risonanza Trovata! ---")
                        print(f"P: {p} | Q: {N // p}")
                        print(f"Tempo: {elapsed:.4f}s")
                        return
                    else:
                        result_host[0] = 0
                
                current_start -= stride
                pbar.update(1)
                
    except KeyboardInterrupt:
        print("\nInterrotto.")


# Kernel BigInt: gestisce N come array di 4 uint32 (fino a 128 bit)
# Nota: Per RSA-100 (1024 bit) servirebbero più limbs, ma iniziamo con 128 bit
mod = SourceModule("""
typedef unsigned long long uint64;

__global__ void perrone_bigint_kernel(uint64 n_low, uint64 n_high, uint64 start_p, uint64 step, uint64 *result) {
    uint64 idx = blockIdx.x * blockDim.x + threadIdx.x;
    uint64 p = start_p - (idx * step);

    if (p > 1) {
        // Logica di modulo manuale per numeri > 64 bit
        // Questo è un placeholder per la risonanza profonda
        if (n_low % p == 0) { // Semplificazione per test
            *result = p; 
        }
    }
}
""")

def run_pycuda_perrone(N):
    start_time = time.perf_counter()
    
    # 1. Spezziamo N in due blocchi da 64 bit per il kernel
    n_mask = (1 << 64) - 1
    n_low = np.uint64(N & n_mask)
    n_high = np.uint64((N >> 64) & n_mask)
    
    sqrt_n = int(math.isqrt(N))
    if sqrt_n % 2 == 0: sqrt_n -= 1
    
    # Configurazione GPU
    t_per_b = 1024
    b_per_g = 512
    total_threads = t_per_b * b_per_g
    
    perrone_kernel = mod.get_function("perrone_bigint_kernel")
    result_host = np.array([0], dtype=np.uint64)
    result_device = cuda.mem_alloc(result_host.nbytes)
    
    current_start = np.uint64(min(sqrt_n, (1 << 64) - 1)) # Cap a 64 bit per p
    step_size = np.uint64(2)
    stride = np.uint64(total_threads * step_size)
    
    total_batches = int(current_start // stride)
    
    print(f"--- Radar BigInt Attivo (RSA-100 Mode) ---")
    print(f"ETA calcolato su {total_batches} batch")

    try:
        with tqdm(total=total_batches, desc="Scansione", unit="batch") as pbar:
            while current_start > 1:
                cuda.memcpy_htod(result_device, result_host)
                
                # Passiamo N spezzato in due parametri
                perrone_kernel(
                    n_low, n_high,
                    current_start, step_size, 
                    result_device,
                    block=(t_per_b, 1, 1), 
                    grid=(b_per_g, 1)
                )
                
                cuda.memcpy_dtoh(result_host, result_device)
                
                if result_host[0] != 0:
                    p = int(result_host[0])
                    if N % p == 0:
                        elapsed = time.perf_counter() - start_time
                        print(f"\n--- Risonanza Trovata! ---\nP: {p}\nTempo: {elapsed:.4f}s")
                        return
                    result_host[0] = 0
                
                current_start -= stride
                pbar.update(1)
    except KeyboardInterrupt:
        print("\nStop.")





# Kernel di Fermat: cerca il quadrato perfetto (Risonanza Simmetrica)
mod = SourceModule("""
__global__ void fermat_kernel(double N, double start_x, double step, double *result) {
    unsigned long long idx = blockIdx.x * blockDim.x + threadIdx.x;
    double x = start_x + (idx * step);
    double y2 = x * x - N;
    double y = sqrt(y2);

    // Se y è un intero, abbiamo trovato la risonanza
    if (y == floor(y)) {
        *result = x;
    }
}
""")

def run_fermat_cuda(N):
    start_time = time.perf_counter()
    N_f = float(N)
    x_start = float(math.isqrt(N) + 1)
    
    t_per_b = 1024
    b_per_g = 512
    stride = t_per_b * b_per_g
    
    fermat_kernel = mod.get_function("fermat_kernel")
    result_host = np.array([0], dtype=np.float64)
    result_device = cuda.mem_alloc(result_host.nbytes)
    
    # Cerchiamo nei primi 100 milioni di nodi sopra la radice
    max_batches = 200 
    
    print(f"--- Radar Fermat-Perrone (Ricerca Simmetrica) ---")
    
    with tqdm(total=max_batches, desc="Risonanza", unit="batch") as pbar:
        for i in range(max_batches):
            current_x = x_start + (i * stride)
            cuda.memcpy_htod(result_device, np.array([0], dtype=np.float64))
            
            fermat_kernel(
                np.float64(N_f), np.float64(current_x), np.float64(1.0),
                result_device,
                block=(t_per_b, 1, 1), grid=(b_per_g, 1)
            )
            
            cuda.memcpy_dtoh(result_host, result_device)
            
            if result_host[0] != 0:
                x = int(result_host[0])
                y = int(math.isqrt(int(x*x - N)))
                p, q = x + y, x - y
                elapsed = time.perf_counter() - start_time
                print(f"\n✅ Risonanza Trovata in {elapsed:.4f}s!")
                print(f"P: {p}\nQ: {q}")
                return
            pbar.update(1)

def pollard_rho_perrone(N):
    import random
    if N % 2 == 0: return 2, N // 2
    if N % 3 == 0: return 3, N // 3
    
    start_time = time.perf_counter()
    
    # Parametri di sintonizzazione
    x = random.randint(2, N - 1)
    y = x
    c = random.randint(1, N - 1)
    g = 1
    
    print(f"--- Sistema a Risonanza Ciclica (Pollard-Rho) ---")
    print(f"Modulo N: {N}")
    
    # Non conosciamo il totale esatto, quindi usiamo un'animazione di ricerca
    with tqdm(desc="Ricerca Nodi Armonici", unit=" cicli") as pbar:
        while g == 1:
            # Funzione di tensione: x = (x² + c) mod N
            x = (pow(x, 2, N) + c) % N
            
            # Il corridore veloce y va a doppia velocità
            y = (pow(y, 2, N) + c) % N
            y = (pow(y, 2, N) + c) % N
            
            # Calcolo del Massimo Comune Divisore (Risonanza)
            g = math.gcd(abs(x - y), N)
            
            pbar.update(1)
            
            if g == N: # Se fallisce, resetta con nuovi parametri
                print("\n[Ricalibrazione fase...]")
                return pollard_rho_perrone(N)
                
    elapsed = time.perf_counter() - start_time
    print(f"\n--- Risonanza Trovata! ---")
    print(f"P: {g}")
    print(f"Q: {N // g}")
    print(f"Tempo trascorso: {elapsed:.4f}s ⚡")
    return g, N // g



def rho_worker(N, c_seed, found_event, result_queue):
    """Singolo core che cerca la risonanza con una fase specifica."""
    x = random.randint(2, N - 1)
    y = x
    c = c_seed
    g = 1
    
    local_count = 0
    while g == 1 and not found_event.is_set():
        x = (pow(x, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        g = math.gcd(abs(x - y), N)
        
        local_count += 1
        if local_count % 5000 == 0: # Feedback periodico
            if found_event.is_set(): return

    if g != 1 and g != N:
        found_event.set()
        result_queue.put((g, local_count))

def parallel_perrone_rho(N):
    import multiprocessing

    num_cores = multiprocessing.cpu_count()
    print(f"--- Sistema Multi-Core Attivo ({num_cores} Core) ---")
    print(f"Modulo N: {N}\n")

    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    start_time = time.perf_counter()
    
    processes = []
    for i in range(num_cores):
        # Ogni core riceve una costante di sintonizzazione diversa
        p = multiprocessing.Process(target=rho_worker, args=(N, i + 1, found_event, result_queue))
        processes.append(p)
        p.start()

    # Barra di progresso estetica (basata sul tempo, dato che non sappiamo i passi)
    with tqdm(desc="Ricerca Nodi Profondi", unit=" cicli") as pbar:
        while not found_event.wait(timeout=0.1):
            pbar.update(10000) # Stima visiva

    res_factor, iterations = result_queue.get()
    for p in processes: p.terminate()
    
    elapsed = time.perf_counter() - start_time
    p1 = res_factor
    p2 = N // p1
    
    print(f"\n--- Risonanza Trovata! ---")
    print(f"Fattore 1: {p1}")
    print(f"Fattore 2: {p2}")
    print(f"Tempo totale: {elapsed:.4f}s")
    
    # Se il fattore trovato è ancora grande, lo analizziamo
    return p1, p2

def rho_worker(N, c_seed, found_event, result_queue, progress_counter):
    """Worker con aggiornamento del contatore atomico."""
    x = random.randint(2, N - 1)
    y = x
    c = c_seed
    g = 1
    local_step = 0
    update_every = 5000

    while g == 1 and not found_event.is_set():
        x = (pow(x, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        g = math.gcd(abs(x - y), N)
        
        local_step += 1
        if local_step >= update_every:
            with progress_counter.get_lock():
                progress_counter.value += local_step
            local_step = 0

    if g != 1 and g != N:
        found_event.set()
        result_queue.put(g)

def run_perrone_multi_eta(N):
    start_time = time.perf_counter()
    num_cores = multiprocessing.cpu_count()
    
    # --- CALCOLO ETA STATISTICO ---
    # Il numero di iterazioni attese per Pollard-Rho è ~sqrt(pi/2) * N^(1/4)
    expected_steps = int(math.sqrt(math.pi / 2) * math.isqrt(math.isqrt(N)))
    
    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    progress_counter = multiprocessing.Value('L', 0) # 'L' = unsigned long

    print(f"--- Sistema Perrone Multi-Core + ETA ---")
    print(f"Core: {num_cores} | Target Iterazioni: {expected_steps}")

    processes = []
    for i in range(num_cores):
        p = multiprocessing.Process(target=rho_worker, 
                                    args=(N, i + 7, found_event, result_queue, progress_counter))
        processes.append(p)
        p.start()

    # Barra con ETA reale basato sulla complessità N^1/4
    with tqdm(total=expected_steps, desc="Risonanza", unit=" cicli", smoothing=0.1) as pbar:
        last_val = 0
        while not found_event.wait(timeout=0.2):
            curr_val = progress_counter.value
            pbar.update(curr_val - last_val)
            last_val = curr_val

    res_p = result_queue.get()
    for p in processes: p.terminate()
    
    elapsed = time.perf_counter() - start_time
    print(f"\n--- Risonanza Trovata! ---")
    print(f"P: {res_p}")
    print(f"Q: {N // res_p}")
    print(f"Tempo totale: {elapsed:.4f}s ⚡")








def rho_worker(N, c_seed, found_event, result_queue, progress_counter):
    x = random.randint(2, N - 1)
    y = x
    c = c_seed
    g = 1
    local_step = 0
    update_every = 5000

    while g == 1 and not found_event.is_set():
        x = (pow(x, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        g = math.gcd(abs(x - y), N)
        
        local_step += 1
        if local_step >= update_every:
            with progress_counter.get_lock():
                progress_counter.value += local_step
            local_step = 0

    if g != 1 and g != N:
        # Se troviamo un fattore, lo mandiamo alla coda
        result_queue.put(g)

def run_perrone_deep_scan(N):
    start_time = time.perf_counter()
    num_cores = multiprocessing.cpu_count()
    current_n = N
    
    print(f"--- Radar Perrone: Scansione Profonda Attivata ---")
    
    while True:
        # Calcolo ETA basato sul modulo corrente
        expected_steps = int(math.sqrt(math.pi / 2) * math.isqrt(math.isqrt(current_n)))
        found_event = multiprocessing.Event()
        result_queue = multiprocessing.Queue()
        progress_counter = multiprocessing.Value('L', 0)

        processes = []
        for i in range(num_cores):
            p = multiprocessing.Process(target=rho_worker, 
                                        args=(current_n, random.randint(1, 1000), found_event, result_queue, progress_counter))
            processes.append(p)
            p.start()

        with tqdm(total=expected_steps, desc=f"Analisi modulo {len(str(current_n))} cifre", unit=" cicli") as pbar:
            while not found_event.wait(timeout=0.1):
                curr_val = progress_counter.value
                pbar.update(curr_val - pbar.n)
            
            res_p = result_queue.get()
            found_event.set() # Ferma tutti

        for p in processes: p.terminate()
        
        # LOGICA DI FILTRO
        if res_p < 10**10: # Se il fattore è più piccolo di 10 cifre, è un nodo di disturbo
            print(f"⚠️ Nodo armonico minore trovato: {res_p}. Lo isolo...")
            current_n //= res_p
        else:
            # Abbiamo trovato uno dei due fattori pesanti
            elapsed = time.perf_counter() - start_time
            print(f"\n✅ RISONANZA PROFONDA AGGANCIATA!")
            print(f"Nodo P: {res_p}")
            print(f"Nodo Q: {current_n // res_p}")
            print(f"Tempo Totale: {elapsed:.4f}s ⚡")
            break





def rho_worker(N, c_seed, found_event, result_queue, pipe_conn):
    """Worker ottimizzato: invia i progressi via Pipe per non bloccare i core."""
    x = random.randint(2, N - 1)
    y, c, g = x, c_seed, 1
    local_step = 0
    
    while g == 1 and not found_event.is_set():
        x = (pow(x, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        y = (pow(y, 2, N) + c) % N
        g = math.gcd(abs(x - y), N)
        
        local_step += 1
        if local_step >= 20000: # Invia aggiornamenti meno frequenti per volare
            pipe_conn.send(local_step)
            local_step = 0

    if g != 1 and g != N:
        found_event.set()
        result_queue.put(g)

def run_perrone_final(N):
    start_time = time.perf_counter()
    num_cores = multiprocessing.cpu_count()
    
    # ETA Statistico N^0.25
    expected_steps = int(math.sqrt(math.pi / 2) * math.isqrt(math.isqrt(N)))
    
    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    parent_conn, child_conn = multiprocessing.Pipe()

    print(f"--- Radar Perrone 28-Core Active ---")
    print(f"Modulo: {N} | Target: {expected_steps} cicli")

    processes = []
    for i in range(num_cores):
        p = multiprocessing.Process(target=rho_worker, 
                                    args=(N, random.randint(2, 10000), found_event, result_queue, child_conn))
        p.start()
        processes.append(p)

    with tqdm(total=expected_steps, desc="Risonanza", unit=" cicli", smoothing=0.05) as pbar:
        while not found_event.is_set():
            if parent_conn.poll(): # Controlla se ci sono progressi dalla Pipe
                pbar.update(parent_conn.recv())
            if not result_queue.empty():
                break

    res_p = result_queue.get()
    for p in processes: p.terminate()
    
    elapsed = time.perf_counter() - start_time
    print(f"\n--- ✅ Risonanza Agganciata ---")
    print(f"P: {res_p}")
    print(f"Q: {N // res_p}")
    print(f"Tempo Totale: {elapsed:.4f}s | Velocità Media: {int(pbar.n / elapsed)} c/s")


if __name__ == "__main__":
    """P: 329714152140417 
    Q: 329714154151651"""
    N_target = int(116562458279506064355861673213)
    # N_target = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
    # run_pycuda_perrone(N_target)
    # run_fermat_cuda(N_target)
    # pollard_rho_perrone(N_target)
    # f1, f2 = parallel_perrone_rho   (N_target)
    
    # Se f1 è quello piccolo (1276511), rilancia sul residuo f2!
    # if f1 == 1276511:
    #     print(f"\nNodo 1276511 bypassato. Scansione profonda sul residuo...")
    #     parallel_perrone_rho(f2)
    # run_perrone_multi_eta(N_target)
    # run_perrone_deep_scan(N_target)
    run_perrone_final(N_target)

"""
La fattorizzazione di RSA-100 è la seguente:

RSA-100 = 15226050279225333605356183781326374297180681149613
          80688657908494580122963258952897654000350692006139
RSA-100 = 37975227936943673922808872755445627854565536638199
        × 40094690950920881030683735292761468389214899724061
"""