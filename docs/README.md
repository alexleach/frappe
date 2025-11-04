# Frappe Framework Documentation

This directory contains the Sphinx documentation for the Frappe Framework.

## Building the Documentation Locally

### Prerequisites

Install the documentation dependencies:

```bash
pip install -r requirements.txt
```

Or install with the dev dependencies:

```bash
pip install -e ".[dev]"
```

### Build Commands

To build the HTML documentation:

```bash
make html
```

To build the PDF documentation:

```bash
make latexpdf
```

To clean the build directory:

```bash
make clean
```

### Viewing the Documentation

After building, open `_build/html/index.html` in your web browser:

```bash
# On Linux/Mac
open _build/html/index.html

# Or
python -m http.server --directory _build/html
```

## Auto-build for Development

For continuous rebuilding during development:

```bash
sphinx-autobuild . _build/html
```

Then navigate to `http://localhost:8000` in your browser.

## ReadTheDocs

This documentation is configured to be built automatically on ReadTheDocs. 
The configuration is in the `.readthedocs.yaml` file in the repository root.

## Documentation Structure

- `conf.py` - Sphinx configuration file
- `index.rst` - Main documentation index
- `modules.rst` - Complete module reference
- `api/` - API documentation by component
- `requirements.txt` - Documentation build dependencies
