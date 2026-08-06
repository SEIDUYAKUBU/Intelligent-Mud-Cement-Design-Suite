"""
hydraulics.py
--------------
Drilling Fluids & Hydraulics Engine (PENG 258 Capstone - PyMudCement-Optima)

Handles:
- Equivalent Circulating Density (ECD)
- Basic annular frictional pressure loss estimate (Bingham-Plastic, laminar flow)

All inputs are dynamic (no hardcoded values) - pass in your own well/mud data.

Note: the annular pressure loss function here uses a simplified laminar-flow
Bingham-Plastic model suitable for a sophomore-level capstone. It assumes
laminar flow and does not check/handle turbulent flow regimes - flag this
as a stated simplification in your technical report.
"""

G = 9.81  # m/s^2


def annular_pressure_loss(plastic_viscosity_pa_s: float, yield_point_pa: float,
                           flow_rate_m3_s: float, hole_diameter_m: float,
                           pipe_od_m: float, length_m: float) -> float:
    """
    Estimate annular frictional pressure loss for laminar flow of a Bingham-Plastic
    fluid, using a simplified slot-flow approximation common in introductory
    drilling hydraulics teaching.

    dP = [ (PV * L * v) / (1000 * (D_hole - D_pipe)^2) ] + [ (YP * L) / (200 * (D_hole - D_pipe)) ]

    (Field-derived approximation, converted to consistent SI-friendly form for
    this capstone; velocities and diameters must be in metres/seconds.)

    Parameters
    ----------
    plastic_viscosity_pa_s : float
        Plastic viscosity (Pa.s)
    yield_point_pa : float
        Yield point (Pa)
    flow_rate_m3_s : float
        Volumetric flow rate (m^3/s)
    hole_diameter_m : float
        Open hole (or casing ID) diameter, m
    pipe_od_m : float
        Drillpipe/collar outer diameter, m
    length_m : float
        Length of the annular section, m

    Returns
    -------
    float
        Estimated frictional pressure loss in Pascals (Pa)
    """
    annular_gap = hole_diameter_m - pipe_od_m
    if annular_gap <= 0:
        raise ValueError("Hole diameter must be greater than pipe OD.")

    annular_area = (3.141592653589793 / 4) * (hole_diameter_m**2 - pipe_od_m**2)
    velocity = flow_rate_m3_s / annular_area  # m/s

    viscous_term = (plastic_viscosity_pa_s * length_m * velocity) / (annular_gap**2)
    yield_term = (yield_point_pa * length_m) / annular_gap

    return viscous_term + yield_term


def equivalent_circulating_density(mud_density_kg_m3: float, annular_pressure_loss_pa: float,
                                    tvd_m: float, g: float = G) -> float:
    """
    Calculate Equivalent Circulating Density (ECD) - the effective density the
    formation experiences while circulating, accounting for annular friction.

    ECD = rho_mud + (dP_annulus / (g * TVD))

    Parameters
    ----------
    mud_density_kg_m3 : float
        Static mud density, kg/m^3
    annular_pressure_loss_pa : float
        Annular frictional pressure loss, Pa
    tvd_m : float
        True vertical depth, m

    Returns
    -------
    float
        ECD in kg/m^3
    """
    if tvd_m <= 0:
        raise ValueError("TVD must be greater than zero.")
    return mud_density_kg_m3 + (annular_pressure_loss_pa / (g * tvd_m))


# ---------------------------------------------------------------------------
# Quick manual test - run this file directly to validate against a hand calc
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example data (matches the ECD hand-calculation worked through earlier)
    mud_density = 1250      # kg/m3
    dp_annulus = 2_000_000  # Pa (given directly here for validation purposes)
    tvd = 2500               # m

    ecd = equivalent_circulating_density(mud_density, dp_annulus, tvd)
    print(f"ECD: {ecd:.1f} kg/m3")
    # Expected result (from hand calc): ~1331.6 kg/m3