import os
from setuptools import setup, Extension
from Cython.Build import cythonize
from glob import glob


def find_py_files(package_dir="library"):
    """Find all .py files in a package, excluding __init__.py and tests."""
    path = os.path.join(package_dir, "**", "*.py")
    for py_file in glob(path, recursive=True):
        # Exclude files that are not part of the runtime application logic
        if "__init__.py" in py_file or "tests.py" in py_file:
            continue
        yield py_file


def create_extensions(package_dir="library"):
    """Create Extension objects for all relevant .py files in a package."""
    extensions = []
    for py_file in find_py_files(package_dir):
        # Convert file path to module path (e.g., 'library/views.py' -> 'library.views')
        module_path = py_file.replace(os.path.sep, ".").removesuffix(".py")
        extensions.append(Extension(module_path, [py_file]))
    return extensions


setup(
    name="University Library Backend Extensions",
    ext_modules=cythonize(create_extensions(), compiler_directives={"language_level": "3"}),
)