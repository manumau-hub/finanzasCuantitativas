# -*- coding: utf-8 -*-
"""
UCEMA QUANT - WebApp

Propiedades, payoffs, market data, griegas y pricing de estrategias.
"""
import streamlit as st
from pathlib import Path

from i18n import _

st.set_page_config(
    page_title="UCEMA QUANT",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar reducido en toda la app (12rem)
st.markdown("""
<style>[data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }</style>
""", unsafe_allow_html=True)

st.title(f"📈 {_('home.title')}")
st.markdown(f"**{_('home.subtitle')}**")

st.markdown(f"""
{_('home.welcome')}

- **{_('home.nav.propiedades')}** — {_('home.nav.propiedades.desc')}
- **{_('home.nav.modelos')}** — {_('home.nav.modelos.desc')}
- **{_('home.nav.market_data')}** — {_('home.nav.market_data.desc')}
- **{_('home.nav.griegas')}** — {_('home.nav.griegas.desc')}
- **{_('home.nav.pricing')}** — {_('home.nav.pricing.desc')}
- **{_('home.nav.notebooks')}** — {_('home.nav.notebooks.desc')}
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
    md_content = md_content.replace("# UCEMA QUANT — Documentación técnica", "## Documentación técnica")
    md_content = md_content.replace("# Finanzas Cuantitativas UCEMA — Documentación técnica", "## Documentación técnica")
    md_content = md_content.replace("# Finanzas Cuantitativas app — Documentación técnica completa", "## Documentación técnica")
    st.markdown(md_content, unsafe_allow_html=False)
else:
    st.info(_("home.docs.not_found"))

st.divider()
st.caption(_("home.footer"))
