pip install -u sphinx
pip install -u sphinx-rtd-theme
sphinx-apidoc -o apidoc/ racketinterpreter/
make html
