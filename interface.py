import streamlit as st
import json
import os
import sys
import base64

#PASSWORD = "maneko"

#if "auth" not in st.session_state:
#    st.session_state.auth = False

# Affichage du champ mot de passe uniquement si pas authentifié
#if not st.session_state.auth:
#    st.markdown("<h3>🔒 Accès sécurisé</h3>", unsafe_allow_html=True)
#    pwd = st.text_input("Entrez le mot de passe :", type="password")

#    if pwd == PASSWORD:
#        st.session_state.auth = True
#        st.rerun()  # Recharger l’interface après connexion

#    st.stop()

if "options" not in st.session_state:
    st.session_state["options"] = {}



# Masquer le menu, le header et le footer Streamlit
hide_streamlit_style = """
<style>
MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --------------------------------------------------------------------
# Setup chemin pour accéder au solver existant
# --------------------------------------------------------------------
def load_json(path):
    """Charge un fichier JSON situé dans simulateur_ui ou ses sous-dossiers."""
    full_path = os.path.join(os.path.dirname(__file__), path)
    with open(full_path, "r") as f:
        return json.load(f)

# --------------------------------------------------------------------
# Setup chemin pour accéder au solver existant
# --------------------------------------------------------------------
BASE_PATH = os.path.abspath("../simulateur_minimal19")
sys.path.append(BASE_PATH)

from solver_v19.solver import solve
from solver_v19.geometry import get_geometry
from solver_v19.solver import select_loader_name

# --------------------------------------------------------------------
# Configuration style constructeur
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Simulateur de Stabilité - MANEKO",
    page_icon="assets/manekowhite.ico",
    layout="wide"
)

st.markdown("""
<style>
/* iPhone vertical */
@media only screen and (max-width: 812px) {

    /* Réduction des marges générales */
    .block-container {
        padding-left: 5px !important;
        padding-right: 5px !important;
    }

    /* Réduction globale des tailles de texte */
    html, body, .stApp {
        -webkit-text-size-adjust: 90% !important;
        font-size: 14px !important;
    }

    /* Titres */
    h1 { font-size: 24px !important; }
    h2 { font-size: 18px !important; }
    h3 { font-size: 12px !important; }

    /* Boutons */
    button {
        transform: scale(0.9) !important;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        transform: scale(0.9);
        
    }
}
</style>
""", unsafe_allow_html=True)

# Masquer le menu Sreamlit manageApp
st.markdown("""
<style>
/* Si jamais Streamlit l’injecte dans TON DOM */
button[data-testid="manage-app-button"],
button._terminalButton_rix23_138 {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
</style>

<script>
function hideManageAppButton() {
    const doc = window.parent.document;

    // 1) Par data-testid
    let btn = doc.querySelector('button[data-testid="manage-app-button"]');
    if (btn) {
        btn.style.display = "none";
        btn.style.visibility = "hidden";
        btn.style.opacity = "0";
        btn.style.pointerEvents = "none";
    }

    // 2) Par class CSS générée (_terminalButton_rix23_138)
    let btn2 = doc.querySelector('button[class*="terminalButton"]');
    if (btn2) {
        btn2.style.display = "none";
        btn2.style.visibility = "hidden";
        btn2.style.opacity = "0";
        btn2.style.pointerEvents = "none";
    }
}

// Plusieurs tentatives car Streamlit recrée parfois l’élément dynamiquement
setTimeout(hideManageAppButton, 100);
setTimeout(hideManageAppButton, 400);
setTimeout(hideManageAppButton, 1000);
setInterval(hideManageAppButton, 1500);
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
#  CUSTOM GLOBAL FONT (Google Fonts)
# ---------------------------------------------------------

st.markdown("""
<!-- Import Google Sans Flex -->
<link href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
/* Déclaration des polices globales utilisées dans l'UI */
:root {
    --font-title: 'Google Sans Flex', sans-serif;
    --font-body: 'Google Sans Flex', sans-serif;
    --font-ui: 'Google Sans Flex', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* === TITRES (H1 / H2 / H3) === */
h1 {
    font-family: var(--font-title) !important;
    font-weight: 520 !important;
    font-size: 42px !important;
    letter-spacing: -0.03em !important;
    color: #1D1D1F !important;
    margin-top: -100px !important;
}

h2 {
    font-family: var(--font-title) !important;
    font-weight: 600 !important;
    font-size: 30px !important;
    letter-spacing: -0.03em !important;
    color: #D32F2F !important;
    margin-top: 18px !important;
}

h3 {
    font-family: var(--font-title) !important;
    font-weight: 600 !important;
    font-size: 17px !important;
    letter-spacing: -0.03em !important;
    color: #1D1D1F !important;
    margin-top: 0px !important;
    margin-bottom: -20px !important;
}

/* === TEXTE CORPS (labels, spans, paragraphes…) === */
 p, div,label, span, input, textarea {
    font-family: var(--font-body) ;
    letter-spacing: -0.016em ;
    margin-top: 0px !important;
    margin-bottom: 0px !important;
    color: #1D1D1F;
}

/* === SELECTBOX & UI WIDGETS === */
.stSelectbox, .stMultiSelect, .stCheckbox, .stRadio {
    font-family: var(--font-ui) !important;
    font-size: 16px !important;
    letter-spacing: -0.03em !important;
    color: #D32F2F !important;
    margin-top: 0px !important;
}

/* === SLIDERS (texte + valeur affichée) === */
[data-testid="stSliderThumbValue"] {
    font-family: var(--font-ui) !important;
    font-weight: 400 !important;
    font-size: 11px !important;
    letter-spacing: -0.03em !important;
    color: #D32F2F !important;
    margin-top: 15px !important;
}



</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# Configuration style slider
# --------------------------------------------------------------------
st.markdown("""
<style>

 /* ======== RAIL DU SLIDER (ligne de fond) ======== */
.st-dx {
    background-color: #0071e3 !important;   /* bleu Maneko */
    height: 4px !important;
    border-radius: 4px !important;
}

/* ======== RAIL ACTIF (partie colorée sélectionnée) ======== */
.st-dq .st-emotion-cache-dx6mrm div div {
    background-color: #0071e3 !important;   /* orange Maneko */
    color: white !important;
    font-size: 11px !important;
    font-weight: 40 !important;
    
}

/* ======== THUMB (bouton rond) ======== */
div[role="slider"] {
    background: #0071e3 !important;
    border: 1px solid #0054B0 !important;
    width: 15px !important;
    height: 15px !important;
    border-radius: 50% !important;
    box-shadow: 0px 0px 0px rgba(0,0,0,0) !important;
}

/* ======== THUMB AU SURVOL ======== */
div[role="slider"]:hover {
    background: #FFFFFF !important;
    border-color: #0071e3 !important;
}

/* ======== TOOLTIP (valeur affichée au-dessus du thumb) ======== */
[data-testid="stSliderThumbValue"] {
    background-color: transparent !important;
    color: black !important;
    font-size: 11px
    font-weight: 400 !important;
    border-radius: 6px !important;
    padding: 12px 00px !important;
    margin-top: -15px !important;
}


    /* 1️⃣ Tick bar (ligne de base) */
    div[data-testid="stSliderTickBar"] {
        background: #FFFFFF !important;  /* Couleur Maneko */
        height: 4px !important;
        border-radius: 3px !important;
        font-size: 10px !important;
        margin-top : -10px !important;
    }

    /* 2️⃣ Portion active (track sélectionnée) */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
        border: 0.5px solid #A3A3AB !important;
        border-radius: 4px !important;
        height: 6px !important;  /* augmenter pour rendre visible */
        
    }

    /* 3️⃣ Désactive totalement le gradient auto qui revient après mouvement */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div {
        background: transparent !important; /* ligne bleue de base */
    }

    /* 4️⃣ Le cache couleur utilisé par Streamlit : on écrase tout */
    [class*="stSlider"] [class*="track"] {
        background: #FFFFFF !important;
    }

    /* 5️⃣ FINALLY: forcer toute div interne ayant un background-gradient */
    div[data-testid="stSlider"] * {
        background-image: none !important;
    }

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------
# Background
# --------------------------------------------------------------------
st.markdown("""
    <style>
        /* Applique le fond à la zone principale */
        .stApp {
            background-color: #FFFFFF !important;
        }

        /* Applique aussi le fond aux conteneurs internes */
        .block-container {
            background-color: #FFFFFF !important;
        }

        /* Supprime le fond gris des widgets */
        .stSelectbox, .stSlider, .stCheckbox {
            background-color: transparent !important;
        }
    </style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------
# Couleurs par défaut
# --------------------------------------------------------------------
#CONSTRUCTEUR_GREEN = "#2E7D32"
#CONSTRUCTEUR_GREY = "#1F1F1F"
DANGER_RED = "#D32F2F"
WARN_ORANGE = "#F9A825"
OK_GREEN = "#388E3C"
JET_BLACK = "#273340"
ORANGE = "#FCA309"
WHITE = "#FDFFFF"
CHARCOAL_BROWN = "#373A36"
AIR_FORCE_BLUE = "#6A8D92"
BLACK = "#1D1D1F"
BLUE = "#0071e3"

# --------------------------------------------------------------------
# Logo Maneko
# --------------------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
logo_path = os.path.join(BASE_PATH, "assets/logo_maneko.png")

# --------------------------------------------------------------------
# Logo Maneko (cliquable)
# --------------------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
logo_path = os.path.join(BASE_PATH, "assets/logo_maneko.png")

# Convertir en base64
with open(logo_path, "rb") as f:
    img_data = base64.b64encode(f.read()).decode()

# Affichage HTML cliquable
st.markdown(
    f"""
    <a href="https://www.maneko.fr" target="_blank">
        <img src="data:image/png;base64,{img_data}" 
             style="position:absolute; top:0px; left:0px; 
                    width:100px; margin-top:-100px;">
    </a>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------------------
# Gestion du titre
# --------------------------------------------------------------------
st.markdown(f"""
    <h1 style='color:{BLACK};text-align:center;font-weight:700;'>
        Personnalisez votre simulation
    </h1>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# Couleurs des listes déroulantes
# --------------------------------------------------------------------
st.markdown("""
<style>

    /* --- Forcer le fond clair du conteneur principal SELECT --- */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        min-height: 83px !important;      /* Hauteur totale */
        min-width: 100% !important;      /* largeur totale */
        padding: 0px 10px !important;
        color: #1D1D1F !important;
        font-weight: 600 !important;
        font-size: 17px !important;
        letter-spacing: -0.03em !important;
        border-radius: 12px !important;
        border: 1px solid #A3A3AB !important;
        display: flex;
        align-items: center;
    }

    /* --- Nettoyage du label interne --- */
    div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* --- Popover (menu déroulant) : FOND BLANC --- */
    div[data-baseweb="popover"] {
        background-color: transparent !important;
        border-radius: 12px !important;
        border: 1px solid #A3A3AB !important;
        color: #FFFFFF !important;
    }


    /* --- Liste UL des options --- */
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid #0071E3 !important;
    }

    /* --- Option individuelle --- */
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
        padding: 8px 12px !important;
        font-size: 16px !important;
    }

    /* Option hover */
    li[role="option"]:hover {
        background-color: #0071E3 !important;
        color: #FFFFFF !important;
        cursor: pointer !important;
    }

    /* Option sélectionnée */
    li[aria-selected="true"] {
        background-color: #0071E3 !important;
        color: #FFFFFF !important;
        font-weight: 400 !important;
    }

