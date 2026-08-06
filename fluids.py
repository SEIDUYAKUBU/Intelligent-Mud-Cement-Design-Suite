"""
fluids.py
----------
Drilling Fluids & Hydraulics Engine (PENG 258 Capstone - PyMudCement-Optima)

Handles:
- Hydrostatic pressure balance
- Minimum mud weight calculation
- Safe mud weight window check (pore pressure vs fracture gradient)

All inputs are dynamic (no hardcoded values) - pass in your own well data.
"""

G = 9.81  # Acceleration due to gravity, m/s^2 (physical constant, not a "hardcoded" well parameter)


def hydrostatic_pressure(mud_density_kg_m3: float, tvd_m: float, g: float = G) -> float:
    """
    Calculate hydrostatic pressure exerted by a column of drilling fluid.

    P_hyd = rho_mud * g * TVD

    Parameters
    ----------
    mud_density_kg_m3 : float
        Mud density in kg/m^3
    tvd_m : float
        True vertical depth in metres
    g : float
        Gravitational acceleration, default 9.81 m/s^2

    Returns
    -------
    float
        Hydrostatic pressure in Pascals (Pa)
    """
    return mud_density_kg_m3 * g * tvd_m


def minimum_mud_weight(pore_pressure_pa: float, tvd_m: float, g: float = G) -> float:
    """
    Calculate the minimum mud density required to balance formation pore pressure.

    rho_mud(min) = P_pore / (g * TVD)

    Parameters
    ----------
    pore_pressure_pa : float
        Formation pore pressure in Pascals (Pa)
    tvd_m : float
        True vertical depth in metres

    Returns
    -------
    float
        Minimum required mud density in kg/m^3
    """
    if tvd_m <= 0:
        raise ValueError("TVD must be greater than zero.")
    return pore_pressure_pa / (g * tvd_m)


def check_mud_weight_window(mud_density_kg_m3: float, pore_pressure_pa: float,
                             frac_pressure_pa: float, tvd_m: float, g: float = G) -> str:
    """
    Check whether a proposed mud weight sits within the safe operating window
    (above pore pressure equivalent, below fracture pressure equivalent).

    Parameters
    ----------
    mud_density_kg_m3 : float
        Proposed mud density in kg/m^3
    pore_pressure_pa : float
        Formation pore pressure in Pa
    frac_pressure_pa : float
        Formation fracture pressure in Pa
    tvd_m : float
        True vertical depth in metres

    Returns
    -------
    str
        Warning or confirmation message
    """
    min_required = minimum_mud_weight(pore_pressure_pa, tvd_m, g)
    max_allowed = minimum_mud_weight(frac_pressure_pa, tvd_m, g)  # same formula, using frac pressure

    if mud_density_kg_m3 < min_required:
        return (f"WARNING: Underbalanced. Mud weight {mud_density_kg_m3:.1f} kg/m3 is below "
                f"the minimum required {min_required:.1f} kg/m3. Risk of well control incident (kick).")
    elif mud_density_kg_m3 > max_allowed:
        return (f"WARNING: Overbalanced. Mud weight {mud_density_kg_m3:.1f} kg/m3 exceeds "
                f"the maximum allowed {max_allowed:.1f} kg/m3. Risk of formation fracture / lost circulation.")
    else:
        return (f"OK: Mud weight {mud_density_kg_m3:.1f} kg/m3 is within the safe operating "
                f"window ({min_required:.1f} - {max_allowed:.1f} kg/m3).")


# ---------------------------------------------------------------------------
# Quick manual test - run this file directly to validate against a hand calc
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example well data (matches the hand-calculation worked through earlier)
    tvd = 2500          # metres
    pore_p = 30_000_000  # Pa (30 MPa)

    min_mw = minimum_mud_weight(pore_p, tvd)
    print(f"Minimum mud weight required: {min_mw:.1f} kg/m3")
    # Expected result (from hand calc): ~1223 kg/m3

    # Example safe window check
    frac_p = 45_000_000  # Pa (45 MPa) - example fracture pressure
    proposed_mw = 1250   # kg/m3

    result = check_mud_weight_window(proposed_mw, pore_p, frac_p, tvd)
    print(result)