"""
Module de traitement audio
Gère la concaténation, les fondus et l'export
"""

from pydub import AudioSegment
from pydub.effects import normalize
from pathlib import Path
from typing import List, Union, Optional
import os
import json
from datetime import datetime


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
        print(f"📄 Fichier créé : {chemin_sortie.name}")

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
        chemin_sortie: Path,
        generer_metadonnees: bool = True
    ) -> tuple[AudioSegment, Path]:
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

        # Extraire les segments avec métadonnées
        extraits = []
        metadonnees_segments = []
        position_output = 0.0  # Position courante dans le fichier de sortie

        for i, seg in enumerate(segments, 1):
            debut_ms = int(seg['debut'] * 1000)
            fin_ms = int(seg['fin'] * 1000)

            segment = audio[debut_ms:fin_ms]

            # Appliquer les fondus
            duree_fondu = self.audio_config['duree_fondu']
            segment = segment.fade_in(duree_fondu).fade_out(duree_fondu)

            extraits.append(segment)
            duree = (fin_ms - debut_ms) / 1000

            # Collecter les métadonnées
            if generer_metadonnees:
                metadonnees_segments.append({
                    'index': i,
                    'description': seg.get('description', f'Segment {i}'),
                    'debut_source': seg['debut'],
                    'fin_source': seg['fin'],
                    'debut_output': position_output,
                    'fin_output': position_output + duree,
                    'duree': duree,
                    'fichier_source': seg.get('fichier', 'mix_complet.wav')
                })

                # Ajouter le silence pour la prochaine position
                silence_sec = self.audio_config['silence_entre_segments'] / 1000
                position_output += duree + silence_sec

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

        # Feature 1: Nom de fichier horodaté
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_base = chemin_sortie.stem
        nouveau_nom = f"{nom_base}_{timestamp}{chemin_sortie.suffix}"
        chemin_sortie_horodate = chemin_sortie.parent / nouveau_nom

        print(f"💾 Export en {format_export.upper()}...")

        params_export = {'format': format_export}
        if format_export == 'mp3':
            params_export['bitrate'] = debit
            params_export['parameters'] = ["-q:a", "2"]

        final.export(chemin_sortie_horodate, **params_export)

        duree_finale = len(final) / 1000
        taille_fichier = chemin_sortie_horodate.stat().st_size / (1024 * 1024)

        print(f"✅ Montage terminé : {duree_finale:.1f}s ({duree_finale/60:.1f}min)")
        print(f"📁 Taille du fichier : {taille_fichier:.2f} Mo")
        print(f"📄 Fichier : {chemin_sortie_horodate.name}")

        # Feature 2: Générer les métadonnées
        if generer_metadonnees:
            fichier_meta = chemin_sortie_horodate.with_suffix('.json')
            self._generer_metadonnees(
                fichier_meta,
                chemin_sortie_horodate.name,
                duree_finale,
                metadonnees_segments
            )

        return final, chemin_sortie_horodate

    def _generer_metadonnees(
        self,
        chemin_fichier: Path,
        nom_podcast: str,
        duree_totale: float,
        segments: List[dict]
    ):
        """Génère un fichier JSON avec les métadonnées du podcast"""

        metadonnees = {
            'podcast': nom_podcast,
            'date_creation': datetime.now().isoformat(),
            'duree_totale_secondes': round(duree_totale, 2),
            'duree_totale_minutes': round(duree_totale / 60, 2),
            'nombre_segments': len(segments),
            'segments': segments,
            'configuration': {
                'duree_fondu_ms': self.audio_config['duree_fondu'],
                'silence_entre_segments_ms': self.audio_config['silence_entre_segments'],
                'normalisation': self.audio_config['normaliser'],
                'format_export': self.audio_config['format_export'],
                'debit': self.audio_config.get('debit', 'N/A')
            }
        }

        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(metadonnees, f, indent=2, ensure_ascii=False)

        print(f"📊 Métadonnées sauvegardées : {chemin_fichier.name}")

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