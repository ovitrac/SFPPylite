#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SFPPy Example: mass transfer from chained steps and complex scenarios
===============================================================================


Example 3: Advanced Migration Simulation with Variants
------------------------------------------------------

Scenario: Mass Transfer in a Multilayer Packaging System
--------------------------------------------------------
This example simulates the migration of **limonene** from a recycled **polypropylene (PP)** core
to food, using a **trilayer packaging (ABA structure)** where **A = PET** and **B = PP**.
The study follows three consecutive storage and processing steps:

1. Storage at ambient temperature (20°C) for 4 months
2. Hot-filling at 90°C with a fatty food
3. Storage at 30°C for 6 months

Limonene is initially present in **B at 200 mg/kg**. The layer thicknesses are:
- PET (A): **20 µm**
- PP (B): **500 µm**

Variants Studied:
- **Variant 1**: Replace limonene with toluene
- **Variant 2**: Reduce B’s thickness from 20 µm to 10 µm for both limonene and toluene
- **Variant 3**: Combination of Variant 1 and Variant 2

All four conditions (Reference, Variant 1, Variant 2, and Variant 3) are compared in a single
figure, with results exported to **Excel and CSV** for further analysis.

--------------------------------------------------------
Exploring SFPPy’s Database
--------------------------------------------------------
This example allows interaction with **SFPPy’s extensive databases**, including:
- **3D geometries** (predefined packaging shapes)
- **Chemical substances** (millions via PubChem)
- **Food contact conditions** (various storage and processing scenarios)
- **Polymers and materials** (tens of predefined types)

--------------------------------------------------------
Key Features and Pythonic Syntax
--------------------------------------------------------

1. **Compact and Concise Code Structure**
Example 3 demonstrates **chained simulations** with **minimal coding**, contrasting with
Examples 1 and 2. The approach **stores results within objects**, enabling streamlined operations.

2. **Operator `>>` for Seamless Processing**
The `>>` operator automates **property propagation** and **mass transfer simulations**:
- `mypackaging >> myfood` → Updates **food geometry**
- `food1 >> food2` → Synchronizes food properties
- `myfood >> mymaterial` → Transfers **temperature**
- `mymaterial >> myfood` → Simulates **mass transfer**

Example: `mypackaging >> myfood >> mymaterial >> myfood` performs:
1. **Update food geometry** to match packaging
2. **Transfer temperature** to the material
3. **Simulate mass transfer** from material to food

For multiple contact conditions:
`mypackaging >> foodcontact2 >> foodcontact1 >> mymaterial >> foodcontact1 >> foodcontact2`
- Adjusts food geometry (`foodcontact1`, `foodcontact2`)
- Transfers **temperature** (`foodcontact1 >> mymaterial`)
- Simulates mass transfer and propagates results
- Final results stored in **foodcontact1.lastsimulation, foodcontact2.lastsimulation**

To explicitly save results: `result = ... step n >> step n+1`
Dynamic updates:
`foodcontact1 >> mymaterial.update(substance="new migrant", l=new_thickness) >> foodcontact1`

3. **Operator `+` for Combining Results**
- **Material assembly:** `ABA = A + B + A` (trilayer structure)
- **Merging simulation results:** `fullsolution = foodcontact1.lastsimulation + foodcontact2.lastsimulation`

4. **Comprehensive Result Output**
- **Visualization:** Results can be plotted directly
- **Exporting:** Save to **Excel** (`.xlsx`) and **CSV** (`.csv`)

--------------------------------------------------------
Summary
--------------------------------------------------------
Example 3 demonstrates **efficient chaining of migration simulations** using intuitive operators
(`>>` for sequential processing, `+` for merging results). SFPPy’s powerful database and
Pythonic syntax enable complex simulations with minimal effort.


