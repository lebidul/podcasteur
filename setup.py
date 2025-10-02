"""
Setup pour Podcasteur
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_path = Path(__file__).parent / 'README.md'
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ''

setup(
    name='podcasteur',
    version='1.0.0',
    description='Éditeur de podcasts automatisé avec IA',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Projet Bidul',
    url='https://github.com/lebidul/podcasteur',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pydub>=0.25.1',
        'openai-whisper>=20231117',
        'torch>=2.0.0',
        'anthropic>=0.18.0',
        'click>=8.1.0',
        'rich>=13.0.0',
        'pyyaml>=6.0.0',
        'python-dotenv>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'podcasteur=src.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio :: Editors',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)