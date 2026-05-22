#!/usr/bin/env python3
"""
generate_zeros.py — Genera gli zeri non-triviali della funzione zeta di Riemann.

Usa mpmath.zetazero(n) per calcolare la parte immaginaria del n-esimo zero.
Salva progressivamente su file, riprendibile se interrotto.

Uso:
    python generate_zeros.py --count 10000 --output zeri_1M.txt --precision 15
"""

import argparse
import os
import time
import mpmath


def generate_zeros(count: int, output: str, precision: int, resume: bool) -> None:
    mpmath.mp.dps = precision

    # Trova quanti ne abbiamo già se il file esiste
    start_idx = 1
    if resume and os.path.exists(output):
        with open(output, "r") as f:
            existing = [l.strip() for l in f if l.strip()]
        start_idx = len(existing) + 1
        print(f"[resume] Trovati {len(existing)} zeri esistenti, riparto da #{start_idx}")
    elif os.path.exists(output) and not resume:
        os.remove(output)

    if start_idx > count:
        print(f"[ok] Già {start_idx-1} zeri presenti, niente da fare.")
        return

    total_to_compute = count - start_idx + 1
    print(f"[*] Generazione zeri #{start_idx} → #{count} ({total_to_compute} zeri)")
    print(f"[*] Precisione: {precision} cifre decimali")
    print(f"[*] Output: {output}")
    print()

    t_start = time.time()
    checkpoint = 100  # salva ogni N zeri

    with open(output, "a") as f:
        for n in range(start_idx, count + 1):
            gamma = float(mpmath.im(mpmath.zetazero(n)))
            f.write(f"{gamma:.{precision}f}\n")

            if n % checkpoint == 0:
                elapsed = time.time() - t_start
                computed = n - start_idx + 1
                rate = computed / elapsed
                remaining = (count - n) / rate if rate > 0 else 0
                print(f"  [{n}/{count}] {rate:.1f} zeri/s | "
                      f"ETA: {remaining/60:.1f} min")
                f.flush()

    elapsed = time.time() - t_start
    print(f"\n[done] {count} zeri salvati in {elapsed:.1f}s ({output})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera zeri di Riemann con mpmath.")
    parser.add_argument("--count",     type=int, default=10000,       help="Numero di zeri (default: 10000)")
    parser.add_argument("--output",    type=str, default="zeri_1M.txt", help="File di output")
    parser.add_argument("--precision", type=int, default=15,           help="Cifre decimali (default: 15)")
    parser.add_argument("--resume",    action="store_true",            help="Riprendi se il file esiste già")
    args = parser.parse_args()

    generate_zeros(args.count, args.output, args.precision, args.resume)


if __name__ == "__main__":
    main()
