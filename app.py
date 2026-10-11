
from pathlib import Path
import base64
import random
import sqlite3
import time
import html

import streamlit as st


try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(*args, **kwargs):
        return None




BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

BG_PATH = ASSETS_DIR / "notebook_bg.jpg"
LOGO_PATH = ASSETS_DIR / "logo.png"
DB_PATH = BASE_DIR / "checkmate_scores.db"




st.set_page_config(
    page_title="ChEckmate! | Chem Eng Converter",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)




DEEP = "#00110F"
DARK_TEAL = "#073331"
OCEAN = "#087782"
BRIGHT = "#0797A5"
SEAFOAM = "#88B8B6"
PAPER = "#F2E8D6"
INK = "#536CA6"




def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS scores (
                player TEXT PRIMARY KEY,
                best_score INTEGER NOT NULL DEFAULT 0
            )"""
        )


def get_best_score(player):
    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT best_score FROM scores WHERE player = ?",
            (player,)
        ).fetchone()

    return row[0] if row else 0


def save_best_score(player, score):
    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO scores(player, best_score)
               VALUES(?, ?)
               ON CONFLICT(player)
               DO UPDATE SET best_score =
               MAX(best_score, excluded.best_score)""",
            (player, int(score)),
        )




UNITS = {
    "Length": {
        "Meter (m)": 1,
        "Kilometer (km)": 1000,
        "Centimeter (cm)": 0.01,
        "Millimeter (mm)": 0.001,
        "Micrometer (µm)": 1e-6,
        "Mile (mi)": 1609.344,
        "Yard (yd)": 0.9144,
        "Foot (ft)": 0.3048,
        "Inch (in)": 0.0254,
    },

    "Area": {
        "Square meter (m²)": 1,
        "Square kilometer (km²)": 1e6,
        "Square centimeter (cm²)": 1e-4,
        "Hectare (ha)": 1e4,
        "Square foot (ft²)": 0.09290304,
        "Acre (ac)": 4046.8564224,
    },

    "Volume": {
        "Cubic meter (m³)": 1,
        "Liter (L)": 0.001,
        "Milliliter (mL)": 1e-6,
        "Cubic centimeter (cm³)": 1e-6,
        "US gallon (gal)": 0.003785411784,
        "US fluid ounce (fl oz)": 2.95735295625e-5,
        "Cubic foot (ft³)": 0.028316846592,
    },

    "Mass": {
        "Kilogram (kg)": 1,
        "Gram (g)": 0.001,
        "Milligram (mg)": 1e-6,
        "Metric ton (t)": 1000,
        "Pound (lb)": 0.45359237,
        "Ounce (oz)": 0.028349523125,
    },

    "Density": {
        "kg/m³": 1,
        "g/cm³": 1000,
        "g/mL": 1000,
        "lb/ft³": 16.01846337,
        "lb/gal (US)": 119.8264273,
    },

    "Pressure": {
        "Pascal (Pa)": 1,
        "Kilopascal (kPa)": 1000,
        "Megapascal (MPa)": 1e6,
        "Bar (bar)": 100000,
        "Atmosphere (atm)": 101325,
        "Torr (Torr)": 133.3223684,
        "psi (lbf/in²)": 6894.757293,
    },

    "Force": {
        "Newton (N)": 1,
        "Kilonewton (kN)": 1000,
        "Dyne (dyn)": 1e-5,
        "Pound-force (lbf)": 4.4482216153,
    },

    "Energy": {
        "Joule (J)": 1,
        "Kilojoule (kJ)": 1000,
        "Calorie (cal)": 4.184,
        "Kilocalorie (kcal)": 4184,
        "Watt-hour (Wh)": 3600,
        "Kilowatt-hour (kWh)": 3.6e6,
        "BTU (IT)": 1055.05585262,
    },

    "Power": {
        "Watt (W)": 1,
        "Kilowatt (kW)": 1000,
        "Megawatt (MW)": 1e6,
        "Horsepower (hp)": 745.6998716,
    },

    "Time": {
        "Second (s)": 1,
        "Minute (min)": 60,
        "Hour (h)": 3600,
        "Day (d)": 86400,
    },

    "Dynamic Viscosity": {
        "Pa·s": 1,
        "mPa·s": 1e-3,
        "Poise (P)": 0.1,
        "Centipoise (cP)": 0.001,
        "lb/(ft·s)": 1.48816394,
    },

    "Volumetric Flow Rate": {
        "m³/s": 1,
        "m³/h": 1 / 3600,
        "L/s": 0.001,
        "L/min": 0.001 / 60,
        "L/h": 0.001 / 3600,
        "US gal/min (gpm)": 0.003785411784 / 60,
        "ft³/s": 0.028316846592,
    },

    "Temperature": {
        "Celsius (°C)": "C",
        "Fahrenheit (°F)": "F",
        "Kelvin (K)": "K",
    },
}



