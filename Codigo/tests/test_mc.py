import time
import sys

sys.path.append('..')
from opcion_europea_mc import opcion_europea_mc, opcion_europea_mc_fv

pasos = 1000000
t1 = time.time()
c1 = opcion_europea_mc('C', 100, 100, 1, 0.02, 0.3, 0.01, pasos)
p1 = opcion_europea_mc('P', 100, 100, 1, 0.02, 0.3, 0.01, pasos)
print(f"time {time.time() - t1}")

t1 = time.time()
c2 = opcion_europea_mc_fv('C', 100, 100, 1, 0.02, 0.3, 0.01, pasos)
p2 = opcion_europea_mc_fv('P', 100, 100, 1, 0.02, 0.3, 0.01, pasos)
print(f"time {time.time() - t1}")


print(c1, p1, c2, p2)

