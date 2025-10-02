"""
Podcasteur - Éditeur de podcasts automatisé avec IA
"""

__version__ = '1.0.0'
__author__ = 'Projet Bidul'

from src.editor import PodcastEditor
from src.audio_processor import AudioProcessor
from src.transcriber import Transcriber
from src.ai_analyzer import AIAnalyzer
from src.decoupage import Decoupage

__all__ = [
    'PodcastEditor',
    'AudioProcessor',
    'Transcriber',
    'AIAnalyzer',
    'Decoupage'
]
