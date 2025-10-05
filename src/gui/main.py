"""
Point d'entrée de l'interface graphique Podcasteur
"""

import sys
from PyQt6.QtWidgets import QApplication
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