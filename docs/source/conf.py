# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import shutil

print(os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = 'squid-py'
copyright = 'squid-py contributors'
author = 'squid-py contributors'

# The full version, including alpha/beta/rc tags
release = '0.2.13'
# The short X.Y version
release_parts = release.split('.')  # a list
version = release_parts[0] + '.' + release_parts[1]

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.apidoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

# apidoc settings
# See https://github.com/sphinx-contrib/apidoc
apidoc_module_dir = '../../squid_py'
# apidoc_output_dir = 'api' by default, and leave it that way!
apidoc_separate_modules = True
# See https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
apidoc_extra_args = []

# autodoc settings
# Setting None is equivalent to giving the option name
# in the list format (i.e. it means “yes/true/on”).
# autodoc_default_options = {
#     'members': None,
#     'member-order': 'bysource',
#     'undoc-members': None,
#     'private-members': None,
#     'special-members': None,
#     'inherited-members': None,
# }

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

highlight_language = 'python3'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {'sidebar.rst'}

# Delete the api/ directory of auto-generated .rst docs files
print("Removing the api/ directory via conf.py, if api/ exists.")
shutil.rmtree('api', ignore_errors=True)
print("Done removal.")
