import matplotlib.pyplot as plt
from main import run_simulation
import numpy as np
  # Optionnel : juste pour barre de progression


MAX_UES_values = [ 10 , 15 ,20 , 25  ]
N_runs = 100            # 100 runs par valeur de K

results = []

for  MAX_UES in  MAX_UES_values :
    run_ratios = []
    for i in range(N_runs):
        # Important : seed aléatoire pour chaque run pour obtenir une moyenne réaliste
        ratio = run_simulation(NB_SLOTS=100 , MAX_UES= MAX_UES, TOTAL_RBS=25, K=20, MU_arrive=3, A=1.5, T_arrive_period=10, MU_depart=0.5, A_depart=1, T_depart_period=20, SEED=42, verbose=False, BMAX=2, OFFSET=3 )
        print(f" ratio = {ratio}")
        run_ratios.append(ratio)
    moyenne = np.mean(run_ratios)
    results.append(moyenne)

plt.figure(figsize=(8, 5))
plt.plot(list( MAX_UES_values), results, marker='o')
plt.xlabel("MAX_UES toleré dans le systeme")
plt.ylabel("nb de fois Load_ratio depasse 1  (100 runs)")
plt.title(" Non respect Load_ratio selon MAX_UES toleré dans le systeme ")
plt.ylim(0, 10)
plt.grid(True)
plt.show()