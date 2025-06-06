# ue.py

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

    def observe_state(self, ue_list):
        """
        Au début du slot suivant :
        - historise et prédit CQI et buffer dans l'état
        - renvoie une copie de l'état pour prise de décision
        """
        self.state.enrich(ue_list)
        return self.state.clone()

    def update_after_action(self, action: Action):
        """
        Enregistre l'action validée dans l'état, sans toucher au buffer ni au CQI.
        Les mises à jour réelles du buffer et du CQI auront lieu au début du slot
        suivant dans `observe_state` via `state.enrich`.
        """
        self.state.update(action)



    
    
