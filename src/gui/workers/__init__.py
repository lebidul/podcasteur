"""
Workers pour l'exécution asynchrone des tâches longues
"""

from .transcription_worker import TranscriptionWorker

__all__ = ['TranscriptionWorker']