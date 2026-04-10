project = "Stars Reborn Research & Design"
author = "Brandon Arrendondo"
release = "0.1"
copyright = "2026, Brandon Arrendondo"

extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.todo",
    "sphinxcontrib.plantuml",
]

plantuml = "plantuml"
plantuml_output_format = "png"

autosectionlabel_prefix_document = True
todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]

html_theme_options = {
    "description": "Game mechanics research and design reference for Stars Reborn.",
    "github_user": "arrendondo",
    "github_repo": "stars-reborn-research-and-design",
    "fixed_sidebar": True,
}

rst_prolog = """
.. |project| replace:: Stars Reborn
.. |original| replace:: Stars!
"""
