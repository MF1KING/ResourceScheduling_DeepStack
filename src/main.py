# main.py

import numpy as np
from helpers import *
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




# === Initialisation ===
ue_list = []
ue_counter = 0


nb_warning=0

start_time = time.time()



load_ratio_indicator = []
load_ratio_expected_indicator= []
nb_warning = 0
pass_nb = 0
cqi0 = 0 
cqiii =0 



for t in range(1, NB_SLOTS + 1):
        
    print(f"\n===== SLOT {t} =====")
        
    # Depart d'ue selon un autre  processus de Poisson + Sinus pour representer les cas de handover ou autre 
    handle_departures(ue_list, t, MU_depart, A_depart, T_depart_period)
    #  Arrivée de nouveaux UEs selon un processus de Poisson + Sinus 
    ue_counter = handle_new_arrivals(ue_list, ue_counter, t, MU_arrive, A, T_arrive_period, MAX_UES)

        
    # Determiner le nombre max de rb que le scheduler peut donner par slot de temps
    MAX_ALLOC_PER_UE = update_max_alloc_per_ue(len(ue_list))
    # Sort les ues selon leur priorité 
    ue_list = prioritize_ues(ue_list) 
        
    ue_list_scheduled = []
    ue_list_unscheduled = []
    load_ratio_expected = 0 # need to be reset to 0 at every timestamp
    rbs_remaining_per_slot = TOTAL_RBS
    load_ratio =0

    update_cqi_for_ues(ue_list, t, OFFSET)

        
    for ue in ue_list: # sorted list

        T_proc_gNB = random.uniform(0.1, 0.4)          
        T_queue = random.uniform(0, ue.qos_latency)
        
            
        if load_ratio_expected >= 1:
         # Pas assez de ressources restantes, on arrête le traitement ici
            ue_list_unscheduled.append(ue)
            continue 

        else:
            sigma_list = [[0 for _ in range(K)] for _ in range(TOTAL_RBS)]   # for the current user; N listes de taille K; pour chaque n RB, jai K valeurs
            ue_regret = [[0 for _ in range(K)] for _ in range(TOTAL_RBS)]  # to store regret for the current user 
            predicted_cqis = [] # to store all cqi_k that has been predicted 

            for k in range(K): 
                if not ue.state.cqi_history:
                    cqi_k = ue.cqi 
                else:
                    cqi_k = Prediction.Predict_cqi( ue.state.cqi_history[-1], Prediction.sigma, Prediction.c, estimator_functions.T_slot)
                predicted_cqis.append(cqi_k)
                ue.state.predicted_cqis_moy= round(sum(predicted_cqis) / K)
                    
                if cqi_k == 0:
                    continue 

                scheduling_type = estimator_functions.choose_scheduling_type(ue.qos_latency)

                nsym_options = [14] if scheduling_type == "Grant-Free Type1" else [2, 4, 7]
                # CFR iterations 
                for Nsym in nsym_options:
                    N = compute_regret_and_sigma_for_nsym(ue, Nsym, cqi_k, k, ue_regret, sigma_list, t,T_queue, T_proc_gNB, rbs_remaining_per_slot, MAX_ALLOC_PER_UE, S)
             
             # verifier le nb de cqi_k =0 predis , si plus de 3/4 des cas --> I =0    
            zero_cqi_ratio = sum(1 for cq in predicted_cqis if cq == 0) / len(predicted_cqis)
            pass_nb+=1
            #if zero_cqi_ratio >= 0.75:
                #print(f"[WARNING] UE id={ue.ue_id} discarded due to low CQI predictions (ratio {zero_cqi_ratio:.2f} out of {pass_nb})")
                #nb_warning +=1 
                #ue.state.rb_chosen = 0
                #ue_list_unscheduled.append(ue)
                #continue        

            nsym_to_N_pairs = [(Nsym, N)] if scheduling_type == "Grant-Free Type1" else [(n, N) for n in [2, 4, 7]]
            # meilleur action choix avec Nsym , I a partir du sigma_moy 
            mapping_nsym_to_I_and_sigma = compute_best_allocation(sigma_list, K, nsym_to_N_pairs)
            
            
            # On extrait le Nsym qui maximise sigma_moy_star
            Nsym_star = max(mapping_nsym_to_I_and_sigma.keys(), key=lambda n: mapping_nsym_to_I_and_sigma[n][1])
            I_star = mapping_nsym_to_I_and_sigma[Nsym_star][0]

            # Decision final pour chaque ue 
            ue.state.N_sym = Nsym_star
            ue.state.rb_chosen= I_star

            # le reste de rb a allouer par le scheduler dans un mm slot
            rbs_remaining_per_slot -= ue.state.rb_chosen

            # update de la valeur du load ratio
            load_ratio_expected += ue.state.rb_chosen / TOTAL_RBS
            print(f"load_ratio_expected     : {load_ratio_expected}")

            # il se peut que son cas soit etudié mais pas traité 
            if ue.state.delta_slot is None and ue.state.rb_chosen!= 0 :
                ue.state.delta_slot = t - ue.state.t_entry
                
            # check si rb_chosen = 0 --> non traité 
            if ue.state.rb_chosen == 0 :
                ue_list_unscheduled.append(ue)
            else:
                ue_list_scheduled.append(ue)
                    
            # Affichage ou stockage du meilleur couple (Nsym*, I*)
            print(f"Best Nsym*: {Nsym_star}, Best allocation I*={I_star} RBs for UE id={ue.ue_id}, sigma_moy*={mapping_nsym_to_I_and_sigma[Nsym_star][1]:.4f}")


    update_ue_cqi_after_scheduling(ue_list, ue_list_scheduled, Prediction, estimator_functions.T_slot)

    # creation d'une liste d'ue dont leur a fini d'etre traité        
    completed_ues = []
    KPI_I_chosen =[]
    # eu_list doit etre seulement la liste de ue qui on etait traité      
    
    for ue in ue_list_scheduled:
        print(f"CQI USED {ue.state.cqi}")
        if ue.state.cqi == 0:
            ue.state.compteur -=1
            ue_list_unscheduled.append(ue)
        else:
            ue.state.compteur = 0
            Nsym_chosen= ue.state.N_sym
            I= ue.state.rb_chosen
            KPI_I= kpi_formula.compute_kpi( I  , Nsym_chosen  , ue.state.cqi, estimator_functions.S, estimator_functions.mu , estimator_functions.T_slot ,ue.state.delta_slot , ue.qos_latency, ue.qos_throughput, T_queue, T_proc_gNB)
            KPI_I_chosen.append(KPI_I)
            ue.state.enrich( ue_list_scheduled) # Append CQI and buffer history
            ue.state.buffer = update_buffer_size(ue.state.buffer_history[-1], I, ue.state.cqi_history[-1], estimator_functions.BMAX ,estimator_functions.T_slot, Nsym_chosen)
            #print(f"ID               : {ue.ue_id},CQI  historyy            : {ue.state.cqi_history[-1]} ,Buffer : {ue.state.buffer},Nsym   : {Nsym_chosen}")
            #update total_rbs pour chaque ue traité
            if ue.state.cqi_history[-1] == 0:
                ue.state.total_rbs= ue.state.total_rbs
            else:
                ue.state.total_rbs = estimator_functions.estimate_required_n_rbs(ue.state.buffer, ue.state.cqi_history[-1], Nsym_chosen, S)
            ue.state.modulation = estimator_functions.choose_modulation(ue.state.cqi)
            print("=== UE Servi ===")
            print(f"ID               : {ue.ue_id},CQI              : {ue.state.cqi:.2f} ,Type Scheduling  : {estimator_functions.choose_scheduling_type(ue.qos_latency)},Périodicité P    : {ue.state.P}")
            print(f"Delta_slot       : {ue.state.delta_slot} , Nsym choisi      : {Nsym_chosen}, RBS RESTANT      : {ue.state.total_rbs}, Buffer     : {ue.state.buffer},I (nb RBs): {I},Modulation       : {ue.state.modulation}")
            print(f"KPI Score        : {KPI_I:.2f}")
            print("=============================\n")
            load_ratio += ue.state.rb_chosen / TOTAL_RBS
            # Si ue.state.total_rbs <= 0 and ue.state.buffer <= 0.0 ---> demande traité --> sort du systeme 
            if ue.state.total_rbs is not None and ue.state.total_rbs <= 0 and ue.state.buffer <= 0.0:
                print(f"[CLEANUP] UE {ue.ue_id} a totalement satisfait sa demande et quitte le système.")
                completed_ues.append(ue)

                

        
        
    for ue in ue_list_unscheduled:
        ue.state.compteur +=1
        ue.state.enrich(ue_list_scheduled)
        ue.state.modulation = estimator_functions.choose_modulation(ue.state.cqi)


    KPI_moy = sum(KPI_I_chosen) / len(KPI_I_chosen) if KPI_I_chosen else 0 


    print(f"KPI MOYEN              : {KPI_moy}")
    print(f"load_ratio    : {load_ratio}")

    load_ratio_indicator.append(load_ratio)
    load_ratio_expected_indicator.append(load_ratio_expected)
    # Mise à jour de la ue_list
    ue_list = [ue for ue in ue_list if ue not in completed_ues]

    try:
        checkes.run_all_checks(
            slot=t,
            load_ratio=load_ratio,
            ue_list=ue_list
        )
    except checkes.ConsistencyError as e:
        print(e)

