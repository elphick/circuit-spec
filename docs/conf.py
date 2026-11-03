"""Sphinx configuration for CircuitSpec."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "CircuitSpec"
copyright = "2026, CircuitSpec contributors"
author = "CircuitSpec contributors"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
]
autosummary_generate = True
templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_book_theme"
html_logo = "_static/circuitspec-logo.svg"
html_title = "CircuitSpec"
html_static_path = ["_static"]
html_theme_options = {
    "show_navbar_depth": 2,
    "navigation_with_keys": True,
}

sphinx_gallery_conf = {
    "examples_dirs": "../examples",
    "gallery_dirs": "generated/gallery",
    "within_subsection_order": "FileNameSortKey",
    "filename_pattern": r"(plot_|plotly_graph_renderer)",
    "copyfile_regex": r".*\.yaml",
    "remove_config_comments": True,
    "image_scrapers": ("matplotlib", "plotly.io._sg_scraper.plotly_sg_scraper"),
}
