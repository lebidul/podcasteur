"""
Point d'entrée de l'interface graphique Podcasteur
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Gérer les imports selon le contexte d'exécution
if getattr(sys, 'frozen', False):
    # Mode exécutable PyInstaller
    application_path = sys._MEIPASS
    # Import depuis le bundle PyInstaller
    from main_window import MainWindow
else:
    # Mode développement/script normal
    application_path = Path(__file__).parent
    # Import relatif normal
    from .main_window import MainWindow


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