import matplotlib.pyplot as plt
from main import run_simulation
import numpy as np
  # Optionnel : juste pour barre de progression


K_values = [1, 5, 10, 15 , 20 ]
N_runs = 100            # 100 runs par valeur de K

results = []

for K in K_values :
    run_ratios = []
    for i in range(N_runs):
        # Important : seed aléatoire pour chaque run pour obtenir une moyenne réaliste
        ratio = run_simulation(NB_SLOTS= 25, MAX_UES=20, TOTAL_RBS=25, K=K, MU_arrive=3, A=1.5, T_arrive_period=10, MU_depart=0.5, A_depart=1, T_depart_period=20, SEED=42, verbose=False, BMAX=2, OFFSET=3 )
        run_ratios.append(ratio)
    moyenne = np.mean(run_ratios)
    results.append(moyenne)

plt.figure(figsize=(8, 5))
plt.plot(list(K_values), results, marker='o')
plt.xlabel("K")
plt.ylabel("Mean load_ratio_moy (100 runs)")
plt.title("Impact of K on average load ratio (100 simulations per K)")
plt.ylim(0, 1)
plt.grid(True)
plt.show()


