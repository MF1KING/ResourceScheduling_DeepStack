

from state import State
from action import Action

class UE:
    def __init__(self, ue_id, initial_cqi, initial_buffer, qos_latency, qos_throughput):
        # Paramètres d'entrée uniquement
        self.ue_id = ue_id
        self.cqi = initial_cqi          # CQI initial fourni par l'UE
        self.buffer = initial_buffer    # Buffer initial en MB
        self.qos_latency = qos_latency  # QoS latency requirement
        self.qos_throughput = qos_throughput  # QoS throughput requirement

        # État interne géré par State
        self.state = State(
            ue_id=ue_id,
            qos_latency=qos_latency,
            qos_throughput=qos_throughput,
            cqi=initial_cqi,
            buffer=initial_buffer,
        ) 


    
