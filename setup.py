#!/usr/bin/env python3
"""
Setup script for Reminder Warrior.
"""
from setuptools import setup, find_packages

# Read the version from the package
version = '0.1.0'
try:
    with open('reminder_warrior/__init__.py', 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                version = line.split('=')[1].strip().strip('"').strip("'")
                break
except FileNotFoundError:
    pass

setup(
    name='reminder-warrior',
    version=version,
    description='Sync tasks between Taskwarrior and Apple Reminders',
    packages=find_packages(),
    install_requires=[
        'click>=7.0,<9.0',
    ],
    entry_points={
        'console_scripts': [
            'reminder-warrior=reminder_warrior.cli:main',
            'rw=reminder_warrior.cli:main',
        ],
    },
    python_requires='>=3.6',
)
