# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Monkey Patch ------------------------------------------------------------
# source: https://stackoverflow.com/questions/31784830/sphinx-ivar-tag-goes-looking-for-cross-references
# issue: https://github.com/sphinx-doc/sphinx/issues/2549

from docutils import nodes
from sphinx.util.docfields import TypedField
from sphinx import addnodes


def patched_make_field(self, types, domain, item, env=None):
    # type: (List, unicode, Tuple, BuildEnvironment) -> nodes.field
    def handle_item(fieldarg, content):
        par = nodes.paragraph()
        par += addnodes.literal_strong('', fieldarg)  # Patch: this line added
        #par.extend(self.make_xrefs(self.rolename, domain, fieldarg,
        #                           addnodes.literal_strong))
        if fieldarg in types:
            par += nodes.Text(' (')
            # NOTE: using .pop() here to prevent a single type node to be
            # inserted twice into the doctree, which leads to
            # inconsistencies later when references are resolved
            fieldtype = types.pop(fieldarg)
            if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                typename = u''.join(n.astext() for n in fieldtype)
                par.extend(self.make_xrefs(self.typerolename, domain, typename,
                                           addnodes.literal_emphasis))
            else:
                par += fieldtype
            par += nodes.Text(')')
        par += nodes.Text(' -- ')
        par += content
        return par

    fieldname = nodes.field_name('', self.label)
    if len(item) == 1 and self.can_collapse:
        fieldarg, content = item[0]
        bodynode = handle_item(fieldarg, content)
    else:
        bodynode = self.list_type()
        for fieldarg, content in item:
            bodynode += nodes.list_item('', handle_item(fieldarg, content))
    fieldbody = nodes.field_body('', bodynode)
    return nodes.field('', fieldname, fieldbody)


TypedField.make_field = patched_make_field


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'racketinterpreter'
copyright = '2020, Zibing Zhang'
author = 'Zibing Zhang'

# The full version, including alpha/beta/rc tags
release = 'v0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['docs/templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'Thumbs.db',
    '.DS_Store',
    '_build',
    'dist',
    'venv'
]

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