def convert(value, category, from_unit, to_unit):

    if category == "Temperature":

        if from_unit.startswith("Celsius"):
            kelvin = value + 273.15

        elif from_unit.startswith("Fahrenheit"):
            kelvin = (value - 32) * 5 / 9 + 273.15

        else:
            kelvin = value

        if to_unit.startswith("Celsius"):
            return kelvin - 273.15

        if to_unit.startswith("Fahrenheit"):
            return (kelvin - 273.15) * 9 / 5 + 32

        return kelvin

    base_value = value * UNITS[category][from_unit]

    return base_value / UNITS[category][to_unit]


def format_num(value):

    if value == 0:
        return "0"

    if abs(value) >= 1e7 or abs(value) < 1e-4:
        return f"{value:.6e}"

    return f"{value:,.8g}"




def inject_style():

   
    bg_css = ""
    if BG_PATH.exists():
        encoded_bg = base64.b64encode(BG_PATH.read_bytes()).decode("utf-8")
        bg_css = f'url("data:image/jpeg;base64,{encoded_bg}")'

    background_image_css = (
        f"linear-gradient(rgba(242,232,214,.10), rgba(242,232,214,.10)), {bg_css}"
        if bg_css
        else "linear-gradient(rgba(242,232,214,.10), rgba(242,232,214,.10))"
    )

    st.markdown(f"""
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Kalam:wght@400;700&family=Nunito:wght@400;600;700;800;900&display=swap'
    );

    :root {{
      --deep: {DEEP};
      --dark: {DARK_TEAL};
      --ocean: {OCEAN};
      --bright: {BRIGHT};
      --seafoam: {SEAFOAM};
      --paper: {PAPER};
      --ink: {INK};
    }}


    .stApp {{
      background-color: var(--paper);
      background-image: {background_image_css};
      background-size: cover;
      background-position: center top;
      background-attachment: fixed;
      background-repeat: no-repeat;
      color: var(--deep);
      font-family: 'Nunito', sans-serif;
    }}

    [data-testid="stHeader"] {{
      background: rgba(242,232,214,.88);
    }}

    [data-testid="stSidebar"] {{
      background: #e7dcc7;
    }}

    [data-testid="stSidebar"] * {{
      color: var(--deep);
    }}


    h1, h2, h3, h4 {{
      font-family: 'Kalam', cursive !important;
      color: var(--dark) !important;
      font-weight: 900 !important;
      text-shadow: 0 1px 1px rgba(255,255,255,.85);
    }}

    p, label, span, div {{
      font-family: 'Nunito', sans-serif;
    }}

    .block-container {{
      padding-top: 1.4rem;
      padding-bottom: 2.5rem;
      max-width: 1150px;
    }}


    .brand-title {{
      font-family: 'Kalam', cursive !important;
      font-size: clamp(2.7rem, 6vw, 4.8rem);
      line-height: 1.15;
      color: #073331 !important;
      font-weight: 900 !important;
      text-align: center;
      margin: .25rem 0;
      -webkit-text-stroke: .7px #00110F;
      text-shadow:
        2px 2px 0 #F2E8D6,
        3px 3px 0 rgba(0,17,15,.45);
    }}


    .brand-sub {{
      text-align: center;
      font-size: 1.05rem;
      color: #173B3B !important;
      font-weight: 900 !important;
      margin-bottom: 1.1rem;
      text-shadow: 0 1px 2px rgba(255,255,255,.95);
    }}

    .doodle-strip {{
      text-align: center;
      font-size: 1.5rem;
      letter-spacing: .5rem;
      color: var(--ocean);
      margin: .4rem 0 1rem;
    }}


    .paper-card {{
      background: rgba(255,250,240,.94);
      color: #00110F !important;
      border: 2px solid rgba(8,119,130,.55);
      border-radius: 22px;
      padding: 1.25rem 1.35rem;
      box-shadow: 5px 6px 0 rgba(8,119,130,.16);
    }}

    .welcome-box {{
      background: rgba(255,250,240,.94);
      color: #00110F !important;
      border: 2px solid rgba(8,119,130,.55);
      border-radius: 26px;
      padding: 2rem 1.2rem;
      text-align: center;
      box-shadow: 7px 8px 0 rgba(8,119,130,.18);
    }}


    .result-card {{
      background: var(--dark);
      color: #FFF7E8 !important;
      border-radius: 20px;
      padding: 1.25rem;
      border: 2px solid var(--bright);
      text-align: center;
    }}

    .result-label {{
      color: #BFE4DF !important;
      font-size: .85rem;
      font-weight: 800 !important;
      text-transform: uppercase;
      letter-spacing: .12rem;
    }}

    .result-number {{
      color: #FFF7E8 !important;
      font-family: 'DM Mono', monospace !important;
      font-size: clamp(1.7rem, 4vw, 2.8rem);
      font-weight: 900 !important;
      overflow-wrap: anywhere;
    }}

    /* Buttons */

    .stButton > button {{
      border-radius: 14px;
      border: 1px solid var(--ocean);
      background: var(--ocean);
      color: white !important;
      font-weight: 900 !important;
      min-height: 2.8rem;
      text-shadow: none;
    }}

    .stButton > button:hover {{
      background: var(--dark);
      border-color: var(--dark);
      color: white !important;
    }}


    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {{
      border-radius: 12px;
      border-color: rgba(8,119,130,.5);
      background: rgba(255,255,255,.95);
    }}

    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {{
      font-family: 'DM Mono', monospace !important;
      color: #FFFFFF !important;
      -webkit-text-fill-color: #FFFFFF !important;
      -webkit-text-stroke: 0 !important;
      caret-color: #FFFFFF !important;
      font-weight: 900 !important;
      text-shadow: none !important;
    }}

    [data-testid="stNumberInput"] div[data-baseweb="input"] > div,
    [data-testid="stTextInput"] div[data-baseweb="input"] > div {{
      background: #073331 !important;
      border: 2px solid #00110F !important;
      border-radius: 12px !important;
    }}

    [data-testid="stNumberInput"] input::placeholder,
    [data-testid="stTextInput"] input::placeholder {{
      color: #D9E6E4 !important;
      -webkit-text-fill-color: #D9E6E4 !important;
      -webkit-text-stroke: 0 !important;
      opacity: 1 !important;
    }}

    [data-baseweb="select"] *,
    [data-baseweb="input"] input {{
      color: #00110F !important;
      font-weight: 800 !important;
    }}

    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label {{
      color: #00110F !important;
      font-weight: 900 !important;
      text-shadow: 0 1px 2px rgba(255,255,255,.9);
    }}

    [data-testid="stNumberInput"] label,
    [data-testid="stTextInput"] label {{
      color: #FFFFFF !important;
      -webkit-text-stroke: .65px #000000;
      paint-order: stroke fill;
      text-shadow:
        -1px -1px 0 #000,
         1px -1px 0 #000,
        -1px  1px 0 #000,
         1px  1px 0 #000,
         0 1px 2px rgba(0,0,0,.35) !important;
      font-weight: 900 !important;
    }}


    .stApp,
    .stApp p,
    .stApp label,
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricValue"] {{
      color: #00110F !important;
      font-weight: 800 !important;
      text-shadow: 0 1px 2px rgba(255,255,255,.9);
    }}

    .tiny-note {{
      font-size: .86rem;
      color: #173B3B !important;
      font-weight: 800 !important;
      text-shadow: 0 1px 2px rgba(255,255,255,.95);
    }}

    /* Preserve light text on dark result cards */

    .result-card,
    .result-card div {{
      color: #FFF7E8 !important;
    }}

    .result-card .result-label {{
      color: #BFE4DF !important;
    }}

    .result-card .result-number {{
      color: #FFF7E8 !important;
    }}

    hr {{
      border-color: rgba(8,119,130,.3);
    }}

    </style>
    """, unsafe_allow_html=True)


