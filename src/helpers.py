import numpy as np

import time
import random
import math
import kpi_formula
import checkes
from ue import UE
import ue
import estimator_functions
from Prediction import update_buffer_size
import Prediction 
import matplotlib.pyplot as plt
#from scheduler import Scheduler
import state
from collections import defaultdict
import time


pass_nb = 0
# === Paramètres globaux ===
NB_SLOTS =200

MAX_UES = 20  # Nombre maximum d'UEs simultanément dans le système
SEED = 42
np.random.seed(SEED)
TOTAL_RBS = 25
MAX_ALLOC_PER_UE = 0
T_slot = 1
BMAX = 2
S =1 
OFFSET = 3
# === Parametres des modelisation d'arrivé et de depart 
MU_arrive= 3 # Moyenne d'arrivées d'UEs par slot
A = 1.5       # Amplitude des variations
T_arrive_period = 10  # Détermine la fréquence des cycles sinusoidaux
MU_depart = 0.5  # Moyenne des departs d'UEs par slot
A_depart = 1 # Amplitude des variations
T_depart_period = 20 # Détermine la fréquence des cycles sinusoidaux
# === Boucle principale ===
# Constants (you may need to define these based on your context)
alpha = 1
beta = 1
gamma = 1
#N = TOTAL_RBS # Example value for nb of RB possible to allocate
K = 20# Number of predictions


regret_bank_per_ue = defaultdict(lambda: np.zeros((TOTAL_RBS, K)))

def prioritize_ues(ue_list):
    priority_candidates = []
    non_priority_candidates = []

    # Séparation des UEs en deux groupes : prioritaires et non-prioritaires
    # Si delta slot initialisé alors --> dependament du P , Si delta slot None --> dependament du P-1
    for ue in ue_list:
        if ue.state.delta_slot is None :
            if ue.state.compteur == (ue.state.P - 1): # compteur : nb de fois d'affilé ou l'ue ne se voit pas allouer des rb 
                ue.is_priority = True
                priority_candidates.append(ue)
            else:
                ue.is_priority = False
                non_priority_candidates.append(ue)
        else: 
            if ue.state.compteur == ue.state.P: # compteur : nb de fois d'affilé ou l'ue ne se voit pas allouer des rb 
                ue.is_priority = True
                priority_candidates.append(ue)
            else:
                ue.is_priority = False
                non_priority_candidates.append(ue)
    # Tri dans chaque groupe : qos_latency (↑), buffer (↓)
    sorted_priority = sorted(priority_candidates, key=lambda u: (u.qos_latency, -u.buffer))
    sorted_non_priority = sorted(non_priority_candidates, key=lambda u: (u.qos_latency, -u.buffer))

    # Concaténation : priorité en tête
    return sorted_priority + sorted_non_priority

def handle_new_arrivals(ue_list, ue_counter, t, MU_arrive, A, T_arrive_period, MAX_UES):
    lambda_arrive_t = MU_arrive + A * np.sin(2 * np.pi * t / T_arrive_period)
    lambda_arrive_t = max(lambda_arrive_t, 0)
    new_ue_count = np.random.poisson(lambda_arrive_t)


    for _ in range(new_ue_count): 
        if len(ue_list) < MAX_UES: 
            initial_cqi = np.random.randint(0, 16)              # entier dans [0, 15]
            initial_buffer = np.random.uniform(0.0, 2 )        # reel entre  [0, 2]
            qos_latency = np.random.choice([ 5, 10, 50, 100, 150, 200, 300]) 
            qos_throughput = np.random.uniform(0.064, 10)
            new_ue = UE(ue_id=ue_counter, initial_cqi=initial_cqi, initial_buffer = initial_buffer, qos_latency=qos_latency, qos_throughput=qos_throughput)
            print(f"[NEW UE] id={new_ue.ue_id} | CQI={new_ue.cqi} | Buffer={new_ue.buffer} | qos_latency={new_ue.qos_latency} | qos_thoughput={new_ue.qos_throughput}")
            new_ue.state.P = estimator_functions.assign_periodicity(new_ue.qos_latency)
            new_ue.state.t_entry = t 
            ue_list.append(new_ue)
            ue_counter += 1
    return ue_counter


def handle_departures(ue_list, t, MU_depart, A_depart, T_depart_period):
    lambda_depart_t = MU_depart + A_depart * np.sin(2 * np.pi * t / T_depart_period)
    lambda_depart_t = max(lambda_depart_t, 0)
    nb_depart = np.random.poisson(lambda_depart_t)
    if len(ue_list) > 0:
        departing_ues = np.random.choice(ue_list, size=min(nb_depart, len(ue_list)-1), replace=False)
        for ue in departing_ues:
            print(f"Slot {t}: UE {ue.ue_id} quitte le système.")
            ue_list.remove(ue)