</style>
""", unsafe_allow_html=True
)


# ---------------------------------------------------------
# 🟩 1) Sélection du TRACTEUR
# ---------------------------------------------------------
st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

st.subheader("Tracteur")

tractor_files = [f for f in os.listdir("tractors") if f.endswith(".json")]

# Charger tous les JSON pour récupérer les noms lisibles
tractor_display = []
tractor_map = {}

for file in tractor_files:
    data = load_json(f"tractors/{file}")
    pretty = data.get("name", file.replace(".json", ""))  # nom lisible
    key = file.replace(".json", "")                       # identifiant interne
    tractor_display.append(pretty)
    tractor_map[pretty] = key
    tractor_display = sorted(tractor_display)

# Selectbox : montre le vrai nom lisible
selected_pretty = st.selectbox("Choisir un tracteur", tractor_display)

# On retrouve la clé correspondant à ce nom
selected_tractor = tractor_map[selected_pretty]

# Charger le JSON correct
tractor = load_json(f"tractors/{selected_tractor}.json")


# ---------------------------------------------------------
# 🟧 2) Sélection de la MACHINE ARRIÈRE
# ---------------------------------------------------------
st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

st.subheader("Machine arrière")

machine_files = [f for f in os.listdir("machines") if f.endswith(".json")]

# Charger tous les JSON pour récupérer le nom lisible
machine_display = []
machine_map = {}

for file in machine_files:
    data = load_json(f"machines/{file}")
    pretty = data.get("model", file.replace(".json", ""))  # nom affiché
    key = file.replace(".json", "")                       # identifiant interne
    machine_display.append(pretty)
    machine_map[pretty] = key
    machine_display = sorted(machine_display)

# Selectbox — affiche les noms lisibles
selected_machine_pretty = st.selectbox("Choisir une machine", machine_display)

# Trouver la clé interne
selected_machine = machine_map[selected_machine_pretty]

# Charger le JSON correspondant
machine = load_json(f"machines/{selected_machine}.json")

# ---------------------------------------------------------
# 🟦 3) Chargeur frontal (optionnel)
# ---------------------------------------------------------
st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

st.subheader("Chargeur frontal")

# Init
if "loader_enabled" not in st.session_state:
    st.session_state.loader_enabled = False

enabled = st.session_state.loader_enabled

# -------------------------------------------------
# CSS DESIGN UNIQUE pour les 2 boutons
# -------------------------------------------------
st.markdown("""
<style>

