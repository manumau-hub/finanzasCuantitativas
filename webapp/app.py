# -*- coding: utf-8 -*-
"""
Finanzas Cuantitativas app - WebApp

Modelos, estrategias, payoffs y market data.
"""
import streamlit as st
from pathlib import Path

from i18n import _, render_language_selector

st.set_page_config(
    page_title="Home",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar reducido en toda la app (12rem)
st.markdown("""
<style>[data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }</style>
""", unsafe_allow_html=True)

render_language_selector()

st.title(f"📈 {_('home.title')}")
st.markdown(f"**{_('home.subtitle')}**")

st.markdown(f"""
{_('home.welcome')}

- **{_('home.nav.propiedades')}** — {_('home.nav.propiedades.desc')}
- **{_('home.nav.modelos')}** — {_('home.nav.modelos.desc')}
- **{_('home.nav.griegas')}** — {_('home.nav.griegas.desc')}
- **{_('home.nav.market_data')}** — {_('home.nav.market_data.desc')}
- **{_('home.nav.superficie')}** — {_('home.nav.superficie.desc')}
- **{_('home.nav.pricing')}** — {_('home.nav.pricing.desc')}
- **{_('home.nav.private_prefix')} {_('home.nav.ibkr')}** — {_('home.nav.ibkr.desc')}
""")

st.divider()

# ── Sección App: Documentación técnica ─────────────────────────────────────
st.subheader(f"📖 {_('home.docs.title')}")
st.caption(_("home.docs.caption"))

docs_path = Path(__file__).resolve().parent.parent / "docs" / "WEBAPP_TOOL.md"
if docs_path.exists():
    md_content = docs_path.read_text(encoding="utf-8")
    # Mostrar solo capítulos 1-5 (sin problemas conocidos, testing, referencias)
    start = md_content.find("\n---\n\n## 6. Problemas conocidos")
    if start > 0:
        md_content = md_content[:start]
    # Quitar Documentación de la tabla (ya no existe)
    md_content = md_content.replace(
        "| **Documentación** | Guía de la webapp (este documento) |\n",
        ""
    )
    md_content = md_content.replace(
        "│       ├── 4_Documentacion.py\n",
        ""
    )
    md_content = md_content.replace(
        "### 3.4 Documentación (`4_Documentacion.py`)\n\nMuestra esta guía (WEBAPP_TOOL.md) en la webapp.\n\n---\n\n",
        ""
    )
    # Nombres actualizados (por si el doc no está sincronizado)
    md_content = md_content.replace("Pricer Sandbox", "Modelos y Estrategias")
    md_content = md_content.replace("1_Pricer.py", "1_Modelos_y_Estrategias.py")
    md_content = md_content.replace("Market Data + Pricer", "Market Data + Pricing de estrategias")
    md_content = md_content.replace("3_Market_Data_Pricer.py", "3_Market_Data_Pricing_de_estrategias.py")
    md_content = md_content.replace("# Finanzas Cuantitativas app — Documentación técnica completa", "## Documentación técnica")
    st.markdown(md_content, unsafe_allow_html=False)
else:
    st.info(_("home.docs.not_found"))

st.divider()
st.caption(_("home.footer"))
