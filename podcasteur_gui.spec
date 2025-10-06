# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Ajouter le dossier src au path Python
src_path = str(Path.cwd() / 'src')

a = Analysis(
    ['podcasteur_gui.py'],
    pathex=[src_path],  # Ajouter src au path
    binaries=[],
    datas=[
        ('config/default_config.yaml', 'config'),
        ('src', 'src'),  # Inclure tout le dossier src
        ('.env.example', '.'),
        ('README_WINDOWS.txt', '.'),
        ('RELEASE_NOTES.md', '.'),
        ('assets/intro.wav', 'assets'),
        ('assets/outro.wav', 'assets'),
        ('assets/icon.ico', 'assets'),
    ],
    hiddenimports=[
        'anthropic',
        'whisperx',
        'whisperx.asr',
        'whisperx.alignment',
        'whisperx.diarize',
        'whisperx.audio',
        'faster_whisper',
        'pydub',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'yaml',
        'dotenv',
        'torch',
        'torchaudio',
        'numpy',
        'scipy',
        'pkg_resources',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Podcasteur',
    debug=True,  # Activez temporairement pour voir les erreurs
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Activez temporairement pour voir les erreurs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)