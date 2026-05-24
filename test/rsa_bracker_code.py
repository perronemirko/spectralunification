import math
import torch
from tqdm import tqdm


def perrone_erdos_decoder_torch(N: int):
    beta_r = 1.6366
    beta   = torch.tensor(beta_r + 0j, dtype=torch.complex128)

    sqrt_n_int = math.isqrt(N)
    sqrt_n_t   = torch.tensor(
        float(sqrt_n_int) + math.log(sqrt_n_int) * 1j,
        dtype=torch.complex128,
    )

    p_int   = sqrt_n_int - (1 if sqrt_n_int % 2 == 0 else 0)
    p_t     = torch.tensor(float(p_int) + math.log(max(p_int, 1)) * 1j,
                           dtype=torch.complex128)
    beta_sq = beta ** 2

    print("--- Sistema Perrone-Torch in funzione ---")
    print(f"Modulo N     : {N}")
    print(f"sqrt(N) int  : {sqrt_n_int}")
    print(f"sqrt_n tensor: {sqrt_n_t}")
    print(f"beta tensor  : {beta}  | beta² = {beta_sq.real:.6f}")
    print(f"Fase iniziale: {sqrt_n_t.imag:.6f} (im = ln(sqrt_n))")

    count_t = torch.tensor(0.0 + 0j, dtype=torch.complex128)

    # total = numero di candidati dispari da sqrt_n fino a 3
    total = (p_int - 3) // 2 + 1

    with tqdm(
        total=total,
        desc="Scansione nodi",
        unit=" nodi",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] ln(p)={postfix}",
    ) as pbar:

        while p_int > 1:
            count_t += 1

            if N % p_int == 0:
                q_int = N // p_int

                p_out = torch.tensor(float(p_int) + math.log(p_int) * 1j,
                                     dtype=torch.complex128)
                q_out = torch.tensor(float(q_int) + math.log(q_int) * 1j,
                                     dtype=torch.complex128)

                resonance = p_out * q_out
                ratio     = p_out / q_out

                pbar.set_postfix_str(f"{p_out.imag:.4f}")
                pbar.update(1)

                print("\n--- Risonanza Trovata! ---")
                print(f"Nodo P (int)    : {p_int}")
                print(f"Nodo Q (int)    : {q_int}")
                print(f"p tensor c128   : {p_out}")
                print(f"q tensor c128   : {q_out}")
                print(f"p*q (resonanza) : {resonance}")
                print(f"|resonance|     : {resonance.abs():.6f}")
                print(f"p/q (simmetria) : {ratio}")
                print(f"Scansioni       : {count_t.real:.0f}")
                return (p_int, q_int), (p_out, q_out)

            p_int -= 2
            p_t = torch.tensor(
                float(p_int) + (math.log(p_int) if p_int > 0 else 0.0) * 1j,
                dtype=torch.complex128,
            )

            # aggiorna postfix ogni 10k per non strangolare il loop
            if int(count_t.real) % 10_000 == 0:
                pbar.set_postfix_str(f"{p_t.imag:.4f}")

            pbar.update(1)

    return None


N_obiettivo = (
    37975227936943673922808872755445627854565536638199
    * 40094690950920881030683735292761468389214899724061
)
result = perrone_erdos_decoder_torch(N_obiettivo)