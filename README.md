# ResourceScheduling_DeepStack
## Description
Ce projet propose l’implémentation d’un **Scheduler 5G adaptif** basé sur l’approche **DeepStack**. DeepStack a été initialement conçu pour résoudre des problèmes décisionnels dans des environnements complexes et partiellement observables, comme le Heads-Up No-Limit Poker, un jeu à information incomplète.
L’objectif est de démontrer la pertinence de DeepStack dans le domaine des télécommunications, en l’appliquant à un problème concret : la **planification dynamique des ressources dans les réseaux 5G (Resource Scheduling)**.


## 📁 Arborescence du projet
```
.
└── src/
    ├── Prediction.py              # Module de prédiction (DeepStack)
    ├── checks.py                  # Testing
    ├── estimator_functions.py     # Fonctions d’estimation
    ├── helpers.py                 # Fonctions utilitaires
    ├── kpi_formula.py             # Calcul de KPI
    ├── main.py                    # Script principal
    ├── plot_selon_k.py            # Visualisation 
    ├── plot_selon_max_ues.py      # Visualisation 
    ├── state.py                   # Classe : Représentation de l’état du système
    └── ue.py                      # Classe : Modélisation des utilisateurs (UE)
```
## 🛠️ Dépendances
Pour exécuter ce projet, assurez-vous d’avoir les bibliothèques Python suivantes installées :
- Python ≥ 3.8
- Bibliothèques : numpy, matplotlib, scipy.

## Author : 
Melek FENDRI: melek.fendri@epfl.ch