def update_max_alloc_per_ue(len_ue): 
    if len_ue == 1 :
        MAX_ALLOC_PER_UE = 25
    if len_ue== 2 :
        MAX_ALLOC_PER_UE = 13
    if len_ue >= 3 and len_ue <= 4 :
        MAX_ALLOC_PER_UE = 9
    if len_ue >= 5 and len_ue <= 6 :
        MAX_ALLOC_PER_UE = 5
    if len_ue >= 7 :
        MAX_ALLOC_PER_UE = 4
       
    return MAX_ALLOC_PER_UE



def compute_regret_and_sigma_for_nsym(ue, Nsym, cqi_k, k, ue_regret, sigma_list, t, T_queue, T_proc_gNB, rbs_remaining_per_slot, MAX_ALLOC_PER_UE, S):
    if ue.state.total_rbs is None :
        total_rbs = estimator_functions.estimate_required_n_rbs(ue.buffer, cqi_k , Nsym, S)
    else: 
        total_rbs = ue.state.total_rbs
    KPIs = []
    
    N = min( MAX_ALLOC_PER_UE, rbs_remaining_per_slot, total_rbs)
    
    for i in range(1, N+1):
        # dans le cas ou delta_slot pas initialisé => delta_slot = t - t_entry logique 
        if ue.state.delta_slot is None:
            T = t - ue.state.t_entry
            KPI_i = kpi_formula.compute_kpi(i, Nsym, cqi_k, estimator_functions.S, estimator_functions.mu, estimator_functions.T_slot, T, ue.qos_latency, ue.qos_throughput,  T_queue, T_proc_gNB)
            
        else: 
            KPI_i = kpi_formula.compute_kpi(i, Nsym, cqi_k, estimator_functions.S, estimator_functions.mu, estimator_functions.T_slot, ue.state.delta_slot, ue.qos_latency, ue.qos_throughput,  T_queue, T_proc_gNB)
        KPIs.append(KPI_i)

    ue_regrets_i = []


    # σ_prev : probabilité d’allouer i RB à l’itération précédente
    if k == 0:                                  # 1ʳᵉ itération → uniforme
        sigma_prev = [1.0 / N] * N
    else:
        raw = [sigma_list[i-1][k-1] for i in range(1, N+1)]
        s   = sum(raw)
        if s == 0:                              # sécurité div/0
            sigma_prev = [1.0 / N] * N
        else:
            sigma_prev = [r / s for r in raw]  
    # l'esperance du gain de la strategie courante utilisé dans la calcule du regret 
    v_sigma = sum(p * kpi for p, kpi in zip(sigma_prev, KPIs)) 

    
    for i in range(1, N+1): # Testing number of RB to allocate 
        if k == 0 :
            R_prev = 0
        else :
            R_prev = ue_regret[i-1][k-1] 

        
        KPI_i = KPIs[i-1]

        increment = KPI_i - v_sigma
        ue_regret[i-1][k] = max(0, R_prev + increment)
        regret_bank_per_ue[ue.ue_id][i-1, k] = ue_regret[i-1][k]
        ue_regrets_i.append(ue_regret[i-1][k])
                       

    for i in range(1, N+1):
        sigma_i_k = ue_regret[i-1][k] / (sum(ue_regrets_i) + 1e-9)  # avoid div by 0
        l = sigma_i_k
        sigma_list[i-1][k] = l
    
    return N

def compute_best_allocation(sigma_list, K, N_list):
    mapping = {}

    for Nsym, N in N_list:
        sigma_moy_list = [
            sum(sigma_list[i - 1][k] for k in range(K)) / K
            for i in range(1, N + 1)
        ]

        # Si en traitant tout les i rb possible et que tous in a sigma moy sont egaux --> prendre le cas optimal
        #  set transforme la liste en ensemble de valeurs unique , si tout les elements sont identique --> == 1  
        if len(set(sigma_moy_list)) == 1 and N != 1 :
            print("Tous les sigma_moy sont identiques")
            I = 1
            sigma_moy_I = sigma_moy_list[I - 1]
        else:
            I = max(range(1, N + 1), key=lambda i: sigma_moy_list[i - 1])
            sigma_moy_I = sigma_moy_list[I - 1]

        mapping[Nsym] = (I, sigma_moy_I)

    return mapping

def update_cqi_for_ues(ue_list, t, OFFSET):
    for ue in ue_list:
        if (t - ue.state.t_entry) % OFFSET == 0 and ue.state.cqi_history:
            ue.state.cqi = np.random.randint(1, 16)
            ue.state.cqi_history.append(ue.state.cqi)


def update_ue_cqi_after_scheduling(ue_list, ue_list_scheduled, Prediction, T_slot):
    for ue in ue_list:
        if ue in ue_list_scheduled:
            if not ue.state.cqi_history:
                ue.state.cqi = ue.cqi
            else:
                ue.state.cqi = ue.state.predicted_cqis_moy
        else:
            if not ue.state.cqi_history:
                ue.state.cqi = ue.cqi
            else:
                ue.state.cqi = Prediction.Predict_cqi(
                    ue.state.cqi_history[-1], Prediction.sigma, Prediction.c, T_slot
                )
