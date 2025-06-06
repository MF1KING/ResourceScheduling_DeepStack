# estimator_functions.py

import numpy as np
import random
#from ue import UE

# === Constantes globales ===
#N0 = 1e-13               # Bruit thermique en Watts (~ -100 dBm)
IMAX = 10                # Interférence maximale plausible en dB
ETA = 0.7                # Lissage temporel (LoadRatio, Buffer)
ALPHA_CSI = 0.7          # Pondération temporelle pour AR(2)
SIGMA_CSI = 1.0          # Variance du bruit gaussien pour CSI
BMAX = 2.0               # Capacité maximale du buffer (MB)
WINDOW = 3               # Fenêtre glissante
TOTAL_RBS = 25           # Capacité totale en RBs de la cellule
BW_RB = 180e3            # Bande passante par RB en Hz (5G: 180 kHz)
T_slot= 1                # Durée d'un slot en ms 
S = 1                    # Transfert block scaling factor 
mu = 0                   # 12 sous porteuse de 15 KHz => 180 KHz => mu=0

#T_proc_gNB = random.uniform(0.1, 0.4)          # Processing delay au niveau du gnB [ms]
#T_queue = random.uniform(0, qos_latency)       # Temps d'attente du packet [ms]
#N_sym = compute_Nsym(qos_latency)
#sched_type = choose_scheduling_type(qos_latency)




# === 1. Choix du Modulation and Coding Scheme (MCS) ===
def choose_modulation(cqi):
    if cqi == 0 :
        return "No modulation due to BAD CQI "
    elif cqi > 0 and cqi <= 3:
        return "QPSK"
    elif cqi > 3 and cqi <= 6:
        return "16QAM"
    elif cqi > 6 and cqi <= 11:
        return "64QAM"
    else:
        return "256QAM"

# === 2. Choix du type de scheduling ===
def choose_scheduling_type(qos_latency):
    if qos_latency <= 10 :
        return "Grant-Free Type2"
    else:
        return "Grant-Free Type1"




# === Assigner une Periodicité pour nouveau ue rentrant dans le systeme  ===
def assign_periodicity(qos_latency):
    possible_P_values = [1, 2, 4, 5, 8, 10, 20, 40, 80, 160, 320]
    valid_P = [p for p in possible_P_values if p <= qos_latency]
    return random.choice(valid_P)



# === Estimation de la Spectral Efficiency a travers un mapping utilisé par 3GPP ===
def cqi_to_spectral_efficiency(cqi):
    cqi_to_se = {
        0: 0.0, 1: 0.1523, 2: 0.3770, 3: 0.8770, 4: 1.4766 ,
        5: 1.9141, 6: 2.4063, 7: 2.7305, 8: 3.3223, 9: 3.9023,
        10: 4.5234, 11: 5.1152, 12: 5.5547, 13: 6.2266, 14: 6.9141, 15: 7.4063
    }
    return cqi_to_se.get(cqi, 1.0) #retourne 1 dans le cas ou cqi en dehors de 0-15



# === Delai entre le moment ou gnB autorise la transmission et la transmission ===
def compute_T_scheduling(qos_latency, delta_slot, T_slot):
    sched_type = choose_scheduling_type(qos_latency)
    if sched_type == "Grant-Free Type2":
        return 0
    elif sched_type == "Grant-Free Type1":
        return delta_slot * T_slot
    else:
        print(f"[ERROR] Unknown scheduling type: '{sched_type}'")
        raise ValueError("Unknown scheduling type")

# ===  Temps qu'il faut pour envoyer dans l'uplink channel ===
def compute_T_air(N_sym, T_slot):
   
    T_air = (N_sym * T_slot)/14 # 14 car Cycle prefix CP normal => presence de 14 symboles OFDM par slot 
    
    return T_air


# === calcule de la latence ===
def compute_latency(qos_latency, delta_slot, T_slot , N_sym, T_queue, T_proc_gNB ):
    """
    Calcule la latence total en sommant :
    T_queue + T_scheduling + T_air + T_proc_gNB

    Retour :
    - Latence  [ms]
    """
    T_scheduling = compute_T_scheduling(qos_latency, delta_slot, T_slot)
    T_air = compute_T_air(N_sym, T_slot)

    # Somme des composantes
    latency = T_queue + T_scheduling + T_air + T_proc_gNB

    return latency


# === 3. Estimation du nombre de RBs requis ===
def estimate_required_n_rbs(buffer, cqi, N_sym, S):
    """
    Estimate the required number of PRBs based on buffer size, CQI, number of symbols, and scaling coefficient S.

    Parameters:
    - buffer: data volume to transmit [in MB]
    - cqi: channel quality indicator
    - N_sym: number of OFDM symbols used
    - S: scaling coefficient for transmission block

    Returns:
    - Required number of PRBs (integer)
    """
    SE = cqi_to_spectral_efficiency(cqi)
    #if SE <= 0:
        #return 1  # 1 pour l'instant 1  mais en realité  => ne faire aucune action 
    denominator = S * SE * 12 * N_sym # 12 pour le Nb de sous porteuse dans un RB 
    buffer_bits = buffer * 8 * 1e6  #  MB ----> bits
    return int(np.ceil(buffer_bits / denominator))
    

# === 4. Initialisation des champs total_rbs_demand et remaining_demand
def initialize_ue_demand(buffer, cqi, N_sym, S):
    total_rbs = estimate_required_n_rbs(buffer, cqi, N_sym, S)
    ue.total_rbs_demand = total_rbs
    ue.remaining_demand = total_rbs


import numpy as np

def compute_throughput(nrbs, N_sym, cqi, S, mu , T_slot):
    """
    Estimate throughput in Mbit/s using N_info ≈ TBS.
    
    Args:
        nrbs (int): Number of RBs allocated
        N_sym (int): Number of OFDM symbols 
        cqi: channel quality indicator
        S :  transport block scaling facteur
        mu (int): 0
        T_slot:  Durée d'un slot en ms 


    Returns:
        float: estimated throughput [Mbit/s]
    """
    # Compute N_RE (number of resource elements)
    N_re = nrbs * 12 * N_sym

    SE = cqi_to_spectral_efficiency(cqi)

    # Compute N_info, approximated as TBS (Transport Block Size) Nb de bit exploitable min qu'il faut mettre dans le bloc
    N_info = int(SE * N_re * S)
    
    # Compute slots per second
    N_slot_per_sec = 1000 / (2 ** mu)
    
    # Compute throughput
    throughput_mbps = ( N_info * N_slot_per_sec) / (1e6) # ---> Mbit/s
    
    return throughput_mbps