/* Style commun */
div.st-key-loader_off button,
div.st-key-loader_on button {
    background-color: #F6F6F7 !important;
    border: 1px solid #A3A3AB !important; 
    border-radius: 15px !important;
    min-height: 83px !important;      /* Hauteur totale */
    padding: 15px !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1D1D1F !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
    margin-top:0px;
    margin-bottom:0px;
}

/* Survol */
div.st-key-loader_off button:hover,
div.st-key-loader_on button:hover {
    border: 2px solid #0071E3 !important;
}

/* État Désactivé */
div.st-key-loader_off button {
    background-color: #FFFFFF !important;
}

/* État Activé */
div.st-key-loader_on button {
    background-color: #FFFFFF !important;
}

/* Bouton actuellement actif */
div.st-key-loader_off button.active-btn,
div.st-key-loader_on button.active-btn {
    border: 2px solid #0071E3 !important;
    box-shadow: 0 0 0 4px rgba(0,113,227,0.25) !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# Boutons STREAMLIT (normaux)
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Désactiver", key="loader_off", use_container_width=True):
        st.session_state.loader_enabled = False
        enabled = False

with col2:
    if st.button("Activer", key="loader_on", use_container_width=True):
        st.session_state.loader_enabled = True
        enabled = True

loader_enabled = enabled


st.markdown("""
<script>
setTimeout(() => {
    const btns = window.parent.document.querySelectorAll("button");
    btns.forEach((b, i) => {
        console.log("BTN", i, b.outerHTML);
    });
}, 800);
</script>
""", unsafe_allow_html=True)
# -------------------------------------------------
# Appliquer classe CSS dynamique
# -------------------------------------------------
active_key = "loader_on" if enabled else "loader_off"

st.markdown(f"""
<script>
// Trouve tous les boutons Streamlit
const buttons = window.parent.document.querySelectorAll('button[data-streamlit-key]');

buttons.forEach(btn => {{
    if (btn.getAttribute("data-streamlit-key") === "{active_key}") {{
        btn.classList.add("custom-btn");
        btn.classList.add("custom-btn-active");
    }} else if (btn.getAttribute("data-streamlit-key") === "loader_off" ||
               btn.getAttribute("data-streamlit-key") === "loader_on") {{
        btn.classList.add("custom-btn");
        btn.classList.remove("custom-btn-active");
    }}
}});
</script>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 📝 TEXTE INDICATEUR
# ---------------------------------------------------------
if enabled:
    st.markdown("<p style='color:#0071E3;font-size:14px;;font-weight:400;margin-top:-80px;'>Chargeur frontal activé</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#0071E3;font-size:14px;;font-weight:400;margin-top:-80px;'>Chargeur frontal désactivé</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SI ACTIF → affichage du menu de choix du chargeur
# ---------------------------------------------------------
loader = None

if loader_enabled:
    tractor_mass = tractor.get("mass", 0)

    # Sélection automatique via solver
    loader_name_auto = select_loader_name(tractor_mass)

    st.markdown(
        f"""
        <p style="
            font-size:14px;
            font-weight:400;
            color:#0071E3;
        ">
            Chargeur de série : <b>{loader_name_auto}</b>
        </p>
        """,
        unsafe_allow_html=True
    )

    loader_files = os.listdir("loaders")
    loader_list = [f.replace(".json", "") for f in loader_files if f.endswith(".json")]
    loader_list = sorted(loader_list)

    # Selectbox avec valeur persistante
    st.selectbox(
        "Sélection manuelle du chargeur (optionnel) :",
        ["De série"] + loader_list,
        key="loader_choice"
    )

    choice = st.session_state.loader_choice

    # Chargement du JSON correct
    if choice == "De série":
        loader = load_json(f"loaders/{loader_name_auto}.json")
    else:
        loader = load_json(f"loaders/{choice}.json")

# MISE À JOUR DES OPTIONS
options = st.session_state["options"]

options["loader_enabled"] = loader_enabled
options["loader_mode"]    = "low"

# Sauvegarde du loader sélectionné
st.session_state["loader_json"] = loader
options["loader"] = loader

# ---------------------------------------------------------
# 🟦 LESTAGE À L’EAU (boutons stylés)
# ---------------------------------------------------------
st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

st.subheader("Lestage à l'eau")
st.markdown("<p style='color:#0071E3;font-size:14px;;font-weight:400;margin-top:-10px;'>Lestage sur pneus arrière uniquement</p>", unsafe_allow_html=True)

# Init état
if "water_enabled" not in st.session_state:
    st.session_state.water_enabled = False

water_enabled = st.session_state.water_enabled

# -------------------------------------------------
# CSS DESIGN IDENTIQUE AU CHARGEUR (dupliqué)
# -------------------------------------------------
st.markdown("""
<style>

/* Style commun */
div.st-key-water_off button,
div.st-key-water_on button {
    background-color: #F6F6F7 !important;
    border: 1px solid #A3A3AB !important;
    border-radius: 15px !important;
    min-height: 83px !important;      /* Hauteur totale */
    padding: 15px !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1D1D1F !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
    margin-top:0px;
    margin-bottom:0px;
}

/* Hover */
div.st-key-water_off button:hover,
div.st-key-water_on button:hover {
    border: 2px solid #0071E3 !important;
}

/* Désactivé */
div.st-key-water_off button {
    background-color: #FFFFFF !important;
}

/* Activé */
div.st-key-water_on button {
    background-color: #FFFFFF !important;
}

/* Bouton actif */
div.st-key-water_off button.active-btn,
div.st-key-water_on button.active-btn {
    border: 2px solid #0071E3 !important;
    box-shadow: 0 0 0 4px rgba(0,113,227,0.25) !important;
}

</style>
""", unsafe_allow_html=True)



# -------------------------------------------------
# Boutons STREAMLIT
# -------------------------------------------------
colA, colB = st.columns(2)

with colA:
    if st.button("Désactiver", key="water_off", use_container_width=True):
        st.session_state.water_enabled = False
        water_enabled = False

with colB:
    if st.button("Activer", key="water_on", use_container_width=True):
        st.session_state.water_enabled = True
        water_enabled = True

# -------------------------------------------------
# Appliquer classe CSS dynamique
# -------------------------------------------------
active_key_water = "water_on" if water_enabled else "water_off"

st.markdown(f"""
<script>
const buttonsWater = window.parent.document.querySelectorAll('button[data-streamlit-key]');

buttonsWater.forEach(btn => {{
    if (btn.getAttribute("data-streamlit-key") === "{active_key_water}") {{
        btn.classList.add("custom-btn");
        btn.classList.add("active-btn");
    }} else if (btn.getAttribute("data-streamlit-key") === "water_off" ||
               btn.getAttribute("data-streamlit-key") === "water_on") {{
        btn.classList.add("custom-btn");
        btn.classList.remove("active-btn");
    }}
}});
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TEXTE INDICATEUR
# ---------------------------------------------------------
if water_enabled:
    st.markdown("<p style='color:#0071E3;font-size:14px;font-weight:400;'>Lestage à l'eau activé</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#0071E3;font-size:14px;font-weight:400;'>Lestage à l'eau désactivé</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Valeur pour le solver (IMPORTANT)
# ---------------------------------------------------------



# --------------------------------------------------------------------
# Chargement données pneus + tracteurs + machines
# --------------------------------------------------------------------


def load_json(path):
    """Charge un fichier JSON situé dans simulateur_ui ou ses sous-dossiers."""
    full_path = os.path.join(os.path.dirname(__file__), path)
    with open(full_path, "r") as f:
        return json.load(f)

tires = load_json("data/tires.json")

#TRACTOR_LIST = os.listdir(os.path.join(BASE_PATH, "tractors"))
#MACHINE_LIST = os.listdir(os.path.join(BASE_PATH, "machines"))




# ====================================================================
# 🟥 BLOC 1 — Sélection PNEUS uniquement
# ====================================================================
st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

st.subheader("Pneus")

# ------------------------------
# INIT
# ------------------------------
if "auto_tire_enabled" not in st.session_state:
    st.session_state.auto_tire_enabled = True

auto_tire_enabled = st.session_state.auto_tire_enabled

if "options" not in st.session_state:
    st.session_state["options"] = {}

options = st.session_state["options"]

# Liste pneus
tire_list = list(tires.keys())
tire_def = tractor.get("tire_defaults", {})
front_auto = tire_def.get("front", tire_list[0])
rear_auto  = tire_def.get("rear", tire_list[0])

# -------------------------------------------------
# CSS DESIGN IDENTIQUE AU LESTAGE À L’EAU
# -------------------------------------------------
st.markdown("""
<style>

div.st-key-tires_auto button,
div.st-key-tires_manual button {
    background-color: #FFFFFF !important;
    border: 1px solid #A3A3AB !important;
    border-radius: 15px !important;
    min-height: 83px !important;
    padding: 15px !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1D1D1F !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
    margin-top:0px;
    margin-bottom:0px;
}

/* Hover */
div.st-key-tires_auto button:hover,
div.st-key-tires_manual button:hover {
    border: 2px solid #0071E3 !important;
}

/* Bouton actif */
div.st-key-tires_auto button.active-btn,
div.st-key-tires_manual button.active-btn {
    border: 2px solid #0071E3 !important;
    box-shadow: 0 0 0 4px rgba(0,113,227,0.25) !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Boutons Auto / Manuel avec style actif
# -------------------------------------------------
colA, colB = st.columns(2)

with colA:
    auto_clicked = st.button("De série", key="tires_auto", use_container_width=True)
    if auto_clicked:
        st.session_state.auto_tire_enabled = True
        auto_tire_enabled = True

with colB:
    man_clicked = st.button("Personnaliser", key="tires_manual", use_container_width=True)
    if man_clicked:
        st.session_state.auto_tire_enabled = False
        auto_tire_enabled = False

# -------------------------------------------------
# Ajout dynamique de la classe 'active-btn'
# -------------------------------------------------
active_script = """
<script>
let autoBtn = window.parent.document.querySelector('div.st-key-tires_auto button');
let manBtn  = window.parent.document.querySelector('div.st-key-tires_manual button');

if (autoBtn && manBtn) {
    autoBtn.classList.remove('active-btn');
    manBtn.classList.remove('active-btn');

    if (%s) {
        autoBtn.classList.add('active-btn');
    } else {
        manBtn.classList.add('active-btn');
    }
}
</script>
""" % ("true" if auto_tire_enabled else "false")

st.markdown(active_script, unsafe_allow_html=True)

# -------------------------------------------------
# Mode AUTO
# -------------------------------------------------
if auto_tire_enabled:

    st.markdown(f"""
    <p style='color:#0071E3;font-size:14px;font-weight:400;'>
        Pneus recommandés du constructeur
    </p>
    <ul>
      <li>Pneus avants : <b>{front_auto}</b></li>
      <li>Pneus arrières : <b>{rear_auto}</b></li>
    </ul>
    """, unsafe_allow_html=True)

    st.session_state.options["front_tire"] = front_auto
    st.session_state.options["rear_tire"]  = rear_auto

# -------------------------------------------------
# Mode MANUEL
# -------------------------------------------------
else:
    front_tire = st.selectbox("Pneus avants", tire_list, key="manual_front")
    rear_tire  = st.selectbox("Pneus arrières", tire_list, key="manual_rear")

    st.session_state.options["front_tire"] = front_tire
    st.session_state.options["rear_tire"]  = rear_tire

    
options["water_ballast"] = water_enabled

# ====================================================================
# 🟦 BLOC 2 — SLIDERS (ballast, masses, slopes, vitesse…)
# ====================================================================
st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

options = st.session_state["options"]

#st.subheader("Réglages des options et environnement")

col1, col2 = st.columns(2)

# Valeurs dynamiques du tracteur
dyn = tractor.get("dynamics", {})

max_speed_kmh = dyn.get("max_speed_kmh", 40.0)
max_speed_ms = max_speed_kmh / 3.6   # Conversion km/h → m/s

max_brake = dyn.get("max_braking_accel", 5.0)
max_turn = dyn.get("max_turn_radius", 10.0)

with col1:
    st.markdown(
        "<p style='font-size:18px; font-weight:600; color:#1D1D1F; margin-bottom:10px;'>Masses additionnelles</p>",
        unsafe_allow_html=True
    )
    options["wheel_weight_ARG"] = st.slider("Masse Roue arrière gauche (kg)", 0, 500, 0)
    options["wheel_weight_ARD"] = st.slider("Masse Roue arrière droite (kg)", 0, 500, 0)
    options["front_ballast_mass"] = st.slider("Masse avant (kg)", 0, 1500, 0)
    options["front_ballast_offset"] = st.slider("Décalage masse avant (m)", 0.0, 3.0, 1.0)
    st.markdown(
        f"<p style='font-size:14px; margin-top: -0px !important; font-weight:400; color:#0071E3;'>Distance du centre de gravité de la masse à l'axe des roues avants en m</p>",
        unsafe_allow_html=True
    )
    options["rear_ballast_mass"] = st.slider("Masse arrière (kg)", 0, 1500, 0)
    options["rear_ballast_offset"] = st.slider("Décalage Masse arrière (m)", 0.0, 3.0, 1.0)
    st.markdown(
        f"<p style='font-size:14px; margin-top: -0px !important; font-weight:400; color:#0071E3;'>Distance du centre de gravité de la masse à l'axe des roues arrières en m</p>",
        unsafe_allow_html=True
    )
    


with col2:
    st.markdown(
        "<p style='font-size:18px; font-weight:600; color:#1D1D1F; margin-bottom:10px;'>Conditions environnementales</p>",
        unsafe_allow_html=True
    )

    env = {}
    env["slope_lat"] = st.slider("Pente latérale (°)", -30.0, 30.0, 0.0)
    env["slope_long"] = st.slider("Pente longitudinale (°)", -30.0, 30.0, 0.0)
    env["speed"] = st.slider(f"Vitesse (m/s) — max {max_speed_kmh} km/h",0.0,float(max_speed_ms),1.4)
    st.markdown(
        f"<p style='font-size:14px; margin-top: -0px !important; font-weight:400; color:#0071E3;'>{env['speed']} m/s = {env['speed'] * 3.6:.1f} km/h</p>",
        unsafe_allow_html=True
    )
    env["accel_long"] = st.slider(f"Accélération longitudinale (m/s²)",0.0,10.0,float(max_brake))
    env["turn_radius"] = st.slider(f"Rayon de virage (m)",float(max_turn),20.0,float(max_turn))



# ====================================================================
# 🟧 BOUTON DE CALCUL
# ====================================================================

st.markdown("""
<div style="height:0.5px;background:#D5D5D9;margin-top:20px;margin-bottom:-20px;"></div>
""", unsafe_allow_html=True)

# ----- CSS pour le bouton de simulation -----
st.markdown("""
<style>
/* Style commun du bouton Simulation */
div.st-key-run_sim button {
    background-color: transparent !important;
    border: 2px solid #0071E3 !important;
    border-radius: 15px !important;
    min-height: 83px !important;      /* Hauteur totale */
    padding: 15px !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #FDFFFF !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
}

/* Hover */
div.st-key-run_sim button:hover {
    border: 0px solid #A3A3AB !important;
}

/* État actif (halo bleu) */
div.st-key-run_sim button.active-btn {
    border: 2px solid #A3A3AB !important;
    box-shadow: 0 0 0 4px rgba(0,113,227,0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# ----- Bouton -----
run = st.button("Lancer la simulation", key="run_sim", use_container_width=True)

# Activation visuelle du style sélectionné
if run:
    st.markdown("""
    <script>
    const btn = window.parent.document.querySelector('button[data-streamlit-key="run_sim"]');
    if (btn) btn.classList.add("active-btn");
    </script>
    """, unsafe_allow_html=True)

# ----- Traitement après clic -----
if run:

    # Chargement du tracteur et de la machine par défaut
    tractor = load_json(f"tractors/{selected_tractor}.json")
    machine = load_json(f"machines/{selected_machine}.json")
    loader = None

    status_placeholder = st.empty()   # emplacement réservé

    status_placeholder.info("Calcul en cours...")   # affiche le message

    
    loader_json = st.session_state.get("loader_json", None)
    result = solve(tractor, machine, loader_json, tires, options, env)

    status_placeholder.markdown("""
    <div style="
    background:transparent;
    color:#0071E3;
    border:0px solid transparent;
    border-radius:12px;
    font-weight:400;
    font-size:14px;
    ">
    Simulation terminée !
    </div>
    """, unsafe_allow_html=True)   # remplace le message précédent


    # ====================================================================
    # AFFICHAGE RESULTATS
    # ====================================================================
    #st.subheader("📘 Résultats du Centre de Gravité")
    #st.write(result["CG"])

    #st.subheader("📘 Charges aux roues")
    #st.write(result["wheels"])

    #st.subheader("📘 Stabilité statique")
    #st.write(result["static"]["work"])
    st.subheader("Critères de sécurité")
    for crit in result["compatibility"]:
        status_color = OK_GREEN
        if "Danger" in crit["status"]:
            status_color = DANGER_RED
        elif "Avert" in crit["status"]:
            status_color = WARN_ORANGE

        st.markdown(
            f"<p style='color:{status_color};;font-size:17px;font-weight:600;'>"
            f"{crit['status']} — {crit['name']} "
            f"</p>",
            unsafe_allow_html=True
        )

    with st.expander("Résultats du Centre de Gravité"):
        st.json(result["CG"])

    with st.expander("Charges aux roues"):
        st.json(result["wheels"])

    with st.expander("Stabilité statique (mode work)"):
        st.json(result["static"]["work"])





































