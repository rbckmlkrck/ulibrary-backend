# Makefile for the University Library Backend

# Use the python interpreter from the current environment.
PYTHON := python

.PHONY: all clean build

all: build

# Build the Cython extensions using the setup.py script.
build:
	@echo "Building Cython extensions..."
	$(PYTHON) setup.py build_ext --inplace

# Clean up build artifacts, Cython-generated C files, and Python cache.
clean:
	@echo "Cleaning up build artifacts and compiled files..."
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.so" -delete
	find . -path "library/*.c" -delete
	rm -rf build/ dist/ *.egg-info/
	@echo "Cleanup complete."