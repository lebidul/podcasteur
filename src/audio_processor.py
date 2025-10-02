"""
Module de traitement audio
Gère la concaténation, les fondus et l'export
"""

from pydub import AudioSegment
from pydub.effects import normalize
from pathlib import Path
from typing import List, Union
import os


class AudioProcessor:
    """Gère toutes les opérations de traitement audio"""
    
    def __init__(self, config: dict):
        """
        Initialise le processeur audio avec la configuration
        
        Args:
            config: Dictionnaire de configuration
        """
        self.config = config
        self.audio_config = config['audio']
        
    def concatener_fichiers(
        self, 
        fichiers: List[Path], 
        chemin_sortie: Path,
        methode_tri: str = "nom",
        ordre_tri: str = "asc"
    ) -> AudioSegment:
        """
        Concatène plusieurs fichiers audio en un seul
        
        Args:
            fichiers: Liste des chemins des fichiers audio
            chemin_sortie: Chemin pour sauvegarder le fichier concaténé
            methode_tri: "nom" ou "date"
            ordre_tri: "asc" ou "desc"
            
        Returns:
            AudioSegment concaténé
        """
        print(f"🔗 Concaténation de {len(fichiers)} fichiers...")
        
        # Trier les fichiers
        fichiers_tries = self._trier_fichiers(fichiers, methode_tri, ordre_tri)
        
        # Charger le premier fichier
        combine = AudioSegment.from_file(fichiers_tries[0])
        print(f"  ✓ Chargé {fichiers_tries[0].name}")
        
        # Concaténer les autres
        for i, fichier in enumerate(fichiers_tries[1:], 2):
            audio = AudioSegment.from_file(fichier)
            combine += audio
            print(f"  ✓ Ajouté {fichier.name} ({i}/{len(fichiers_tries)})")
        
        # Exporter
        combine.export(chemin_sortie, format="wav")
        duree = len(combine) / 1000
        print(f"✅ Concaténation terminée : {duree:.1f}s")
        
        return combine
    
    def _trier_fichiers(
        self, 
        fichiers: List[Path], 
        methode: str, 
        ordre: str
    ) -> List[Path]:
        """Trie les fichiers par nom ou date de création"""
        inverse = (ordre == "desc")
        
        if methode == "nom":
            return sorted(fichiers, reverse=inverse)
        elif methode == "date":
            return sorted(
                fichiers, 
                key=lambda p: os.path.getctime(p), 
                reverse=inverse
            )
        else:
            raise ValueError(f"Méthode de tri inconnue : {methode}")
    
    def creer_montage(
        self,
        audio_source: Union[AudioSegment, Path],
        segments: List[dict],
        chemin_sortie: Path
    ) -> AudioSegment:
        """
        Crée la version montée avec les segments sélectionnés
        
        Args:
            audio_source: Audio source (AudioSegment ou chemin)
            segments: Liste de dictionnaires de segments avec 'debut' et 'fin' en secondes
            chemin_sortie: Chemin du fichier de sortie
            
        Returns:
            AudioSegment final monté
        """
        # Charger l'audio si c'est un chemin
        if isinstance(audio_source, Path):
            audio = AudioSegment.from_file(audio_source)
        else:
            audio = audio_source
        
        print(f"✂️  Création du montage avec {len(segments)} segments...")
        
        # Extraire les segments
        extraits = []
        for i, seg in enumerate(segments, 1):
            debut_ms = int(seg['debut'] * 1000)
            fin_ms = int(seg['fin'] * 1000)
            
            segment = audio[debut_ms:fin_ms]
            
            # Appliquer les fondus
            duree_fondu = self.audio_config['duree_fondu']
            segment = segment.fade_in(duree_fondu).fade_out(duree_fondu)
            
            extraits.append(segment)
            duree = (fin_ms - debut_ms) / 1000
            print(f"  ✓ Segment {i}: {seg['debut']:.1f}s → {seg['fin']:.1f}s ({duree:.1f}s)")
        
        # Combiner avec des silences
        duree_silence = self.audio_config['silence_entre_segments']
        silence = AudioSegment.silent(duration=duree_silence)
        
        final = extraits[0]
        for segment in extraits[1:]:
            final = final + silence + segment
        
        # Normaliser si configuré
        if self.audio_config['normaliser']:
            print("📊 Normalisation de l'audio...")
            final = normalize(final)
        
        # Exporter
        format_export = self.audio_config['format_export']
        debit = self.audio_config['debit']
        
        print(f"💾 Export en {format_export.upper()}...")
        
        params_export = {'format': format_export}
        if format_export == 'mp3':
            params_export['bitrate'] = debit
            params_export['parameters'] = ["-q:a", "2"]
        
        final.export(chemin_sortie, **params_export)
        
        duree_finale = len(final) / 1000
        taille_fichier = chemin_sortie.stat().st_size / (1024 * 1024)
        
        print(f"✅ Montage terminé : {duree_finale:.1f}s ({duree_finale/60:.1f}min)")
        print(f"📁 Taille du fichier : {taille_fichier:.2f} Mo")
        
        return final
    
    @staticmethod
    def obtenir_infos_audio(chemin_fichier: Path) -> dict:
        """Obtient les informations d'un fichier audio"""
        audio = AudioSegment.from_file(chemin_fichier)
        return {
            'duree': len(audio) / 1000,
            'canaux': audio.channels,
            'taux_echantillonnage': audio.frame_rate,
            'largeur_echantillon': audio.sample_width
        }
