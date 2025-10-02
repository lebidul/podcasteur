"""
Module de transcription utilisant Whisper
"""

import whisper
from pathlib import Path
from typing import Optional


class Transcriber:
    """Gère la transcription audio avec Whisper"""
    
    def __init__(self, config: dict):
        """
        Initialise le transcripteur avec la configuration
        
        Args:
            config: Dictionnaire de configuration
        """
        self.config = config['transcription']
        self.model = None
        
    def charger_modele(self):
        """Charge le modèle Whisper"""
        nom_modele = self.config['modele']
        print(f"🤖 Chargement du modèle Whisper '{nom_modele}'...")
        print("   (Cela peut prendre du temps au premier lancement)")
        
        self.model = whisper.load_model(nom_modele)
        print("✅ Modèle chargé")
    
    def transcrire(
        self, 
        chemin_audio: Path, 
        chemin_sortie: Optional[Path] = None
    ) -> dict:
        """
        Transcrit un fichier audio
        
        Args:
            chemin_audio: Chemin vers le fichier audio
            chemin_sortie: Chemin optionnel pour sauvegarder la transcription
            
        Returns:
            Dictionnaire de résultat avec 'texte', 'segments', etc.
        """
        if self.model is None:
            self.charger_modele()
        
        print(f"🎤 Transcription de {chemin_audio.name}...")
        
        # Transcrire
        langue = self.config.get('langue')
        
        resultat = self.model.transcribe(
            str(chemin_audio),
            language=langue,
            verbose=False
        )
        
        # Formater le résultat
        transcription = {
            'texte': resultat['text'],
            'langue': resultat['language'],
            'segments': []
        }
        
        # Traiter les segments avec timestamps
        for segment in resultat['segments']:
            transcription['segments'].append({
                'debut': segment['start'],
                'fin': segment['end'],
                'texte': segment['text'].strip()
            })
        
        print(f"✅ Transcription terminée : {len(transcription['texte'])} caractères")
        print(f"   Langue détectée : {resultat['language']}")
        print(f"   {len(transcription['segments'])} segments")
        
        # Sauvegarder si chemin fourni
        if chemin_sortie:
            self._sauvegarder_transcription(transcription, chemin_sortie)
        
        return transcription
    
    def _sauvegarder_transcription(self, transcription: dict, chemin_sortie: Path):
        """Sauvegarde la transcription dans un fichier"""
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le texte complet
        fichier_texte = chemin_sortie.with_suffix('.txt')
        with open(fichier_texte, 'w', encoding='utf-8') as f:
            f.write(transcription['texte'])
        
        # Sauvegarder la version avec timestamps
        fichier_timestamps = chemin_sortie.with_name(
            f"{chemin_sortie.stem}_timestamps.txt"
        )
        with open(fichier_timestamps, 'w', encoding='utf-8') as f:
            for seg in transcription['segments']:
                temps_debut = self._formater_temps(seg['debut'])
                temps_fin = self._formater_temps(seg['fin'])
                f.write(f"[{temps_debut} - {temps_fin}] {seg['texte']}\n")
        
        print(f"💾 Transcription sauvegardée :")
        print(f"   Texte : {fichier_texte}")
        print(f"   Avec timestamps : {fichier_timestamps}")
    
    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"
