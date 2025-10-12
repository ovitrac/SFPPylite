#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFPPy demo - Multilayer with a Functional Barrier
-------------------------------------------------
Scenario: Toluene in a recycled PP core, with/without a PET functional barrier
Contact: ethanol, 60 days @ 40oC
Outputs: CF(t) curves, snapshots, and a small thickness study for the FB

Created on Thu Aug 28 11:08:24 2025

@author: olivi
"""

# --- Imports ---
from patankar.loadpubchem import migrant
from patankar.layer import PP, gPET
from patankar.food import ethanol
from patankar.migration import senspatankar, CFSimulationContainer
import matplotlib.pyplot as plt

# --- Define Migrant (Toluene) ---
tol = migrant("toluene")

# --- Define Layers ---
PPcore = PP(l=500e-6, C0=200, substance=tol)    # 500 µm PP with 200 mg/kg toluene
PETbarrier = gPET(l=30e-6, C0=0, substance=tol) # 30 µm PET barrier, initially no migrant

# --- Build Multilayer Systems ---
multilayer_with_FB = PETbarrier + PPcore    # PET on food side
multilayer_no_FB = PPcore                   # no barrier

# --- Define Food (Ethanol, 40°C, 10 days) ---
food_contact = ethanol(contacttime=(60, "days"), contacttemperature=(40, "degC"))

# --- Run Simulations ---
result_no_FB = senspatankar(multilayer_no_FB, food_contact, name="No Barrier")
result_with_FB = senspatankar(multilayer_with_FB, food_contact, name="With 30 µm PET FB")

# --- Plot & Compare ---
result_no_FB.plotCF()
result_with_FB.plotCF()
comparison = CFSimulationContainer(name="Toluene Migration into Fatty Food", SML=0.15e-3, SMLunit="mg/kg")
comparison.add(result_no_FB, label="No Barrier", color='red')
comparison.add(result_with_FB, label="With 30 µm PET FB", color='blue')
hfig=comparison.plotCF()
plt.yscale("log")
plt.ylim(1e-10,10)
plt.axhline(0.5e-3, color='black', linestyle='--', label="FDA ToR (0.5 µg/kg)")
plt.title("Toluene Migration into Fatty Food")
plt.ylabel("C_F (mg/kg)")
plt.xlabel("Time (days)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Print ---
hfig.print('ex5RAG',destinationfolder="tmp/",overwrite=True)
