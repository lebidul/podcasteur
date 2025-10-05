"""
Point d'entrée de l'interface graphique Podcasteur
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path si nécessaire
if getattr(sys, 'frozen', False):
    # Mode exécutable PyInstaller
    application_path = sys._MEIPASS
else:
    # Mode développement
    application_path = Path(__file__).parent

# Ajouter au path Python
if str(application_path) not in sys.path:
    sys.path.insert(0, str(application_path))

from PyQt6.QtWidgets import QApplication

# Import absolu au lieu de relatif
try:
    from main_window import MainWindow
except ImportError:
    from src.gui.main_window import MainWindow


def main():
    """Lance l'application GUI"""
    app = QApplication(sys.argv)

    # Style de l'application
    app.setStyle('Fusion')

    # Fenêtre principale
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()