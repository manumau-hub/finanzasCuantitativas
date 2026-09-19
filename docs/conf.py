# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# Añadir raíz del proyecto para importar Codigo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

project = "finanzasCuantitativas"
copyright = "2024, QUANt UCEMA"
author = "QUANt UCEMA"
release = "0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Napoleon para docstrings NumPy/Google
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Mock QuantLib si no está instalado
autodoc_mock_imports = ["QuantLib"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}
