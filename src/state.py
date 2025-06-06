# state.py fiche d'info que le scheduler fait pour chaque ue a chaque slot de temps t 

from typing import List
import copy
import numpy as np
from Prediction import Predict_cqi, update_buffer_size
from action import Action

class State:
    def __init__(self, ue_id, qos_latency, qos_throughput, cqi, buffer, P = 0 , compteur = 0 , N_sym = 0,
                 scheduling_type = "", modulation = "", total_rbs = None , t_entry = 0 , delta_slot =None , rb_chosen=0, predicted_cqis_moy=0):
        # Paramètres initiaux fournis
        self.ue_id = ue_id
        self.qos_latency = qos_latency
        self.qos_throughput = qos_throughput
        self.cqi = cqi
        self.buffer = buffer
        self.scheduling_type = scheduling_type
        self.modulation = modulation
        self.total_rbs = total_rbs
        self.N_sym = N_sym
        self.P = P
        self.compteur= compteur
        self.t_entry= t_entry
        self.delta_slot = delta_slot
        self.rb_chosen= rb_chosen
        self.predicted_cqis_moy = predicted_cqis_moy

        # Historiques pour prédiction
        self.cqi_history = []  # List[int]
        self.buffer_history = []  # List[float]
        self.ue_activity_history = []  # List[int]

  

   

    def enrich(self, ue_list=None):
        # Historisation des valeurs courantes
        self.cqi_history.append(self.cqi)
        self.buffer_history.append(self.buffer)
        if ue_list is not None:
            self.ue_activity_history.append(len(ue_list))

       

  
