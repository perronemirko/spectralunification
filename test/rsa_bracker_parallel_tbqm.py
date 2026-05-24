import math
import multiprocessing
from tqdm import tqdm

def check_range_tqdm(N, start_p, end_p, step, found_event, result_queue, progress_counter):
    """Worker con aggiornamento del contatore globale."""
    p = start_p
    local_count = 0
    update_interval = 1000  # Aggiorna la barra ogni 1000 iterazioni per non rallentare
    
    while p >= end_p and not found_event.is_set():
        if N % p == 0:
            q = N // p
            found_event.set()
            result_queue.put((p, q))
            return
        
        p -= step
        local_count += 1
        
        if local_count >= update_interval:
            progress_counter.value += local_count
            local_count = 0

def parallel_perrone_tqdm(N, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    sqrt_n = int(math.isqrt(N))
    if sqrt_n % 2 == 0: sqrt_n -= 1
    
    # Range totale di numeri dispari da controllare
    total_to_check = (sqrt_n // 2)
    chunk_size = (sqrt_n // num_workers)
    if chunk_size % 2 != 0: chunk_size += 1

    # Risorse condivise
    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    progress_counter = multiprocessing.Value('i', 0) # 'i' sta per integer

    processes = []
    for i in range(num_workers):
        start_p = sqrt_n - (i * chunk_size)
        end_p = max(3, start_p - chunk_size + 2)
        p = multiprocessing.Process(
            target=check_range_tqdm, 
            args=(N, start_p, end_p, 2, found_event, result_queue, progress_counter)
        )
        processes.append(p)
        p.start()

    # Gestione della barra di avanzamento nel thread principale
    with tqdm(total=total_to_check, desc="Scansione Nodi Perrone", unit="nodi") as pbar:
        last_val = 0
        while not found_event.wait(timeout=0.1):
            current_val = progress_counter.value
            pbar.update(current_val - last_val)
            last_val = current_val
        
        # Aggiornamento finale
        pbar.update(total_to_check - last_val)

    res = result_queue.get()
    for p in processes: p.terminate()
    
    print(f"\n--- Risonanza Trovata! ---")
    print(f"P: {res[0]}\nQ: {res[1]}")
    return res

if __name__ == "__main__":
    # N obiettivo (RSA-15 ridotto o simile per test)
    N_obiettivo = 15226050279225333605356183781326374297180681149613
    parallel_perrone_tqdm(N_obiettivo)
