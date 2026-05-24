import math
import time
import multiprocessing
from tqdm import tqdm

def perrone_worker(N, start_p, end_p, step, found_event, result_queue, child_conn):
    """Segue fedelmente l'algoritmo di Perrone: scansione lineare decrescente."""
    p = start_p
    local_count = 0
    # Sintonizzazione sulla tensione di Erdos
    while p >= end_p and not found_event.is_set():
        if N % p == 0:
            q = N // p
            found_event.set()
            result_queue.put((p, q))
            return
        
        p -= step
        local_count += 1
        
        # Aggiorna la barra ogni 50.000 nodi per non rallentare i core
        if local_count >= 50000:
            child_conn.send(local_count)
            local_count = 0

def run_perrone_original_parallel(N):
    start_time = time.perf_counter()
    num_cores = multiprocessing.cpu_count()
    
    # 1. Puntamento: Centro di gravità (Radice Quadrata)
    sqrt_n = int(math.isqrt(N))
    if sqrt_n % 2 == 0: sqrt_n -= 1
    
    # 2. Suddivisione dell'intervallo per i 28 core
    # Scansioniamo dalla radice in giù. Definiamo un range di ricerca ragionevole.
    search_limit = sqrt_n  # Scansione totale fino a 3
    chunk_size = (search_limit // num_cores)
    if chunk_size % 2 != 0: chunk_size += 1
    
    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    parent_conn, child_conn = multiprocessing.Pipe()

    print(f"--- Radar Perrone Originale (Lineare) ---")
    print(f"Core attivi: {num_cores} | Puntamento iniziale: {sqrt_n}")

    processes = []
    for i in range(num_cores):
        # Ogni core prende un segmento diverso sotto la radice
        core_start = sqrt_n - (i * chunk_size)
        core_end = max(3, core_start - chunk_size + 2)
        
        p = multiprocessing.Process(target=perrone_worker, 
                                    args=(N, core_start, core_end, 2, found_event, result_queue, child_conn))
        p.start()
        processes.append(p)

    # 3. ETA basato sulla scansione lineare
    total_steps_to_zero = sqrt_n // 2
    with tqdm(total=total_steps_to_zero, desc="Scansione Erdos", unit="nodi") as pbar:
        while not found_event.is_set():
            if parent_conn.poll():
                pbar.update(parent_conn.recv())
            if not result_queue.empty():
                break
            time.sleep(0.1)

    res = result_queue.get()
    for p in processes: p.terminate()
    
    elapsed = time.perf_counter() - start_time
    print(f"\n--- 🎯 Risonanza Trovata (Metodo Perrone) ---")
    print(f"P: {res[0]}")
    print(f"Q: {res[1]}")
    print(f"Tempo: {elapsed:.4f}s")

if __name__ == "__main__":
    # Test RSA-30 con i fattori vicini alla radice
    N_target = 108711422784795325878486022807
    run_perrone_original_parallel(N_target)
