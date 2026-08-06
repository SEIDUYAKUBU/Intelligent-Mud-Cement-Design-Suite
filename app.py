"""
app.py
-------
PyMudCement-Optima - Streamlit GUI
PENG 258 Capstone Project

Ties together the fluids, rheology, hydraulics, and cementing backend modules
into a single interactive web app.

Run with: streamlit run app.py
"""

import streamlit as st
from backend.fluids import minimum_mud_weight, check_mud_weight_window
from backend.rheology import shear_stress, pv_from_cp, hole_cleaning_indicator
from backend.hydraulics import annular_pressure_loss, equivalent_circulating_density
from backend.cementing import inches_to_metres, annular_volume, m3_to_bbl, plug_bumping_pressure

st.set_page_config(page_title="PyMudCement-Optima", layout="wide")

st.title("🛢️ PyMudCement-Optima")
st.caption("Intelligent Mud & Cement Design Suite — PENG 258 Capstone Project")

tab1, tab2, tab3 = st.tabs(["Drilling Fluids & Hydraulics", "Cementing Design", "About"])

# ---------------------------------------------------------------------------
# TAB 1: Drilling Fluids & Hydraulics
# ---------------------------------------------------------------------------
with tab1:
    st.header("Drilling Fluids & Hydraulics Engine")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Well & Pressure Data")
        tvd = st.number_input("True Vertical Depth (m)", min_value=1.0, value=2500.0, step=50.0)
        pore_pressure_mpa = st.number_input("Formation Pore Pressure (MPa)", min_value=0.0, value=30.0, step=1.0)
        frac_pressure_mpa = st.number_input("Formation Fracture Pressure (MPa)", min_value=0.0, value=45.0, step=1.0)
        proposed_mw = st.number_input("Proposed Mud Weight (kg/m³)", min_value=0.0, value=1250.0, step=10.0)

        st.subheader("Mud Rheology (from Mud Report)")
        yp = st.number_input("Yield Point, YP (Pa)", min_value=0.0, value=8.0, step=0.5)
        pv_cp = st.number_input("Plastic Viscosity, PV (cP)", min_value=0.0, value=20.0, step=1.0)
        shear_rate = st.number_input("Shear Rate (s⁻¹)", min_value=0.0, value=500.0, step=10.0)

    with col2:
        st.subheader("Results")

        pore_pa = pore_pressure_mpa * 1_000_000
        frac_pa = frac_pressure_mpa * 1_000_000

        min_mw = minimum_mud_weight(pore_pa, tvd)
        st.metric("Minimum Required Mud Weight", f"{min_mw:.1f} kg/m³")

        window_result = check_mud_weight_window(proposed_mw, pore_pa, frac_pa, tvd)
        if window_result.startswith("WARNING"):
            st.error(window_result)
        else:
            st.success(window_result)

        pv_pas = pv_from_cp(pv_cp)
        tau = shear_stress(yp, pv_pas, shear_rate)
        st.metric("Shear Stress", f"{tau:.1f} Pa")

        cleaning_result = hole_cleaning_indicator(yp, pv_pas)
        if "LOW" in cleaning_result:
            st.warning(cleaning_result)
        else:
            st.info(cleaning_result)

        st.subheader("Annular Hydraulics (ECD)")
        flow_rate = st.number_input("Flow Rate (L/s)", min_value=0.1, value=25.0, step=1.0)
        hole_d_in = st.number_input("Hole/Casing ID (in)", min_value=1.0, value=8.5, step=0.125)
        pipe_od_in = st.number_input("Drillpipe OD (in)", min_value=1.0, value=5.0, step=0.125)
        section_length = st.number_input("Annular Section Length (m)", min_value=1.0, value=2500.0, step=50.0)

        try:
            dp = annular_pressure_loss(
                pv_pas, yp, flow_rate / 1000, inches_to_metres(hole_d_in),
                inches_to_metres(pipe_od_in), section_length
            )
            ecd = equivalent_circulating_density(proposed_mw, dp, tvd)
            st.metric("Annular Pressure Loss", f"{dp / 1000:.1f} kPa")
            st.metric("ECD", f"{ecd:.1f} kg/m³")

            if ecd * 9.81 * tvd > frac_pa:
                st.error("WARNING: ECD exceeds fracture gradient equivalent — risk of lost circulation!")
        except ValueError as e:
            st.error(f"Input error: {e}")

# ---------------------------------------------------------------------------
# TAB 2: Cementing Design
# ---------------------------------------------------------------------------
with tab2:
    st.header("Cementing Engineering Module")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Casing & Hole Geometry")
        hole_diameter_in = st.number_input("Open Hole Diameter (in)", min_value=1.0, value=8.5, step=0.125, key="ch_hole")
        casing_od_in = st.number_input("Casing OD (in)", min_value=1.0, value=7.0, step=0.125, key="ch_casing")
        cement_length = st.number_input("Cemented Interval Length (m)", min_value=1.0, value=300.0, step=10.0)
        excess_pct = st.slider("Excess / Washout Factor (%)", 0, 100, 15)

        st.subheader("Fluid Densities")
        cement_density = st.number_input("Cement Slurry Density (kg/m³)", min_value=500.0, value=1900.0, step=10.0)
        displacement_density = st.number_input("Displacement Fluid Density (kg/m³)", min_value=500.0, value=1250.0, step=10.0)
        margin_kpa = st.number_input("Operational Safety Margin (kPa)", min_value=0.0, value=500.0, step=50.0)

    with col2:
        st.subheader("Results")

        try:
            hole_d_m = inches_to_metres(hole_diameter_in)
            casing_od_m = inches_to_metres(casing_od_in)

            vol_m3 = annular_volume(hole_d_m, casing_od_m, cement_length, excess_pct / 100)
            vol_bbl = m3_to_bbl(vol_m3)

            st.metric("Annular Cement Volume", f"{vol_m3:.2f} m³", f"{vol_bbl:.1f} bbl")

            p_bump = plug_bumping_pressure(cement_density, displacement_density, cement_length, margin_kpa * 1000)
            st.metric("Estimated Plug Bumping Pressure", f"{p_bump / 1000:,.1f} kPa")

        except ValueError as e:
            st.error(f"Input error: {e}")

        st.caption(
            "Note: this covers primary cementing volumetrics and plug bumping pressure. "
            "Additive database lookup and P&A plug sub-module are flagged as future work "
            "in the accompanying technical report."
        )

# ---------------------------------------------------------------------------
# TAB 3: About
# ---------------------------------------------------------------------------
with tab3:
    st.header("About PyMudCement-Optima")
    st.markdown("""
    **PENG 258: Drilling Engineering 1 — Capstone Project**

    This tool automates core drilling fluids and primary cementing calculations:

    - Minimum mud weight & safe operating window
    - Bingham-Plastic shear stress & hole cleaning indicator
    - Annular pressure loss & Equivalent Circulating Density (ECD)
    - Annular cement volume
    - Plug bumping pressure

    All calculations are dynamically evaluated from user input — no hardcoded well data.
    See the accompanying technical report for mathematical validation and
    comparative analysis against industry benchmarks.
    """)