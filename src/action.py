class Action:
    def __init__(self, ue_id, scheduling_type, modulation, n_rbs, N_sym):
        self.ue_id = ue_id
        self.scheduling_type = scheduling_type
        self.modulation = modulation
        self.n_rbs = n_rbs
        self.score = None  # Sera mis à jour après simulation
        #self.remaining_demand = remaining_demand
        self.N_sym = N_sym

    def set_score(self, value):
        self.score = value

    def __repr__(self):
        return (f"Action(UE={self.ue_id}, Type={self.scheduling_type}, MCS={self.mcs}, "
                f"RBs={self.n_rbs}, Score={self.score})")
