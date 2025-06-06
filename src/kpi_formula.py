import math
from estimator_functions import compute_latency , compute_throughput
# kpi_formula.py

# Coefficients de pondération
ALPHA = 1.0   # poids du throughput
BETA = 1.5 # poids de la latence
GAMMA = 2 # poids de la violation QoS
LAMBDA = 2.0  # effet de la congestion sur la latence
RB_BW_HZ           = 180e3        # Bande passante d'un RB (180 kHz)
BITS_PER_MEGABIT   = 1e6          # Conversion bit → Mbit
BITS_PER_BYTE      = 8            # bits dans un octet
T_min, T_max = 0.064, 10
L_min, L_max = 5, 300



#def compute_violation(latency, qos_latency, throughput, qos_throughput):
    #return int(latency > qos_latency) + int(throughput < qos_throughput)

def compute_violation(latency, qos_latency, throughput, qos_throughput):
    latency_penalty = max(0, (latency - qos_latency) / qos_latency)
    throughput_penalty = max(0, (qos_throughput - throughput) / qos_throughput)
    return latency_penalty + throughput_penalty


def compute_kpi(nrbs, N_sym, cqi, S, mu , T_slot, delta_slot, qos_latency, qos_throughput, T_queue, T_proc_gNB):
    throughput = compute_throughput(nrbs, N_sym, cqi, S, mu , T_slot)
    latency = compute_latency(qos_latency, delta_slot, T_slot , N_sym, T_queue, T_proc_gNB)
    violation = compute_violation(latency, qos_latency, throughput, qos_throughput)

     # Normalisations (bornées à 1)
    throughput_norm =(math.log1p(throughput) - math.log1p(T_min)) / (math.log1p(T_max) - math.log1p(T_min))
    latency_norm    = min(max((L_max - latency) / (L_max - L_min), 0),1)

    # Pénalité de latence = (1 - score)
    latency_penalty = 1.0 - latency_norm

    violation_norm  = violation / (1.0 + violation) 


    return ALPHA * throughput_norm - BETA * latency_penalty - GAMMA * violation_norm
