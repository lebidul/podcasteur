"""
Worker pour la transcription dans un thread séparé
"""

from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import os


class TranscriptionWorker(QThread):
    """Worker pour la transcription WhisperX"""

    # Signaux
    progress = pyqtSignal(int, str)  # pourcentage, message
    finished = pyqtSignal(dict)  # résultat transcription
    error = pyqtSignal(str)  # message d'erreur

    def __init__(self, transcriber, fichier_audio, detecter_speakers=False, token_hf=None):
        super().__init__()
        self.transcriber = transcriber
        self.fichier_audio = fichier_audio
        self.detecter_speakers = detecter_speakers
        self.token_hf = token_hf

    def run(self):
        """Exécute la transcription"""
        try:
            self.progress.emit(0, "🎤 Chargement du modèle WhisperX...")

            # Transcrire
            transcription = self.transcriber.transcrire(
                Path(self.fichier_audio),
                chemin_sortie=None,
                detecter_speakers=self.detecter_speakers,
                token_hf=self.token_hf
            )

            self.progress.emit(100, "✅ Transcription terminée")
            self.finished.emit(transcription)

        except Exception as e:
            self.error.emit(f"Erreur lors de la transcription : {str(e)}")