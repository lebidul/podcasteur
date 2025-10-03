"""
Module de transcription utilisant Whisper et optionnellement Pyannote pour la diarisation
"""

import whisper
from pathlib import Path
from typing import Optional


class Transcriber:
    """Gère la transcription audio avec Whisper et diarisation optionnelle"""

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
        chemin_sortie: Optional[Path] = None,
        detecter_speakers: bool = False,
        token_hf: Optional[str] = None
    ) -> dict:
        """
        Transcrit un fichier audio avec option de diarisation

        Args:
            chemin_audio: Chemin vers le fichier audio
            chemin_sortie: Chemin optionnel pour sauvegarder la transcription
            detecter_speakers: Si True, active la détection des speakers avec Pyannote
            token_hf: Token HuggingFace (requis si detecter_speakers=True)

        Returns:
            Dictionnaire de résultat avec 'texte', 'segments', 'langue'
        """
        if self.model is None:
            self.charger_modele()

        print(f"🎤 Transcription de {chemin_audio.name}...")

        # Transcrire avec Whisper
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

        # Ajouter la diarisation si demandée
        if detecter_speakers:
            if not token_hf:
                print("⚠️  Token HuggingFace manquant, diarisation ignorée")
                print("   Définissez HUGGINGFACE_TOKEN dans .env")
            else:
                transcription = self._ajouter_speakers(
                    chemin_audio,
                    transcription,
                    token_hf
                )

        # Sauvegarder si chemin fourni
        if chemin_sortie:
            self._sauvegarder_transcription(transcription, chemin_sortie)

        return transcription

    def _ajouter_speakers(
        self,
        chemin_audio: Path,
        transcription: dict,
        token_hf: str
    ) -> dict:
        """
        Ajoute l'identification des speakers via Pyannote

        Args:
            chemin_audio: Fichier audio
            transcription: Transcription Whisper
            token_hf: Token HuggingFace

        Returns:
            Transcription enrichie avec speakers
        """
        try:
            from pyannote.audio import Pipeline

            print("👥 Détection des speakers avec Pyannote...")
            print("   (Cela peut prendre quelques minutes)")

            # Charger le pipeline de diarisation
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=token_hf
            )

            # Appliquer la diarisation
            diarization = pipeline(str(chemin_audio))

            # Mapper chaque segment Whisper à un speaker
            for segment in transcription['segments']:
                debut = segment['debut']
                fin = segment['fin']
                milieu = (debut + fin) / 2

                # Trouver le speaker au milieu du segment
                speaker = None
                for turn, _, spk in diarization.itertracks(yield_label=True):
                    if turn.start <= milieu <= turn.end:
                        speaker = spk
                        break

                segment['speaker'] = speaker if speaker else "Unknown"

            # Compter les speakers détectés
            speakers = set(seg.get('speaker') for seg in transcription['segments'])
            speakers.discard('Unknown')
            speakers.discard(None)

            print(f"✅ Diarisation terminée")
            print(f"   👥 {len(speakers)} speaker(s) détecté(s) : {', '.join(sorted(speakers))}")

            return transcription

        except ImportError:
            print("⚠️  pyannote.audio non installé, diarisation ignorée")
            print("   Installez avec : pip install pyannote.audio")
            return transcription
        except Exception as e:
            print(f"⚠️  Erreur lors de la diarisation : {e}")
            print("   La transcription continue sans identification des speakers")
            return transcription

    def _sauvegarder_transcription(self, transcription: dict, chemin_sortie: Path):
        """Sauvegarde la transcription dans des fichiers"""
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

        # Sauvegarder le texte complet
        fichier_texte = chemin_sortie.with_suffix('.txt')
        with open(fichier_texte, 'w', encoding='utf-8') as f:
            f.write(transcription['texte'])

        # Sauvegarder la version avec timestamps (et speakers si disponibles)
        fichier_timestamps = chemin_sortie.with_name(
            f"{chemin_sortie.stem}_timestamps.txt"
        )
        with open(fichier_timestamps, 'w', encoding='utf-8') as f:
            for seg in transcription['segments']:
                temps_debut = self._formater_temps(seg['debut'])
                temps_fin = self._formater_temps(seg['fin'])

                # Ajouter speaker si disponible
                speaker = seg.get('speaker', '')
                prefix = f"[{speaker}] " if speaker else ""

                f.write(f"[{temps_debut} - {temps_fin}] {prefix}{seg['texte']}\n")

        print(f"💾 Transcription sauvegardée :")
        print(f"   Texte : {fichier_texte}")
        print(f"   Avec timestamps : {fichier_timestamps}")

    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"