@project: SFPPy - SafeFoodPackaging Portal in Python initiative
@author: INRAE\\olivier.vitrac@agroparistech.fr
@licence: MIT
"""

# %% Output Folder & layout
# -------------------------
# Define the output directory to store results.
import os
outputfolder = os.path.join(os.getcwd(), "tmp")  # Full path
os.makedirs(outputfolder, exist_ok=True)  # Create folder if missing
# 👤 User Overrides to set units for plotting
from patankar.useroverride import useroverride # type useroverride <enter>
useroverride.update(
    tunit = "days",    # time units (can be any value s,min,days,weeks,months,years)
    lunit = "µm",      # length units (can be any value, nm, µm or um, mm,cm or even in)
    Cunit = "mg/kg",  # set concentration units instead of a.u.
    )
# %% Build the geometry
# ---------------------
"""
Identify and select a suitable 3D packaging geometry.
The function `help_geometry()` lists available shapes.

Example: `box_container` is a rectangular prism with one open face.
Its volume and surface area are computed as:
    Volume = length × width × height
    Surface Area = 2(lw + lh + wh) - lw  (removing the open top)
"""
# Import the geometry module
from patankar.geometry import Packaging3D, help_geometry

# Display available geometries and required parameters
help_geometry()

# Define the container as an open rectangular prism
container = Packaging3D('box_container', height=(8, "cm"), width=(10, "cm"), length=(19, "cm"))

# %% Define the migrant
# ---------------------
# Retrieve the properties of the migrating substance.
from patankar.loadpubchem import migrant

# Search for limonene in PubChem and retrieve chemical properties.
m = migrant("limonene")

# %% Identify the materials
# -------------------------
"""
List available polymer/material options for packaging.
Use `help_layer()` to display predefined materials.

| Class Name | Type     | Material                 | Code |
|------------|---------|---------------------------|------|
| PP         | polymer | isotactic Polypropylene   | PP   |
| gPET       | polymer | glassy PET                | PET  |
| wPET       | polymer | plasticized PET           | PET  |
"""
# Import material properties
from patankar.layer import help_layer, layer

# Display available polymer options
help_layer()

# Import required polymer classes (Polypropylene, PET with two states)
from patankar.layer import gPET, wPET, PP

# %% Build the materials
# ----------------------
"""
Define and configure the layers for the multilayer packaging.
Each layer has properties such as:
    - Thickness (`l`)
    - Initial concentration (`C0`)
    - Migrant type (`substance`, `migrant`, etc.)

Property synonyms:
| Parameter  | Synonyms                  |
|------------|---------------------------|
| substance  | molecule, solute, migrant |
| C0         | Cp0, CP0                  |
| l          | lp, lP                    |
"""
# Define the PET (A) and PP (B) layers
Aw = wPET(l=(20, "um"), migrant=m, C0=0)      # 20 µm plasticized PET with no initial migrant
B = PP(l=(0.5, "mm"), migrant=m, CP0=200)    # 500 µm PP with 200 mg/kg limonene
A = gPET(l=(20, "um"), migrant=m, C0=0)      # 20 µm PET with no initial migrant

# Assemble the multilayer structure: ABA configuration
ABA = Aw + B + A

# Display basic information (default temperature: 40°C)
print("\nOur ABA technology\n", repr(ABA))

# %% Identify storage and contact conditions
# -----------------------------------------
"""
Define different storage and processing conditions.
Use `help_food()` to display available predefined food-contact scenarios.

| Class Name  | Description              | Level  | Inheritance    | Parameters        |
|-------------|--------------------------|--------|----------------|-------------------|
| fat        | Fat contact               | root   |chemicalaffinity| k0                |
| liquid     | Liquid food               | root   | texture        | h                 |
| ambient    | Ambient storage           | contact| realcontact    | contacttemperature|
| hotfilled  | Hot-filling               | contact| realcontact    | contacttemperature|
| stacked    | Stacked storage           | user   | setoff         | h                 |
"""
from patankar.food import help_food
help_food()

# Import relevant food-contact conditions
from patankar.food import realfood, liquid, fat, ambient, hotfilled, stacked

# Define three food-contact conditions
class contact1(stacked, ambient):
    name = "1:setoff"
    contacttemperature = (20, "degC")
    contacttime = (3, "months")

class contact2(hotfilled, realfood, liquid, fat):
    name = "2:hotfilling"

class contact3(ambient, realfood, liquid, fat):
    name = "3:storage"
    contacttime = (6, "months")

# Instantiate food-contact conditions
medium1 = contact1(contacttime=(4, "months"))  # Adjust time
medium2 = contact2()
medium3 = contact3()

# %% Wrap the food with its container-packaging
# --------------------------------------------
"""
Use the `>>` operator to propagate the packaging properties (volume, surface area)
to all food-contact conditions.

