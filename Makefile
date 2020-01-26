SOURCE = rpi_mini_battery_display
PYTHON_FILES = $(SOURCE)/*.py *.py
SHELL_FILES = bin/*

.PHONY: check clean package reformat requirements upload venv

check:
	flake8 $(PYTHON_FILES)
	pylint $(PYTHON_FILES)
	black --check .
	isort --check-only $(PYTHON_FILES)
	bashate $(SHELL_FILES)
	yamllint .
	pip list --outdated

clean:
	rm -rf $(SOURCE)/__pycache__/ .venv/ *.egg-info/ build/ dist/

package:
	python3 setup.py sdist bdist_wheel

reformat:
	black .
	isort $(PYTHON_FILES)

requirements:
	pip3 install --upgrade pip wheel setuptools
	pip3 install -r requirements.txt
	pip3 install -r requirements_dev.txt

upload:
	python3 -m twine upload dist/*

venv:
	rm -rf .venv/
	python3 -m venv .venv
