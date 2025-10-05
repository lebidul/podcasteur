"""
Worker pour le montage audio dans un thread séparé
"""

from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path


class MontageWorker(QThread):
    """Worker pour le montage final du podcast"""

    # Signaux
    progress = pyqtSignal(int, str)  # pourcentage, message
    finished = pyqtSignal(object)  # Path du fichier final
    error = pyqtSignal(str)  # message d'erreur

    def __init__(self, audio_processor, fichier_source, suggestion, dossier_sortie):
        super().__init__()
        self.audio_processor = audio_processor
        self.fichier_source = Path(fichier_source)
        self.suggestion = suggestion
        self.dossier_sortie = Path(dossier_sortie)

    def run(self):
        """Exécute le montage"""
        try:
            self.progress.emit(0, "✂️ Création du montage...")

            # Préparer les segments
            segments = [
                {
                    'debut': seg['debut'],
                    'fin': seg['fin'],
                    'fichier': seg.get('fichier', 'mix_complet.wav'),  # ← IMPORTANT
                    'description': seg['description']
                }
                for seg in self.suggestion['segments']
            ]

            self.progress.emit(30, f"🎬 Montage de {len(segments)} segments...")

            # Créer nom de fichier
            nom_fichier = self._nettoyer_nom_fichier(self.suggestion['titre'])
            format_export = self.audio_processor.config['audio']['format_export']
            fichier_sortie = self.dossier_sortie / f"{nom_fichier}.{format_export}"

            self.progress.emit(50, "🎵 Application des effets...")

            # Monter (retourne tuple)
            _, fichier_final = self.audio_processor.creer_montage(
                self.fichier_source,
                segments,
                fichier_sortie
            )

            self.progress.emit(100, f"✅ Montage terminé : {fichier_final.name}")
            self.finished.emit(fichier_final)

        except Exception as e:
            self.error.emit(f"Erreur lors du montage : {str(e)}")

    @staticmethod
    def _nettoyer_nom_fichier(nom: str) -> str:
        """Nettoie un nom pour en faire un nom de fichier valide"""
        import re
        nom = re.sub(r'[^\w\s-]', '', nom)
        nom = re.sub(r'[-\s]+', '_', nom)
        return nom[:50].lower()