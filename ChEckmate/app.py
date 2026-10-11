
import streamlit as st

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="ChEckmate! | Unit Converter",
    page_icon="⚗️",
    layout="wide"
)

# --------------------------------------------------
# DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #F2F7F5;
    color: #102A43;
}

[data-testid="stSidebar"] {
    background-color: #102A43;
}

[data-testid="stSidebar"] * {
    color: #F2F7F5;
}

.hero {
    background: linear-gradient(120deg, #102A43, #176B70);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
}

.hero h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    color: #D5F5EF;
    font-size: 16px;
}

div.stButton > button {
    background-color: #176B70;
    color: white;
    border-radius: 10px;
    border: none;
    min-height: 44px;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #102A43;
    color: white;
    border: 1px solid #43D9C3;
}

.result {
    background-color: #DDF7F0;
    padding: 22px;
    border-left: 5px solid #176B70;
    border-radius: 12px;
    margin-top: 20px;
}

.result-label {
    color: #176B70;
    font-size: 14px;
    font-weight: 600;
}

.result-value {
    color: #102A43;
    font-size: 28px;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.small-note {
    color: #526777;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CONVERSION DATA
# Each factor converts the unit to its SI base unit.
# --------------------------------------------------

CONVERSIONS = {
    "Length": {
        "Meter (m)": 1,
        "Kilometer (km)": 1000,
        "Centimeter (cm)": 0.01,
        "Millimeter (mm)": 0.001,
        "Micrometer (µm)": 1e-6,
        "Inch (in)": 0.0254,
        "Foot (ft)": 0.3048,
        "Yard (yd)": 0.9144,
        "Mile (mi)": 1609.344
    },

    "Volume": {
        "Cubic meter (m³)": 1,
        "Liter (L)": 0.001,
        "Milliliter (mL)": 1e-6,
        "Cubic centimeter (cm³)": 1e-6,
        "Cubic millimeter (mm³)": 1e-9,
        "Cubic foot (ft³)": 0.028316846592,
        "Cubic inch (in³)": 1.6387064e-5,
        "US gallon (gal)": 0.003785411784,
        "US fluid ounce (fl oz)": 2.95735295625e-5,
        "US barrel (bbl)": 0.158987294928
    },

    "Mass": {
        "Kilogram (kg)": 1,
        "Gram (g)": 0.001,
        "Milligram (mg)": 1e-6,
        "Metric tonne (t)": 1000,
        "Pound mass (lbm)": 0.45359237,
        "Ounce (oz)": 0.028349523125,
        "Slug (slug)": 14.59390294
    },

    "Density": {
        "Kilogram per cubic meter (kg/m³)": 1,
        "Gram per cubic centimeter (g/cm³)": 1000,
        "Kilogram per liter (kg/L)": 1000,
        "Gram per liter (g/L)": 1,
        "Pound per cubic foot (lb/ft³)": 16.01846337,
        "Pound per US gallon (lb/gal)": 119.8264273
    },

    "Dynamic Viscosity": {
        "Pascal-second (Pa·s)": 1,
        "Millipascal-second (mPa·s)": 0.001,
        "Centipoise (cP)": 0.001,
        "Poise (P)": 0.1,
        "Pound per foot-second (lb/(ft·s))": 1.48816394
    },

    "Energy": {
        "Joule (J)": 1,
        "Kilojoule (kJ)": 1000,
        "Calorie (cal)": 4.184,
        "Kilocalorie (kcal)": 4184,
        "Watt-hour (Wh)": 3600,
        "Kilowatt-hour (kWh)": 3600000,
        "British thermal unit (BTU)": 1055.05585262,
        "Foot-pound force (ft·lbf)": 1.355817948
    }
}

# Additional quantities for the SI ↔ English category.
SYSTEM_CONVERSIONS = {
    "Length": CONVERSIONS["Length"],

    "Volume": CONVERSIONS["Volume"],

    "Mass": CONVERSIONS["Mass"],

    "Pressure": {
        "Pascal (Pa)": 1,
        "Kilopascal (kPa)": 1000,
        "Megapascal (MPa)": 1e6,
        "Bar (bar)": 100000,
        "Atmosphere (atm)": 101325,
        "Pound per square inch (psi)": 6894.757293,
        "Millimeter of mercury (mmHg)": 133.322387
    },

    "Force": {
        "Newton (N)": 1,
        "Kilonewton (kN)": 1000,
        "Pound-force (lbf)": 4.448221615,
        "Kilogram-force (kgf)": 9.80665
    },

    "Energy": CONVERSIONS["Energy"],

    "Power": {
        "Watt (W)": 1,
        "Kilowatt (kW)": 1000,
        "Megawatt (MW)": 1e6,
        "Horsepower (hp)": 745.699872,
        "BTU per hour (BTU/h)": 0.29307107
    },

    "Density": CONVERSIONS["Density"],

    "Dynamic Viscosity": CONVERSIONS["Dynamic Viscosity"],

    "Volumetric Flow Rate": {
        "Cubic meter per second (m³/s)": 1,
        "Cubic meter per hour (m³/h)": 1 / 3600,
        "Liter per second (L/s)": 0.001,
        "Liter per minute (L/min)": 0.001 / 60,
        "Liter per hour (L/h)": 0.001 / 3600,
        "US gallon per minute (US gpm)": 0.003785411784 / 60,
        "Cubic foot per second (ft³/s)": 0.028316846592
    }
}

# --------------------------------------------------
# TEMPERATURE CONVERSION
# Convert to Celsius first, then to the target unit.
# --------------------------------------------------

TEMPERATURE_UNITS = [
    "Celsius (°C)",
    "Fahrenheit (°F)",
    "Kelvin (K)"
]


def to_celsius(value, unit):
    if unit == "Celsius (°C)":
        return value
    elif unit == "Fahrenheit (°F)":
        return (value - 32) * 5 / 9
    else:
        return value - 273.15


def from_celsius(value, unit):
    if unit == "Celsius (°C)":
        return value
    elif unit == "Fahrenheit (°F)":
        return value * 9 / 5 + 32
    else:
        return value + 273.15


def convert_temperature(value, from_unit, to_unit):
    celsius_value = to_celsius(value, from_unit)
    return from_celsius(celsius_value, to_unit)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

st.image(str(LOGO_PATH), use_container_width=True)

category = st.selectbox(
        "CONVERSION CATEGORY",
        [
            "Length",
            "Volume",
            "Mass",
            "Temperature",
            "Density",
            "Dynamic Viscosity",
            "Energy",
            "SI ↔ English Units"
        ]
    )

            st.divider()
    st.markdown("### About")
    st.write(
        "A unit conversion tool designed for "
        "Chemical Engineering students."
    )

    st.caption("Study smart. Convert accurately.")

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.image("assets/logo.png", use_container_width=True)

# --------------------------------------------------
# CONVERTER TITLE AND DESCRIPTION
# --------------------------------------------------

DESCRIPTIONS = {
    "Length": "Convert distances, dimensions, and pipe lengths.",
    "Volume": "Convert liquid volumes and equipment volumes.",
    "Mass": "Convert mass measurements used in calculations.",
    "Temperature": "Convert Celsius, Fahrenheit, and Kelvin.",
    "Density": "Convert mass per unit volume.",
    "Dynamic Viscosity": "Convert a fluid's resistance to flow.",
    "Energy": "Convert energy and heat quantities.",
    "SI ↔ English Units": (
        "Convert common engineering quantities between SI "
        "and English units, including pressure, force, power, "
        "density, viscosity, and flow rate."
    )
}

if category == "Dynamic Viscosity":
    display_category = "Dynamic Viscosity"
elif category == "SI ↔ English Units":
    display_category = "SI ↔ English Units"
else:
    display_category = category

st.subheader(f"{display_category} Converter")
st.write(DESCRIPTIONS[category])

# --------------------------------------------------
# SELECT CONVERSION TYPE
# --------------------------------------------------

if category == "Temperature":
    units = TEMPERATURE_UNITS
    quantity = None

elif category == "SI ↔ English Units":
    quantity = st.selectbox(
        "Engineering quantity",
        list(SYSTEM_CONVERSIONS.keys())
    )
    units = list(SYSTEM_CONVERSIONS[quantity].keys())

else:
    quantity = category
    units = list(CONVERSIONS[category].keys())

# --------------------------------------------------
# INPUTS
# --------------------------------------------------

st.divider()

col1, col2, col3 = st.columns([1.2, 1, 1])

with col1:
    value = st.number_input(
        "Value to convert",
        value=1.0,
        format="%.8g"
    )

with col2:
    from_unit = st.selectbox(
        "From",
        units,
        key=f"from_{category}"
    )

with col3:
    to_unit = st.selectbox(
        "To",
        units,
        index=1 if len(units) > 1 else 0,
        key=f"to_{category}"
    )

convert_button = st.button(
    "Convert Units",
    use_container_width=True
)

# --------------------------------------------------
# CALCULATION
# --------------------------------------------------

if convert_button:

    if category == "Temperature":
        result = convert_temperature(
            value,
            from_unit,
            to_unit
        )

    else:
        if category == "SI ↔ English Units":
            conversion_table = SYSTEM_CONVERSIONS[quantity]
        else:
            conversion_table = CONVERSIONS[category]

        # Convert source value to the SI base unit,
        # then convert the base value to the target unit.
        result = (
            value
            * conversion_table[from_unit]
            / conversion_table[to_unit]
        )

    # Display result
    st.markdown(f"""
    <div class="result">
        <div class="result-label">CONVERSION RESULT</div>
        <div class="result-value">{result:.10g} {to_unit}</div>
        <p>{value:.10g} {from_unit} = {result:.10g} {to_unit}</p>
    </div>
    """, unsafe_allow_html=True)

    # Show calculation details
    with st.expander("Show calculation details"):
        if category == "Temperature":
            st.write("Temperature conversion uses the appropriate formula.")

            if from_unit == "Celsius (°C)" and to_unit == "Fahrenheit (°F)":
                st.latex(r"^\circ F = \frac{9}{5}(^\circ C) + 32")
            elif from_unit == "Fahrenheit (°F)" and to_unit == "Celsius (°C)":
                st.latex(r"^\circ C = \frac{5}{9}(^\circ F - 32)")
            elif from_unit == "Celsius (°C)" and to_unit == "Kelvin (K)":
                st.latex(r"K = ^\circ C + 273.15")
            elif from_unit == "Kelvin (K)" and to_unit == "Celsius (°C)":
                st.latex(r"^\circ C = K - 273.15")
            else:
                st.write(
                    "The conversion passes through Celsius "
                    "using the correct temperature relationship."
                )

        else:
            st.write("General conversion formula:")
            st.latex(
                r"\text{Result} = \text{Input}"
                r"\times \frac{\text{Source factor}}"
                r"{\text{Target factor}}"
            )

            st.write(f"Input value: {value:g}")
            st.write(f"Source unit: {from_unit}")
            st.write(f"Target unit: {to_unit}")
            st.write(f"Calculated result: {result:.10g}")

    # Copy-friendly result
    st.code(f"{value:.10g} {from_unit} = {result:.10g} {to_unit}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "ChEckmate! | Chemical Engineering Unit Converter | Student Project"
)
st.caption(
    "Always verify units and significant figures before using "
    "conversion results in engineering design calculations."
)
