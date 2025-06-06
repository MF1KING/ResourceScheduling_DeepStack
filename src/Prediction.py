import random
import numpy as np
from scipy.special import j0
from estimator_functions import cqi_to_spectral_efficiency
# Constante : vitesse de la lumière en m/s
c = 3e8  # [m/s]
sigma = 2 # pour l'instant


# === Prediction du CQI a travers un filtre autoregressif d'ordre 1 + alpha modelisé par un modele de Jacke/Clarke ===
def Predict_cqi(cqi_t, sigma, c, T_slot):

       # === Pairing vitesse (m/s) et frequence porteuse (Hz) pour le modèle de Jakes/Clarke
    scenario_pairings = {
        "Indoor Hotspot (InH) - 4 GHz": (3 / 3.6, 4e9),
        "Indoor Hotspot (InH) - 30 GHz": (3 / 3.6, 30e9),
        "Indoor Hotspot (InH) - 70 GHz": (3 / 3.6, 70e9),
        "Dense Urban UMi-SC (30 GHz)": (30 / 3.6, 30e9),
        "Dense Urban Macro (4 GHz)": (30 / 3.6, 4e9),
        "Rural Macro (RMa)": (120 / 3.6, 700e6),
        "Long Range Rural": (160 / 3.6, 700e6),
        "Highway": (250 / 3.6, 6e9),
        "High-Speed Train (HST) - 4 GHz": (500 / 3.6, 4e9),
        "High-Speed Train (HST) - 30 GHz": (500 / 3.6, 30e9)
    }

    # Étape 1 : Choix aléatoire
    chosen_scenario, (v, fc) = random.choice(list(scenario_pairings.items()))
    #possible_speeds_ms = speed_options[fc]

    #v = random.choice(possible_speeds_ms)
    # Étape 2 : Calcul Doppler
    f_d = v * fc / c  # Doppler shift en Hz

    # Initialisation de alpha via le modèle de Clarke/Jakes
    alpha = j0(2 * np.pi * f_d * T_slot/1000)
    #stabilizer =2 

    # AR(1) process with Gaussian noise
    wt = np.random.normal(loc=0, scale=sigma)
    cqi_t1 = alpha * cqi_t  + np.sqrt(1 - alpha**2) * wt

    #clipping
    cqi_t1_clipped = int(np.clip(round(cqi_t1), 0, 15))

    return cqi_t1_clipped



# === Update du buffer en enlevant la taille du buffer transmit par le scheduler au slot de temps t 
def update_buffer_size(buffer_t, nrbs, cqi, BMAX, T_slot, Nsym):
    
    # 1. Compute Spectral Efficiency η(CQI)
    SE = cqi_to_spectral_efficiency(cqi)  # [bit/s/Hz]

    # 2. Compute service S_u(t) in MB
    #bits_transmitted = nrbs * SE * 12 * 15000 * T_slot
    bits_transmitted = nrbs * SE * 12 * Nsym* T_slot
    S_t = bits_transmitted / (8 * 1e6)  # --->[MB]

    # 3. Update buffer:
    buffer_next = min(BMAX, max(0.0, buffer_t - S_t))

    return buffer_next











# Affichage
#print(f"🎯 Scenario: {chosen_scenario}")
#print(f"→ v = {v:.2f} m/s, fc = {fc/1e9:.1f} GHz")
#print(f"→ Doppler shift f_d = {f_d:.2f} Hz")