Example:
    container >> medium1 >> medium2 >> medium3
"""
container >> medium1 >> medium2 >> medium3

# %% Simulate Step 1
# ------------------
"""
Chain operations using `>>`:
1. Transfer temperature from `medium1` to `ABA`
2. Simulate mass transfer from `ABA` to `medium1`
"""
medium1 >> ABA
medium1 >> ABA >> medium1

# Verify simulation results
medium1.lastsimulation.plotCx()

# %% Simulate all steps (Step 1 → Step 2 → Step 3)
# -----------------------------------------------
"""
Continue simulation by chaining:
    medium1 >> ABA >> medium1 >> medium2 >> medium3 <--- recommended syntax
    medium1 @ ABA >> medium1 >> medium2 >> medium3
    m % medium1 >> ABA >> medium1 >> medium2 >> medium3
    m % medium1 @ ABA >> medium1 >> medium2 >> medium3

All results are stored inside:
    medium1.lastsimulation, medium2.lastsimulation, medium3.lastsimulation

note: @ and >> work similarly except that @ does not force the propagation of the substance id
"""
medium1 >> ABA >> medium1 >> medium2 >> medium3

# Plot migration kinetics
medium1.lastsimulation.plotCx()
medium2.lastsimulation.plotCF()
medium3.lastsimulation.plotCF()

# %% Combine all profiles into a single kinetic curve
# ---------------------------------------------------
"""
Use `+` operator to merge kinetic profiles.
"""
sol123 = medium1.lastsimulation + medium2.lastsimulation + medium3.lastsimulation
sol123.plotCF()

# %% Variant 1: Replace limonene with toluene
# -------------------------------------------
"""
Repeat all steps using toluene instead of limonene.
"""
m2 = migrant("toluene")  # Retrieve new migrant

# Restart the simulation pipeline with updated migrant
# Different methdologies exist to update susbtance, note that substances always update from the most left position.
# It is recommended to start the update at the begining (strategy A)
# or to clear (with []) any substance first (strategy B).
m2 % medium1 @ ABA >> medium1 >> medium2 >> medium3

# Store results
sol123_variant1 = medium1.lastsimulation + medium2.lastsimulation + medium3.lastsimulation
sol123_variant1.plotCF()

# %% Variant 2: Reduce thickness of outer PET layers
# --------------------------------------------------
"""
Halve the thickness of the first and last layers (A) while keeping PP constant.
"""
refthickness = ABA.l.copy()
newthickness = refthickness.copy()
newthickness[[0, -1]] /= 2  # Reduce thickness of A layers (index 0=first layer in contact with food, index -1= last layer)

# Restart simulation with modified structure (strategy B)
medium1.update(solute=[]) >> ABA.copy(l=newthickness, migrant=m) >> medium1 >> medium2 >> medium3
sol123_variant2 = medium1.lastsimulation + medium2.lastsimulation + medium3.lastsimulation

# %% Variant 3: Combine Variant 1 and Variant 2
# ---------------------------------------------
"""
Use both modifications:
- Toluene as the migrant
- Reduced PET layer thickness

