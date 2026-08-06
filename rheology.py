"""
rheology.py
------------
Drilling Fluids & Hydraulics Engine (PENG 258 Capstone - PyMudCement-Optima)

Handles:
- Bingham-Plastic shear stress model
- PV/YP-based fluid characterisation
- Basic hole-cleaning indicator (YP:PV ratio)

All inputs are dynamic (no hardcoded values) - pass in your own mud report data.
"""


def shear_stress(yield_point_pa: float, plastic_viscosity_pa_s: float, shear_rate_s: float) -> float:
    """
    Calculate shear stress using the Bingham-Plastic rheological model.

    tau = YP + PV * shear_rate

    Parameters
    ----------
    yield_point_pa : float
        Yield Point (YP) in Pascals - the minimum stress needed before the fluid flows
    plastic_viscosity_pa_s : float
        Plastic Viscosity (PV) in Pa.s
    shear_rate_s : float
        Shear rate in s^-1

    Returns
    -------
    float
        Shear stress in Pascals (Pa)
    """
    if shear_rate_s < 0:
        raise ValueError("Shear rate cannot be negative.")
    return yield_point_pa + (plastic_viscosity_pa_s * shear_rate_s)


def pv_from_cp(pv_cp: float) -> float:
    """
    Convert Plastic Viscosity from centipoise (cP) - the common field unit reported
    on mud reports - to Pa.s (SI unit) used in the calculations here.

    1 cP = 0.001 Pa.s

    Parameters
    ----------
    pv_cp : float
        Plastic viscosity in centipoise, as read from a mud report

    Returns
    -------
    float
        Plastic viscosity in Pa.s
    """
    return pv_cp * 0.001


def hole_cleaning_indicator(yield_point_pa: float, plastic_viscosity_pa_s: float) -> str:
    """
    Simple qualitative indicator of hole-cleaning / cuttings-carrying capacity based
    on the YP:PV ratio. A higher ratio generally indicates better cuttings transport
    at lower flow rates.

    This is a simplified screening tool, not a substitute for full cuttings-transport
    hydraulics modelling.

    Parameters
    ----------
    yield_point_pa : float
        Yield Point (YP) in Pascals
    plastic_viscosity_pa_s : float
        Plastic Viscosity (PV) in Pa.s

    Returns
    -------
    str
        Qualitative hole-cleaning assessment
    """
    if plastic_viscosity_pa_s <= 0:
        raise ValueError("Plastic viscosity must be greater than zero.")

    ratio = yield_point_pa / plastic_viscosity_pa_s

    if ratio < 200:
        return f"YP:PV ratio = {ratio:.1f} -> LOW: poor cuttings-carrying capacity, review hole cleaning."
    elif ratio <= 600:
        return f"YP:PV ratio = {ratio:.1f} -> GOOD: adequate cuttings-carrying capacity."
    else:
        return f"YP:PV ratio = {ratio:.1f} -> HIGH: excellent carrying capacity, but check for excess ECD/pump pressure."


# ---------------------------------------------------------------------------
# Quick manual test - run this file directly to validate against a hand calc
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example mud report data (matches the hand-calculation worked through earlier)
    yp = 8              # Pa
    pv = pv_from_cp(20)  # 20 cP converted to Pa.s -> 0.02 Pa.s
    shear_rate = 500     # s^-1

    tau = shear_stress(yp, pv, shear_rate)
    print(f"PV (converted): {pv} Pa.s")
    print(f"Shear stress: {tau:.1f} Pa")
    # Expected result (from hand calc): 18 Pa

    print(hole_cleaning_indicator(yp, pv))