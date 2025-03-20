"""
===============================================================================
SFPPy Example: mass transfer from monolayer materials
===============================================================================


# Example 1: Migration of Additives from LDPE Film into a Fatty Sandwich
------------------------------------------------------------------------

## Overview
This script simulates **1D mass transfer** of **Irganox 1076** and **Irgafos 168**
from a **100 µm LDPE film** into a **fatty sandwich**. The simulation covers **10 days at 7°C**.

### Simulation Steps:
1. **Define the sandwich geometry** (cylindrical shape).
2. **Set up the polymer layer** (LDPE with additives).
3. **Define the food properties** (real, semisolid, fatty).
4. **Simulate mass transfer** for:
   - **Irganox 1076 in LDPE**.
   - **Irgafos 168 in LDPE**.
5. **Compare migration kinetics** between both cases.
6. **Save and print all simulation results**.

### Expected Outcomes:
✅ **Clear comparison of migration kinetics** for both additives.
✅ **Understanding of additive behavior in food packaging**.
✅ **Ready-to-use figures and reports for food safety analysis**.

### Updates
✅ **Substances are populated in the "foodlayer" to benefit estimates of partition coefficients**


---

@project: SFPPy - SafeFoodPackaging Portal in Python initiative
@author: INRAE\\olivier.vitrac@agroparistech.fr
@licence: MIT
"""

# %% Import Dependencies
# ----------------------
import os
from patankar.loadpubchem import migrant    # Migrant online database
from patankar.geometry import Packaging3D   # 3D geometry module
import patankar.food as food                # Food contact classes
import patankar.layer as polymer            # Polymer database
from patankar.migration import senspatankar as solver # Mass transfer solver
from patankar.migration import CFSimulationContainer as store # Store results
from patankar.migration import print_figure # Printing functions
from patankar.layer import _toSI            # Convert units to SI

# %% Output Folder
# ----------------
# Define the output directory to store results
outputfolder = os.path.join(os.getcwd(), "tmp")
os.makedirs(outputfolder, exist_ok=True)  # Create folder if missing

# %% Define Contact Conditions
# ----------------------------
# Store numbers with their units in a tuple
contactTemperature = (7, "degC")
contactTime = (10, "days")  # Contact duration

# %% Set Parameters with Uncertainty
# ----------------------------------
# Concentrations are in arbitrary units (e.g., mg/kg)
maxConcentration = 5000  # Maximum initial concentration in the polymer (e.g. 5000 mg/mg)

# %% Define Sandwich Geometry
# ---------------------------
"""
Create a **cylindrical sandwich** modeled using `Packaging3D`.
"""
sandwich_geom = Packaging3D(
    'Cylinder',
    length=(19, "cm"),  # Cylinder length/height (19 cm)
    radius=(30, "mm")    # Cylinder radius (6 mm)
)

# Compute internal volume (m³) and contact surface area (m²)
internalvolume, contactsurface = sandwich_geom.get_volume_and_area()

# %% Define the Migrant (Irganox 1076)
# ------------------------------------
# Retrieve chemical properties of the migrant (Irganox 1076)
m1 = migrant("irganox 1076")

# %% Define LDPE Film Wrapping the Sandwich
# -----------------------------------------
# Create a **100 µm thick LDPE layer** containing **Irganox 1076**
LDPElayer_with_m1 = polymer.LDPE(
    l=(100, "um"),    # Thickness: 100 µm
    substance=m1,
    C0=maxConcentration,  # Initial concentration in LDPE
    T=contactTemperature  # Contact temperature
)
# %% Define Food Properties (Fatty Sandwich)
# ------------------------------------------
"""
Define a **fatty sandwich** using multiple inheritance from `food.realfood`,
`food.semisolid`, and `food.fat`.
"""
class sandwich(food.realfood, food.semisolid, food.fat):
    name = "sandwich"

# Instantiate the food layer
FOODlayer = sandwich(
    volume=internalvolume,
    surfacearea=contactsurface,
    contacttime=contactTime,
    contacttemperature=contactTemperature,
    # omit these two lines if you want to test with default values
    substance=m1,        # required to predict partition coefficients
    simulant="ethanol"   # required to predict partition coefficients
)