Here @ replaces the first >>, they are equivalent
"""
ABA_with_toluene = ABA.copy(l=newthickness, migrant=m2)
m2 % medium1 @ ABA_with_toluene >> medium1 >> medium2 >> medium3
sol123_variant3 = medium1.lastsimulation + medium2.lastsimulation + medium3.lastsimulation

# %% Compare Reference and Variants
# ---------------------------------
"""
Store and compare all solutions using `CFSimulationContainer`.
"""
from patankar.migration import CFSimulationContainer as store

# Initialize collection
collection = store(name="container with FB")

# Add results to collection
collection.add(sol123, "Limonene-FB = 20 µm (ref)", "dodgerblue", linewidth=3)
collection.add(sol123_variant1, "Toluene-FB = 20 µm (v1)", "orangered", linewidth=3)
collection.add(sol123_variant2, "Limonene-FB = 10 µm (v2)", "deepskyblue", linewidth=2)
collection.add(sol123_variant3, "Toluene-FB = 10 µm (v3)", "tomato", linewidth=2)

# Plot comparative migration kinetics
collection_fig = collection.plotCF()

# %% Export Results (PNG, PDF, Excel, CSV)
# ----------------------------------------
"""
Save simulation results for further analysis.
"""
printconfig = {"destinationfolder": outputfolder, "overwrite": True}
collection_fig.print(**printconfig)

# Export data
collection.save_as_csv(filename="example3.csv", destinationfolder=outputfolder, overwrite=True)

# saving to Excel requires: openpyxl >= 3.0.10
# (install it with `conda install openpyl` if you encounter an error message)
collection.save_as_excel(filename="example3.xlsx", destinationfolder=outputfolder, overwrite=True)

# %% Script Extension (1) - Potential Release (PR)
# -------------------------------------------------
"""
Analysis at the scale of the full packaging (the initial distribution of contaminants is preserved)
    PR = PRE * PRT

PR : ndarray of shape (n_steps,)
    Array of **intrinsic potential release values** for each step in the
    current sequence of transfer (e.g. storage, hot fill, long-term storage).

    Definition
    ----------
    For step k, PR[k] is the *partial* potential release reconstructed from
    the total potential release of the full sequence (PRN) and the potential
    release of the sequence with step k omitted (PR^{(N\setminus k)}):
        PR[k] = 1 - (1 - PRN) / (1 - PR^{(N\setminus k)})

    Interpretation
    --------------
    - 0 ≤ PR[k] ≤ 1 by construction, though very small negatives can appear
      due to numerical noise.
    - PR[k] measures the **incremental contribution** of step k to the overall
      potential release, taking into account the state inherited from upstream
      steps.
    - Values are *contextual*: PR[k] cannot be obtained from the step alone
      (mass balance with initial contaminant distribution), but only via
      comparison of the full sequence and variants where step k is omitted.

    Usage
    -----
    - The full-chain potential release PRN should satisfy, in the ideal
      independence case:
          PRN ≈ 1 - ∏_k (1 - PR[k])
    - Deviations from this identity (closure error) quantify the degree of
      **non-independence/path dependence** (e.g. set-off, back-diffusion).
    - Ratios such as PR/PRN provide a ranking of steps by their relative
      contribution to the total potential release.

    Notes
    -----
    The array PR is scalar (per step). For spatial attribution within layers,
    see `PR_layers`, which provides signed layer-resolved diagnostics that
    complement the stepwise PR[k].

"""
import numpy as np
# analysis based on variant 1
# effective potential release of steps 1+2+3, 2+3, 1+2
m2 % medium1 @ ABA >> medium1 >> medium2 >> medium3
PRall123 = np.array([medium.lastsimulation.PR.PRtarget_effective for medium in [medium1,medium2,medium3]])
medium2 @ ABA >> medium2 >> medium3 # step 1 omitted
PRall23 = np.array([medium.lastsimulation.PR.PRtarget_effective for medium in [medium2,medium3]])
medium1 @ ABA >> medium1 >> medium3 # step 2 omitted
PRall13 = np.array([medium.lastsimulation.PR.PRtarget_effective for medium in [medium1,medium3]])

# intrinsic potential release for steps, 1=1+2+3\2+3,2=1+2+3\1+3,3=1+2+3\1+2
PR = np.zeros((len(PRall123),),dtype=float)
PRN = PRall123[-1,0] # potential release with all steps
PR[0] = 1.0 - (1.0-PRN)/(1.0-PRall23[1,0])
PR[1] = 1.0 - (1.0-PRN)/(1.0-PRall13[1,0])
PR[2] = 1.0 - (1.0-PRN)/(1.0-PRall123[1,0])
print("PR =", PR)
print("PRT =", PR/medium3.lastsimulation.PR.PRE_effective)
print("score = PR/PRN =", PR/PRN)
# compute the error on intrinsic PR
PRN_control = 1-np.prod(1-PR)
print(f"PR deviation ~ {(PRN_control/PRN - 1).item()*100:0.3f} %")


# %% Script Extension (2) - Potential Release (PR)
# -------------------------------------------------
"""
Analysis at the scale of each layer (j=1,2,3).

