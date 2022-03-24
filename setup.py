#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0', 
    'SQLAlchemy>=1.4.32', 
    'pandas>=1.4.1', 
    'Flask-Cors>=3.0.10', 
    'connexion[swagger-ui]', 
    'PyMySQL>=1.0.2', 
    'Flask>=2.0.3'
  ]

test_requirements = [ ]

setup(
    author="Shubhi Ambast",
    author_email='shubhiambast@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="BioDb Expression Atlas",
    entry_points={
        'console_scripts': [
            'biodb_expression_atlas=biodb_expression_atlas.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='biodb_expression_atlas',
    name='biodb_expression_atlas',
    packages=find_packages(include=['biodb_expression_atlas', 'biodb_expression_atlas.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/shubhiambast/biodb_expression_atlas',
    version='0.1.0',
    zip_safe=False,
)
