#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages


def get_version(filename):
    """Extract the package version"""
    with open(filename) as in_fh:
        for line in in_fh:
            if line.startswith('__version__'):
                return line.split('=')[1].strip()[1:-1]
    raise ValueError("Cannot extract version from %s" % filename)


with open('README.rst') as readme_file:
    readme = readme_file.read()

try:
    with open('HISTORY.rst') as history_file:
        history = history_file.read()
except OSError:
    history = ''

requirements = ['numpy', 'scipy', 'matplotlib', 'qutip']

dev_requirements = [
    'coverage', 'pytest', 'pytest-cov', 'pytest-xdist', 'twine', 'pep8',
    'flake8', 'wheel', 'sphinx', 'sphinx-autobuild', 'sphinx_rtd_theme',
    'sphinx-autodoc-typehints', 'gitpython', 'better-apidoc', 'jupyter',
    'nbval', 'nbsphinx', 'watermark']


version = get_version('./src/weylchamber/__init__.py')

setup(
    author="Michael Goerz",
    author_email='mail@michaelgoerz.net',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Python package for analyzing two-qubit gates in the Weyl chamber",
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='weylchamber',
    name='weylchamber',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url='https://github.com/qucontrol/weylchamber',
    version=version,
    zip_safe=False,
)
