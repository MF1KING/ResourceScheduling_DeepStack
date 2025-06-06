
periodicity_alert_counter =0 
congestion_alerte_counter=0

class ConsistencyError(Exception):
    """Exception levée en cas de violation d'une règle de cohérence dans le scheduling."""
    pass

def check_load_ratio(load_ratio, slot):
    global congestion_alerte_counter
    if load_ratio > 1:
        congestion_alerte_counter+= 1
        raise ConsistencyError(f"[ALERT] Slot {slot}: Load ratio {load_ratio:.3f} exceeds 1!")

def check_ue_compteur(ue, slot):
    global periodicity_alert_counter
    if ue.state.compteur == ue.state.P + 1 :
        periodicity_alert_counter +=1 
        raise ConsistencyError(f"[ALERT] Slot {slot}: Non respect de la Periodicité de l'UE {ue.ue_id}  compteur={ue.state.compteur}; P={ue.state.P}")
   
def check_ue_exit_conditions(ue, slot, ue_list):
    # On considère comme "en infraction" une UE qui n'aurait plus de demande mais resterait dans la liste
    if ue.state.total_rbs is not None and ue.state.total_rbs <= 0 and ue.state.buffer <= 0.0 and ue in ue_list:
        raise ConsistencyError(
            f"[ALERT] Slot {slot}: UE {ue.ue_id} has total_rbs <= 0 and buffer <= 0 but is still in ue_list."
        )

def run_all_checks(slot, load_ratio, ue_list):
    check_load_ratio(load_ratio, slot)
    for ue in ue_list:
        check_ue_compteur(ue, slot)
        check_ue_exit_conditions(ue, slot, ue_list)
