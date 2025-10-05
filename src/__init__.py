"""
Podcasteur - Éditeur de podcasts automatisé avec IA
"""

__version__ = '1.4.0'
__author__ = 'Projet Bidul'

from .editor import PodcastEditor
from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .ai_analyzer import AIAnalyzer
from .decoupage import Decoupage

__all__ = [
    'PodcastEditor',
    'AudioProcessor',
    'Transcriber',
    'AIAnalyzer',
    'Decoupage'
]