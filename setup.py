"""Setup script for rpi-mini-battery-display package"""
# pragma pylint: disable=invalid-name
from pathlib import Path

from setuptools import find_packages, setup

with Path("README.md").open("r") as readme_file:
    long_description = readme_file.read()

with Path("requirements.txt").open("r") as requirements_file:
    requirements = requirements_file.read().splitlines()
    requirements = [
        requirement for requirement in requirements if not requirement.startswith("#")
    ]

with Path("VERSION").open("r") as version_file:
    version = version_file.read()

setup(
    name="rpi-mini-battery-display",
    version=version,
    author="Koen Vervloesem",
    author_email="koen@vervloesem.eu",
    url="https://github.com/koenvervloesem/rpi-mini-battery-display",
    project_urls={
        "Documentation": "https://github.com/koenvervloesem/rpi-mini-battery-display",
        "Source": "https://github.com/koenvervloesem/rpi-mini-battery-display",
        "Tracker": "https://github.com/koenvervloesem/rpi-mini-battery-display/issues",
    },
    license="MIT",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    keywords=["tm1651", "raspberry pi", "rpi", "display", "gpio", "led"],
    description="Control 10-segment mini battery displays on a Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3",
    scripts=["bin/rpi-mini-battery-display"],
)
