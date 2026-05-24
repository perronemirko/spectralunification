import os
import subprocess
import sys

# =========================
# CUDA / NUMBA HARD RESET
# =========================

print("=== CUDA TOTAL FIX START ===")

# 🔥 forza RTX 4090
os.environ["NUMBA_CUDA_DEFAULT_PTX_CC"] = "8.9"

# 🔥 elimina cache
os.environ["NUMBA_DISABLE_CACHING"] = "1"

# 🔥 forza CUDA 12.8
os.environ["CUDA_HOME"] = "/usr/local/cuda-12.8"
os.environ["PATH"] = os.environ["CUDA_HOME"] + "/bin:" + os.environ["PATH"]
os.environ["LD_LIBRARY_PATH"] = (
    "/usr/local/cuda-12.8/lib64:"
    "/usr/local/cuda-12.8/targets/x86_64-linux/lib"
)

# 🔥 pulizia variabili rotte
for k in [
    "NUMBA_CUDA_PTX_MAX_VER",
    "NUMBA_CUDA_PTX_LIMIT",
    "NUMBA_CUDA_DRIVER"
]:
    os.environ.pop(k, None)

print("Environment fixed")


# =========================
# CLEAN NUMBA CACHE
# =========================
print("Cleaning Numba cache...")

subprocess.run(["rm", "-rf", os.path.expanduser("~/.numba")])
subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/numba")])

print("Cache cleaned")


# =========================
# IMPORT CUDA AFTER FIX
# =========================
from numba import cuda
import math
import numpy as np
from tqdm import tqdm

cuda.close()


# =========================
# KERNEL STABLE VERSION
# =========================
@cuda.jit
def kernel(N_f, start_p_f, step_f, result, found):
    idx = cuda.grid(1)

    if found[0] == 1:
        return

    p = start_p_f - (idx * step_f)

    if p > 1.0:

        q = N_f / p
        r = q - math.floor(q)

        if r < 1e-12 or r > 1.0 - 1e-12:
            cuda.atomic.exch(found, 0, 1)
            result[0] = p


# =========================
# MAIN FUNCTION
# =========================
def run(N):

    N_f = np.float64(N)

    sqrt_n = int(math.isqrt(N))
    if sqrt_n % 2 == 0:
        sqrt_n -= 1

    threads = 256
    blocks = 256

    result = cuda.to_device(np.zeros(1, dtype=np.float64))
    found = cuda.to_device(np.zeros(1, dtype=np.int32))

    step = np.float64(2.0)
    stride = np.float64(threads * blocks * step)

    current = np.float64(sqrt_n)

    print("=== RUN START ===")

    with tqdm(desc="GPU scan") as pbar:

        while current > 1.0:

            kernel[blocks, threads](
                N_f,
                current,
                step,
                result,
                found
            )

            if found.copy_to_host()[0] == 1:
                p = int(result.copy_to_host()[0])

                if N % p == 0:
                    print("\nFOUND FACTOR!")
                    print("P =", p)
                    print("Q =", N // p)
                    return

                result = cuda.to_device(np.zeros(1, dtype=np.float64))
                found = cuda.to_device(np.zeros(1, dtype=np.int32))

            current -= stride
            pbar.update(1)

    print("NOT FOUND")
    return False


if __name__ == "__main__":
    N_target = 15226050279225333605356183781326374297180681149613
    run(N_target)


"""
La fattorizzazione di RSA-100 è la seguente:

RSA-100 = 15226050279225333605356183781326374297180681149613
          80688657908494580122963258952897654000350692006139
RSA-100 = 37975227936943673922808872755445627854565536638199
        × 40094690950920881030683735292761468389214899724061
"""