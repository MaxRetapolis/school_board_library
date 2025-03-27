#!/usr/bin/env python3
"""
Setup script for School Board Documents Usage Database Generator
"""

from setuptools import setup, find_packages

setup(
    name="school_board_db_generator",
    version="0.1.0",
    description="Generates a simulated usage database for school board documents",
    author="Claude 3.7",
    packages=find_packages(),
    package_dir={"": "src"},
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "generate-db=usage_db_generator:main",
            "query-db=query_usage_db:main",
        ],
    },
)