# %% Run Mass Transfer Simulation (Irganox 1076)
# ---------------------------------------------
# Simulate migration for **Irganox 1076** in LDPE
simulation = solver(
    LDPElayer_with_m1,  # LDPE containing Irganox 1076
    FOODlayer,          # Fatty sandwich
    name="I1076-LDPE-sandwich"
)

# Display simulation details
print(simulation)

# Retrieve concentration at target time in SI units
print("CF at time t=", simulation.ttarget, "[s] = ", simulation.CFtarget, "[a.u.]")

# %% Interpolate Concentrations at Specific Times
# -----------------------------------------------
"""
Interpolates concentration values at **specific contact times** between 0 and **2 × ttarget**.
Beyond `2 × ttarget`, extrapolation is required.
"""
tnew = _toSI(([3, 8, 9, 10, 12, 14, 18], "days")).flatten()
CF = simulation.interpolate_CF(tnew).flatten()

# %% Generate Plots (Irganox 1076)
# --------------------------------
# Concentration profiles at ttarget
simulation.plotCx()

# Migration kinetics (CF vs time)
hfig1 = simulation.plotCF(t=tnew) # we set arbitrarily an SML to 30 mg/kg (units are shown as a.u.)

# %% Store Results for Comparison
# -------------------------------
# Store the simulation results for **Irganox 1076**
allCF = store(name="sandwich", SML=10)
allCF.add(simulation, "Irganox 1076", "r")  # Assign red color "r"

# %% Run Simulation for Irgafos 168
# ---------------------------------
# Retrieve chemical properties of the second migrant (Irgafos 168)
m2 = migrant("irgafos 168")

# Define the same LDPE film but containing Irgafos 168 instead
LDPElayer_with_m2 = polymer.LDPE(
    l=(100, "um"),
    substance=m2,  # <-- Updated substance
    C0=maxConcentration,
    T=contactTemperature
)

# Run migration simulation for **Irgafos 168**
simulation2 = solver(
    LDPElayer_with_m2,  # LDPE containing Irgafos 168
    FOODlayer.update(substance=m2),      # Same sandwich with updated substance
    name="I168-LDPE-sandwich"
)

# Add the new simulation (Irgafos 168) to the results store
allCF.add(simulation2, "Irgafos 168", "b")  # Assign blue color "b"

# Generate the corresponding plot
hfig2 = simulation2.plotCF(t=tnew)

# %% Display the partition coefficients used for m1 and m2
# Food-to-polymer partition coefficients (KFP)
# In this case, the partition coefficients are identical
KFP_m1 = LDPElayer_with_m1.k/FOODlayer.update(substance=m1).k0
KFP_m2 = LDPElayer_with_m2.k/FOODlayer.update(substance=m2).k0
print(f"m1:I1076 KF/P = {KFP_m1}","\n",f"m2:I168 KF/P = {KFP_m2}")

# %% Compare Migration Kinetics (Both Migrants)
# ---------------------------------------------
# Compare CF vs time for **Irganox 1076** and **Irgafos 168**
hfig12 = allCF.plotCF(plotSML=False) # we do not plot SML since they have different SMLs

# %% Save and Print Figures
# -------------------------
printconfig = {"destinationfolder": outputfolder, "overwrite": True}
print_figure(hfig1, **printconfig)
print_figure(hfig2, **printconfig)
print_figure(hfig12, **printconfig)


# %% Variant with operators for faster evaluation
# The general template is:
#    substance % food << packaging >> layer >> food
#    food.lastsimulation contains the last result

from patankar.layer import LDPE
film = LDPE(l=(0.1,"mm")) # a virgin film (no substance, not temperature information)
m1 % FOODlayer << sandwich_geom >> film >> FOODlayer
FOODlayer.lastsimulation.plotCF()
m2 % FOODlayer << sandwich_geom >> film >> FOODlayer
FOODlayer.lastsimulation.plotCF()
