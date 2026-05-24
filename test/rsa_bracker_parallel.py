import math
import multiprocessing

def check_range(N, start_p, end_p, step, found_event, result_queue):
    """Funzione eseguita dai singoli worker."""
    p = start_p
    while p >= end_p and not found_event.is_set():
        if N % p == 0:
            q = N // p
            found_event.set()  # Ferma gli altri processi
            result_queue.put((p, q))
            return
        p -= step

def parallel_perrone_decoder(N, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    sqrt_n = int(math.isqrt(N))
    if sqrt_n % 2 == 0:
        sqrt_n -= 1
    
    # Definiamo l'ampiezza della ricerca per ogni processo
    # Nota: qui cerchiamo da sqrt(N) fino a 3
    search_range = sqrt_n - 3
    chunk_size = (search_range // num_workers)
    if chunk_size % 2 != 0: chunk_size += 1 # Mantieni allineamento dispari

    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    processes = []

    print(f"--- Sistema Perrone Multi-Core ---")
    print(f"Core attivati: {num_workers}")

    for i in range(num_workers):
        start_p = sqrt_n - (i * chunk_size)
        end_p = max(3, start_p - chunk_size + 2)
        
        # Ogni processo usa uno step di 2 per restare sui dispari
        p = multiprocessing.Process(target=check_range, 
                                    args=(N, start_p, end_p, 2, found_event, result_queue))
        processes.append(p)
        p.start()

    # Attendi il risultato
    res = result_queue.get()
    
    for p in processes:
        p.terminate() # Chiudi i processi rimasti
        
    print(f"\n--- Risonanza Trovata in parallelo! ---")
    print(f"P: {res[0]} | Q: {res[1]}")
    return res

if __name__ == "__main__":
    N_obiettivo = 15226050279225333605356183781326374297180681149613
    parallel_perrone_decoder(N_obiettivo)
