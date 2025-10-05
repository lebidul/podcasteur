"""
Worker pour l'analyse IA dans un thread séparé
"""

from PyQt6.QtCore import QThread, pyqtSignal


class AIWorker(QThread):
    """Worker pour l'analyse IA avec Claude"""

    # Signaux
    progress = pyqtSignal(int, str)  # pourcentage, message
    finished = pyqtSignal(list)  # liste de suggestions
    error = pyqtSignal(str)  # message d'erreur

    def __init__(self, ai_analyzer, transcription, duree_cible=None, ton=None):
        super().__init__()
        self.ai_analyzer = ai_analyzer
        self.transcription = transcription
        self.duree_cible = duree_cible
        self.ton = ton

    def run(self):
        """Exécute l'analyse IA"""
        try:
            self.progress.emit(0, "🤖 Analyse de la transcription avec Claude...")

            # Analyser
            suggestions = self.ai_analyzer.analyser_transcription(
                self.transcription,
                duree_cible=self.duree_cible,
                ton=self.ton
            )

            self.progress.emit(100, f"✅ Analyse terminée : {len(suggestions)} suggestions générées")
            self.finished.emit(suggestions)

        except Exception as e:
            self.error.emit(f"Erreur lors de l'analyse IA : {str(e)}")