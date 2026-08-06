"""
cementing.py
-------------
Cementing Engineering Module (PENG 258 Capstone - PyMudCement-Optima)

Handles:
- Annular volumetric calculations for cement slurry / spacer / displacement fluid
- Simple unit helpers (inches -> metres, m^3 -> barrels)

All inputs are dynamic (no hardcoded values) - pass in your own well/casing data.
"""

import math

M3_TO_BBL = 6.2898  # 1 cubic metre = 6.2898 US barrels


def inches_to_metres(inches: float) -> float:
    """Convert a diameter in inches to metres."""
    return inches * 0.0254


def annular_volume(hole_diameter_m: float, casing_od_m: float, length_m: float,
                    excess_factor: float = 0.0) -> float:
    """
    Calculate the annular volume between the open hole and the casing string,
    for a given cemented interval length, including an excess/washout allowance.

    V_ann = (pi/4) * (D_hole^2 - D_casing^2) * L * (1 + We)

    Parameters
    ----------
    hole_diameter_m : float
        Diameter of the open hole, in metres
    casing_od_m : float
        Outer diameter of the casing string, in metres
    length_m : float
        Length of the cemented interval, in metres
    excess_factor : float
        Open-hole excess/washout factor (e.g. 0.15 for 15% excess). Default 0 (no excess).

    Returns
    -------
    float
        Annular volume in cubic metres (m^3)
    """
    if hole_diameter_m <= casing_od_m:
        raise ValueError("Hole diameter must be greater than casing OD - casing cannot exceed hole size.")
    if length_m <= 0:
        raise ValueError("Length must be greater than zero.")
    if excess_factor < 0:
        raise ValueError("Excess factor cannot be negative.")

    area_term = (math.pi / 4) * (hole_diameter_m**2 - casing_od_m**2)
    return area_term * length_m * (1 + excess_factor)


def m3_to_bbl(volume_m3: float) -> float:
    """Convert a volume from cubic metres to US barrels."""
    return volume_m3 * M3_TO_BBL


def plug_bumping_pressure(cement_density_kg_m3: float, displacement_density_kg_m3: float,
                           cement_length_m: float, margin_pa: float = 500_000, g: float = 9.81) -> float:
    """
    Estimate the plug bumping pressure - the pressure spike expected when the top
    cementing plug lands on the float collar, used to set safe operational limits
    for the rig crew.

    P_bump = (rho_cement - rho_displacement) * g * L_cement + P_margin

    Parameters
    ----------
    cement_density_kg_m3 : float
        Cement slurry density, kg/m^3
    displacement_density_kg_m3 : float
        Displacement fluid density, kg/m^3
    cement_length_m : float
        Length of the cement column, m
    margin_pa : float
        Additional operational safety margin (friction, surface losses), Pa.
        Default 500,000 Pa (0.5 MPa) - a reasonable teaching-level assumption;
        state this assumption explicitly in your technical report.
    g : float
        Gravitational acceleration, default 9.81 m/s^2

    Returns
    -------
    float
        Estimated plug bumping pressure in Pascals (Pa)
    """
    if cement_length_m <= 0:
        raise ValueError("Cement column length must be greater than zero.")
    if margin_pa < 0:
        raise ValueError("Margin cannot be negative.")

    density_diff = cement_density_kg_m3 - displacement_density_kg_m3
    hydrostatic_diff = density_diff * g * cement_length_m
    return hydrostatic_diff + margin_pa


# ---------------------------------------------------------------------------
# Quick manual test - run this file directly to validate against a hand calc
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example well data (matches the hand-calculation worked through earlier)
    hole_d = inches_to_metres(8.5)     # 8.5" hole
    casing_od = inches_to_metres(7.0)  # 7" casing
    interval_length = 300              # metres
    excess = 0.15                      # 15% excess

    vol_m3 = annular_volume(hole_d, casing_od, interval_length, excess)
    vol_bbl = m3_to_bbl(vol_m3)

    print(f"Hole diameter: {hole_d:.4f} m")
    print(f"Casing OD: {casing_od:.4f} m")
    print(f"Annular volume: {vol_m3:.4f} m3")
    # Expected result (from hand calc): ~4.06 m3
    print(f"Annular volume: {vol_bbl:.2f} bbl")

    # Plug bumping pressure example (matches the hand-calculation worked through earlier)
    cement_density = 1900        # kg/m3
    displacement_density = 1250  # kg/m3
    p_bump = plug_bumping_pressure(cement_density, displacement_density, interval_length)
    print(f"Plug bumping pressure: {p_bump:,.0f} Pa ({p_bump / 1000:.1f} kPa)")
    # Expected result (from hand calc): ~2,412,950 Pa (~2.41 MPa)