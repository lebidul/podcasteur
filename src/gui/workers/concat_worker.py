"""
Worker pour la concaténation audio dans un thread séparé
"""

from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path


class ConcatWorker(QThread):
    """Worker pour la concaténation des fichiers audio"""

    # Signaux
    progress = pyqtSignal(int, str)  # pourcentage, message
    finished = pyqtSignal(object)  # AudioSegment ou Path du fichier
    error = pyqtSignal(str)  # message d'erreur

    def __init__(self, audio_processor, fichiers, chemin_sortie, methode_tri="nom", ordre_tri="asc"):
        super().__init__()
        self.audio_processor = audio_processor
        self.fichiers = [Path(f) for f in fichiers]
        self.chemin_sortie = Path(chemin_sortie)
        self.methode_tri = methode_tri
        self.ordre_tri = ordre_tri

    def run(self):
        """Exécute la concaténation"""
        try:
            self.progress.emit(0, f"🔗 Concaténation de {len(self.fichiers)} fichiers...")

            # Concaténer
            audio_concat = self.audio_processor.concatener_fichiers(
                self.fichiers,
                self.chemin_sortie,
                methode_tri=self.methode_tri,
                ordre_tri=self.ordre_tri
            )

            self.progress.emit(100, f"✅ Concaténation terminée : {self.chemin_sortie.name}")
            self.finished.emit(self.chemin_sortie)

        except Exception as e:
            self.error.emit(f"Erreur lors de la concaténation : {str(e)}")