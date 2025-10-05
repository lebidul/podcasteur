#!/usr/bin/env python3
"""
Lanceur de l'interface graphique Podcasteur
"""

import sys
import traceback
from dotenv import load_dotenv
from pathlib import Path

# Charger le fichier .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def exception_hook(exctype, value, tb):
    """Capture toutes les exceptions non gérées"""
    print("=" * 60)
    print("ERREUR NON GÉRÉE DÉTECTÉE !")
    print("=" * 60)
    traceback.print_exception(exctype, value, tb)
    print("=" * 60)

# Installer le hook
sys.excepthook = exception_hook

from src.gui.main import main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERREUR CRITIQUE : {e}")
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour fermer...")