PR_layers : ndarray of shape (n_steps, n_layers)
    Array of **intrinsic potential release values per step and per layer**
    in a multilayer system, reconstructed by comparison of full and
    step-omitted sequences.

    Definition
    ----------
    For each step k (row) and layer j (column), PR_layers[k,j] is defined by:
        PR_layers[k,j] = 1 - (1 - PRN_layers[j]) / (1 - PR^{(N\setminus k)}[j])
    where:
        - PRN_layers[j] is the potential release at the food side contributed
          by layer j after the full sequence of steps,
        - PR^{(N\setminus k)}[j] is the potential release obtained by omitting
          step k, with all other steps applied.

    Implementation
    --------------
    - In practice, PR_layers is built from chained simulations:
        R123 = F1.potentialRelease(ABA) >> F2 >> F3   # full chain
        R23  = F2.potentialRelease(ABA) >> F3         # omit step 1
        R13  = F3.potentialRelease(ABA) >> F3         # omit step 2
      Each `potentialRelease` call initializes one layer with a concentration
      and propagates mass transfer through all steps.
    - Row k corresponds to step k (e.g. storage, hot fill, long storage).
    - Column j corresponds to a specific layer (e.g. A–B–A).

    Interpretation
    --------------
    - 0 ≤ PR_layers[k,j] ≤ 1 in principle; small negatives may appear due to
      back-diffusion or numerical artifacts.
    - Positive values indicate **net forward (food-ward) contribution** of
      layer j during step k.
    - Negative values indicate **reverse flux / reflux** from layer j
      (e.g. set-off during non-contact storage).
    - These values are *diagnostic*: they show where in the structure the
      release is mobilized or suppressed during each step.

    Usage
    -----
    - Compare rows to identify which step is dominant for each layer.
    - Compare columns to locate protective or source layers in the multilayer.
    - Closure check:
          PRN_layers_control = 1 - ∏_k (1 - PR_layers[k,:])
      should approximate PRN_layers (within path-dependence limits).
    - Do not sum across layers: PR_layers is not a mass partition but a
      **layer-resolved potential release diagnostic**.

    Notes
    -----
    - `PR_layers` complements the stepwise scalar `PR` array by providing
      **spatial attribution** of each step’s effect.
    - Because `potentialRelease` assigns concentrations independently to each
      layer, PR_layers must be read as a **signed relative contribution**,
      not as directly additive quantities.
"""
R123 = medium1.potentialRelease(ABA,C0test=200) >> medium2 >> medium3
R23 = medium2.potentialRelease(ABA) >> medium3
R13 = medium1.potentialRelease(ABA) >> medium3

# intrinsic layer-based potential release
PR_layers = np.zeros((len(R123),len(ABA)),dtype=float) #nsteps x nlayers
PRN_layers = R123.PR[2,:]
PR_layers[0,:] = 1.0 - (1.0-PRN_layers)/(1.0-R23.PR[1,:])
PR_layers[1,:] = 1.0 - (1.0-PRN_layers)/(1.0-R13.PR[1,:])
PR_layers[2,:] = 1.0 - (1.0-PRN_layers)/(1.0-R123.PR[1,:])
PRN_layers_control = 1 - np.prod(1-PR_layers,axis=0)
