# FICHIER: src/gui/workers/ai_worker.py

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

    def __init__(self, analyzer, transcription, duree_cible=None, ton=None, nombre_suggestions=None):
        super().__init__()
        self.analyzer = analyzer
        self.transcription = transcription
        self.duree_cible = duree_cible
        self.ton = ton
        self.nombre_suggestions = nombre_suggestions  # ← AJOUTER ce paramètre

    def run(self):
        """Exécute l'analyse IA"""
        try:
            self.progress.emit(0, "🤖 Analyse en cours avec Claude...")

            # Analyser la transcription
            suggestions = self.analyzer.analyser_transcription(
                self.transcription,
                duree_cible=self.duree_cible,
                ton=self.ton,
                nombre_suggestions=self.nombre_suggestions  # ← PASSER le paramètre
            )

            self.progress.emit(100, "✅ Analyse IA terminée")
            self.finished.emit(suggestions)

        except Exception as e:
            self.error.emit(f"Erreur lors de l'analyse IA : {str(e)}")