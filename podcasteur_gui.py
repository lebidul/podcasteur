#!/usr/bin/env python3
"""
Lanceur de l'interface graphique Podcasteur
"""

import sys
import traceback
from dotenv import load_dotenv
from pathlib import Path
import os

# IMPORTANT : Pour PyInstaller, utiliser le dossier d'exécution
if getattr(sys, 'frozen', False):
    # Mode exécutable
    application_path = Path(sys.executable).parent
else:
    # Mode script
    application_path = Path(__file__).parent

# Charger le fichier .env depuis le dossier d'exécution
env_path = application_path / '.env'
print(f"Chargement .env depuis : {env_path}")
print(f"Fichier existe : {env_path.exists()}")

load_dotenv(env_path)

# Vérifier que la clé est chargée
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print("✓ Clé API chargée")
else:
    print("✗ Clé API non trouvée dans .env")

def exception_hook(exctype, value, tb):
    """Capture toutes les exceptions non gérées"""
    print("=" * 60)
    print("ERREUR NON GÉRÉE DÉTECTÉE !")
    print("=" * 60)
    traceback.print_exception(exctype, value, tb)
    print("=" * 60)

sys.excepthook = exception_hook

from src.gui.main import main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERREUR CRITIQUE : {e}")
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour fermer...")