# Calcule du load ratio moyen 
load_ratio_moy =sum(load_ratio_indicator) / len(load_ratio_indicator) if load_ratio_indicator else 0 
load_ratio_expected_moy =sum(load_ratio_expected_indicator) / len(load_ratio_expected_indicator) if load_ratio_expected_indicator else 0



print(f"load_ratio_moy    : {load_ratio_moy}")
print(f"load_ratio_expected_moy    : {load_ratio_expected_moy}") 
print(f"nb_warning : {nb_warning}")
print(f"pass Total : {pass_nb}")
print(f"nb de fois periodicité brisé : {checkes.periodicity_alert_counter}")
end_time = time.time()
elapsed_ms = (end_time - start_time) * 1000
print(f"Temps total d'exécution : {elapsed_ms:.2f} ms")
plt.figure(figsize=(8,5))
K_range = np.arange(1, K + 1)

for ue_id, M in list(regret_bank_per_ue.items())[:5]:    # M = matrice 25×K d'un UE
    # 1) cumul sur k
    cumul = np.cumsum(M, axis=1)               # shape (25,K)
    # 2) on agrège sur les 25 actions  →  total par UE
    cumul_total = cumul.sum(axis=0)            # shape (K,)

    # 3) option : le regret moyen
    avg_total = cumul_total / K_range

    # 4) tracer (choisis cumul_total OU avg_total)
    plt.plot(K_range, avg_total, label=f"UE {ue_id}")


plt.xlabel("Itération k")
plt.ylabel("Regret moyen UE  R_UE(k)/k")      # ou "Regret cumulé" si tu traces cumul_total
plt.yscale("log")
plt.grid(True, which='both', ls='--', alpha=.3)
plt.legend()
plt.title("CFR : convergence du regret par UE")
plt.tight_layout()
plt.show()