inject_style()




defaults = {
    "screen": "welcome",
    "category": "Length",
    "game_active": False,
    "game_score": 0,
    "game_question": None,
    "game_deadline": None,
    "game_over": False,
    "game_feedback": "",
    "player_name": "Chemist",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value




def doodles():
    st.markdown(
        '<div class="doodle-strip">⚗︎　⌁　⚗︎</div>',
        unsafe_allow_html=True
    )


def logo_markup(width=360):
    if LOGO_PATH.exists():
        encoded_logo = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
        return (
            f'<img src="data:image/png;base64,{encoded_logo}" '
            f'alt="ChEckmate! logo" style="display:block;max-width:100%;'
            f'width:{width}px;height:auto;margin:.25rem auto;" />'
        )
    
    return (
        '<div style="text-align:center;color:#073331;font-weight:800;'
        'padding:1rem 0;">'
        'Your actual logo file is missing. Add it as '
        '<code>assets/logo.png</code>.'
        '</div>'
    )


def header():
    st.markdown(
        f'<div style="text-align:center">{logo_markup(300)}'
        '<div class="brand-sub">your unit conversion buddy</div>'
        '<div class="doodle-strip">⚗︎　⌁　⚗︎</div></div>',
        unsafe_allow_html=True
    )


def go(screen):
    st.session_state.screen = screen
    st.rerun()




if st.session_state.screen == "welcome":

    st.write("")
    st.write("")

    left, center, right = st.columns([1, 2.1, 1])

    with center:

        st.markdown(
            f'<div class="welcome-box">{logo_markup(390)}'
            '<div class="brand-sub">your unit conversion buddy</div>'
            '<div class="doodle-strip">⌬　⚗︎　∿　⚗︎　⌬</div></div>',
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "✦  TAP TO CONTINUE  ✦",
            use_container_width=True,
            key="welcome_continue"
        ):
            go("home")

        st.markdown(
            '<p style="text-align:center;'
            'font-family:Kalam,cursive;'
            'color:#073331;font-weight:900;'
            'text-shadow:0 1px 2px white;">'
            'Made for curious minds and unit-conversion emergencies.'
            '</p>',
            unsafe_allow_html=True
        )




elif st.session_state.screen == "home":

    header()

    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        if st.button("⚗️ Converter", use_container_width=True):
            go("home")

    with nav2:
        if st.button("⏱️ Beat the Units!", use_container_width=True):
            go("game")

    with nav3:
        if st.button("✎ About", use_container_width=True):
            go("about")

    st.markdown(
        '<div class="paper-card">',
        unsafe_allow_html=True
    )

    st.subheader("Unit converter")

    st.caption(
        "Choose a property, enter a value, then pick the units. "
        "Your answer updates when you press Convert."
    )

    categories = list(UNITS.keys())

    category = st.selectbox(
        "What are we converting today?",
        categories,
        index=categories.index(st.session_state.category)
    )

    st.session_state.category = category

    units = list(UNITS[category].keys())

    c1, c2, c3 = st.columns([1.2, 1, 1])

    with c1:
        value = st.number_input(
            "Value",
            value=1.0,
            format="%.8g",
            key="convert_value"
        )

    with c2:
        from_unit = st.selectbox(
            "From",
            units,
            key="from_unit"
        )

    with c3:
        to_unit = st.selectbox(
            "To",
            units,
            index=min(1, len(units) - 1),
            key="to_unit"
        )

    if st.button(
        "Convert it!  →",
        use_container_width=True,
        key="convert_button"
    ):
        try:
            result = convert(
                value,
                category,
                from_unit,
                to_unit
            )

            st.session_state["last_result"] = (
                value,
                category,
                from_unit,
                to_unit,
                result
            )

        except Exception as exc:
            st.error(f"Couldn't convert that value: {exc}")

    if "last_result" in st.session_state:

        old_value, old_category, old_from, old_to, result = (
            st.session_state["last_result"]
        )

        if old_category == category:

            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-label">
                        Your converted result
                    </div>
                    <div class="result-number">
                        {html.escape(format_num(result))}
                    </div>
                    <div>{html.escape(old_to)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")

            with st.expander("Show the calculation"):

                if category == "Temperature":

                    st.write(
                        f"Convert {old_value:g} {old_from} to "
                        f"{old_to} using the temperature "
                        f"conversion relationship."
                    )

                    st.latex(r"K = {}^\circ C + 273.15")

                    st.latex(
                        r"K = ({}^\circ F - 32)"
                        r"\frac{5}{9} + 273.15"
                    )

                else:

                    factor_from = UNITS[category][old_from]
                    factor_to = UNITS[category][old_to]

                    st.write(
                        f"Step 1: Convert {old_value:g} "
                        f"{old_from} to the base unit."
                    )

                    st.latex(
                        fr"\text{{Base value}} = "
                        fr"{old_value:g}\times {factor_from:g}"
                        fr" = {old_value * factor_from:g}"
                    )

                    st.write(
                        "Step 2: Divide by the target unit's "
                        "base-unit factor."
                    )

                    st.latex(
                        fr"\text{{Result}} = "
                        fr"\frac{{{old_value * factor_from:g}}}"
                        fr"{{{factor_to:g}}} = {result:.8g}"
                    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown(
        '<p class="tiny-note">'
        'Notebook tip: always check the units before '
        'substituting values into an engineering equation.'
        '</p>',
        unsafe_allow_html=True
    )




elif st.session_state.screen == "game":

    header()

    if st.button("← Back to converter"):
        go("home")

    st.markdown(
        '<div class="paper-card">',
        unsafe_allow_html=True
    )

    st.subheader("Beat the Units!")

    st.write(
        "Answer as many quick conversion questions as you can. "
        "Each question gives you **15 seconds**."
    )

    player = st.text_input(
        "Player name (for your personal high score)",
        value=st.session_state.player_name,
        max_chars=24
    )

    st.session_state.player_name = player.strip() or "Chemist"

    best = get_best_score(st.session_state.player_name)

    top1, top2 = st.columns(2)

    top1.metric("This round", st.session_state.game_score)
    top2.metric("Personal best", best)

    quiz_units = [
        ("Length", "1 m = ? cm", 100, "cm"),
        ("Length", "2 km = ? m", 2000, "m"),
        ("Volume", "1 L = ? mL", 1000, "mL"),
        ("Mass", "1 kg = ? g", 1000, "g"),
        ("Pressure", "1 bar = ? kPa", 100, "kPa"),
        ("Energy", "1 kJ = ? J", 1000, "J"),
        ("Time", "2 min = ? s", 120, "s"),
        ("Power", "1 kW = ? W", 1000, "W"),
        ("Length", "1 ft = ? in", 12, "in"),
        ("Volume", "1 m³ = ? L", 1000, "L"),
        ("Mass", "500 g = ? kg", 0.5, "kg"),
        ("Pressure", "1 atm ≈ ? kPa", 101.325, "kPa"),
        ("Length", "1 in = ? mm", 25.4, "mm"),
        ("Area", "1 m² = ? cm²", 10000, "cm²"),
    ]

    def new_question():
        st.session_state.game_question = random.choice(quiz_units)

        
        st.session_state.game_deadline = time.time() + 15

        st.session_state.game_feedback = ""

    if not st.session_state.game_active and not st.session_state.game_over:

        if st.button("Start a round!", use_container_width=True):

            st.session_state.game_active = True
            st.session_state.game_over = False
            st.session_state.game_score = 0

            new_question()

            st.rerun()

    if st.session_state.game_active and not st.session_state.game_over:

        remaining = max(
            0,
            st.session_state.game_deadline - time.time()
        )

        if remaining <= 0:

            st.session_state.game_over = True
            st.session_state.game_active = False
            st.session_state.game_feedback = "Time's up!"

            save_best_score(
                st.session_state.player_name,
                st.session_state.game_score
            )

            st.rerun()

        
        st_autorefresh(
            interval=1000,
            limit=None,
            key="game_timer_refresh"
        )

        
        st.progress(remaining / 15)

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">TIME LEFT</div>
                <div class="result-number">
                    {remaining:.1f}s
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        question = st.session_state.game_question

        st.markdown(
            f'<h2 style="text-align:center;'
            f'font-family:Kalam,cursive;'
            f'color:#073331 !important;'
            f'text-shadow:0 1px 2px white;">'
            f'{html.escape(question[1])}</h2>',
            unsafe_allow_html=True
        )

        with st.form("answer_form", clear_on_submit=True):

            answer_text = st.text_input(
                "Your answer (number only)",
                placeholder="e.g. 1000"
            )

            submitted = st.form_submit_button("Submit answer")

        if submitted:

            try:
                user_answer = float(
                    answer_text.replace(",", "").strip()
                )

                correct = (
                    abs(user_answer - question[2])
                    <= max(1e-6, abs(question[2]) * 0.005)
                )

            except (ValueError, AttributeError):
                correct = False

            if (
                correct
                and time.time() <= st.session_state.game_deadline
            ):

                st.session_state.game_score += 1

                if (
                    st.session_state.game_score
                    > get_best_score(st.session_state.player_name)
                ):
                    save_best_score(
                        st.session_state.player_name,
                        st.session_state.game_score
                    )

                new_question()

                st.rerun()

            else:

                st.session_state.game_over = True
                st.session_state.game_active = False

                st.session_state.game_feedback = (
                    f"Not quite! The answer was "
                    f"{format_num(question[2])} {question[3]}."
                )

                save_best_score(
                    st.session_state.player_name,
                    st.session_state.game_score
                )

                st.rerun()

        st.caption(
            "Tip: enter the number only; units are shown in each "
            "question. Answers within 0.5% are accepted."
        )

    if st.session_state.game_over:

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">ROUND COMPLETE</div>
                <div class="result-number">
                    {st.session_state.game_score} point(s)
                </div>
                <div>
                    {html.escape(st.session_state.game_feedback)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if st.button("Play again", use_container_width=True):

            st.session_state.game_active = True
            st.session_state.game_over = False
            st.session_state.game_score = 0

            new_question()

            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.caption(
        "High scores are stored in a local SQLite database. "
        "On Streamlit Cloud, local files may reset when the app "
        "is redeployed or restarted."
    )




elif st.session_state.screen == "about":

    header()

    if st.button("← Back"):
        go("home")

    st.markdown(
        '<div class="paper-card">',
        unsafe_allow_html=True
    )

    st.subheader("About ChEckmate!")

    st.write(
        "A fun unit converter made for chemical engineering "
        "students and curious minds."
    )

    st.write(
        "Includes common engineering conversions for length, area, "
        "volume, mass, density, pressure, force, energy, power, "
        "time, viscosity, volumetric flow rate, and temperature."
    )

    

    st.markdown('</div>', unsafe_allow_html=True)




st.markdown(
    '<div style="text-align:center;'
    'color:#073331;font-family:Kalam,cursive;'
    'font-weight:900;text-shadow:0 1px 2px white;'
    'margin-top:2rem;">'
    'Made with curiosity, coffee, and a little chemistry. '
    '</div>',
    unsafe_allow_html=True
)
