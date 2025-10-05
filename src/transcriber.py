"""
Module de transcription utilisant WhisperX avec diarisation intégrée
"""

import whisperx
from pathlib import Path
from typing import Optional
import torch
import gc
import warnings
import os

# Supprimer les warnings verbeux de torchaudio et pyannote
warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio")
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
warnings.filterwarnings("ignore", message=".*torchaudio.*")
warnings.filterwarnings("ignore", message=".*TorchCodec.*")

# Supprimer aussi les logs HuggingFace si trop verbeux
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'


class Transcriber:
    """Gère la transcription audio avec WhisperX et diarisation"""

    def __init__(self, config: dict):
        """
        Initialise le transcripteur avec la configuration

        Args:
            config: Dictionnaire de configuration
        """
        self.config = config['transcription']
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"

    def charger_modele(self):
        """Charge le modèle WhisperX"""
        nom_modele = self.config['modele']
        print(f"🤖 Chargement du modèle WhisperX '{nom_modele}'...")
        print(f"   🖥️  Device : {self.device.upper()}")
        print("   (Cela peut prendre du temps au premier lancement)")

        self.model = whisperx.load_model(
            nom_modele,
            self.device,
            compute_type=self.compute_type
        )
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
            detecter_speakers: Si True, active la détection des speakers
            token_hf: Token HuggingFace (requis si detecter_speakers=True)

        Returns:
            Dictionnaire de résultat avec 'texte', 'segments', 'langue'
        """
        if self.model is None:
            self.charger_modele()

        print(f"🎤 Transcription de {chemin_audio.name}...")

        # Charger l'audio
        audio = whisperx.load_audio(str(chemin_audio))

        # Étape 1 : Transcription (optimisée pour le français)
        print("   📝 Transcription en cours (français)...")

        resultat = self.model.transcribe(
            audio,
            language="fr",  # Toujours français
            batch_size=16
        )

        langue_detectee = "fr"
        print(f"   ✅ Transcription terminée (langue: {langue_detectee})")

        # Étape 2 : Alignment pour de meilleurs timestamps (français)
        print("   🎯 Alignement des timestamps...")
        try:
            model_a, metadata = whisperx.load_align_model(
                language_code="fr",
                device=self.device
            )

            resultat = whisperx.align(
                resultat["segments"],
                model_a,
                metadata,
                audio,
                self.device,
                return_char_alignments=False
            )

            # Libérer la mémoire
            del model_a
            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()

            print("   ✅ Alignement terminé")
        except Exception as e:
            print(f"   ⚠️  Alignement ignoré : {e}")
            # Continuer sans alignment
            resultat = {"segments": resultat["segments"]}

        # Étape 3 : Diarisation si demandée
        if detecter_speakers:
            if not token_hf:
                print("   ⚠️  Token HuggingFace manquant, diarisation ignorée")
                print("      Définissez HUGGINGFACE_TOKEN dans .env")
            else:
                resultat = self._ajouter_speakers(
                    str(chemin_audio),  # Passer le chemin du fichier
                    resultat,
                    token_hf
                )

        # Formater le résultat
        transcription = self._formater_resultat(resultat, langue_detectee)

        print(f"✅ Transcription complète : {len(transcription['texte'])} caractères")
        print(f"   📊 {len(transcription['segments'])} segments")

        # Sauvegarder si chemin fourni
        if chemin_sortie:
            self._sauvegarder_transcription(transcription, chemin_sortie)

        return transcription

    def _ajouter_speakers(
        self,
        chemin_audio: str,
        resultat: dict,
        token_hf: str
    ) -> dict:
        """
        Ajoute l'identification des speakers avec Pyannote via WhisperX

        Args:
            chemin_audio: Chemin vers le fichier audio
            resultat: Résultat de transcription alignée
            token_hf: Token HuggingFace

        Returns:
            Résultat enrichi avec speakers
        """
        try:
            print("   👥 Détection des speakers...")

            # Utiliser directement pyannote.audio
            from pyannote.audio import Pipeline

            # Charger le pipeline de diarisation
            print("   📦 Chargement du modèle de diarisation...")
            diarize_model = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=token_hf
            )
            print("   ✅ Modèle chargé")

            # Appliquer la diarisation (prend un chemin de fichier)
            print("   🔄 Analyse audio (1/2) : identification des intervenants...")
            diarize_segments = diarize_model(chemin_audio)
            print("   ✅ Intervenants identifiés")

            # Utiliser la fonction d'assignment de WhisperX
            print("   🎯 Analyse audio (2/2) : attribution aux segments...")

            # Vérifier que resultat contient 'segments'
            if 'segments' not in resultat or not resultat['segments']:
                print("   ⚠️  Pas de segments à traiter pour la diarisation")
                return resultat

            # WhisperX assign_word_speakers attend seulement 2 arguments :
            # - diarize_segments (résultat de pyannote)
            # - transcript (le résultat de l'alignement avec 'segments' et optionnellement 'word_segments')
            try:
                resultat_diarize = whisperx.assign_word_speakers(
                    diarize_segments,
                    resultat
                )
            except (KeyError, TypeError) as e:
                print(f"   ⚠️  Erreur d'attribution (segments incompatibles) : {e}")
                print("   💡 Attribution manuelle par segment...")

                # Fallback : attribution manuelle segment par segment
                resultat_diarize = self._attribution_manuelle_speakers(
                    diarize_segments,
                    resultat
                )

            print("   ✅ Attribution terminée")

            # Compter les speakers
            speakers = set()
            for seg in resultat_diarize.get("segments", []):
                speaker = seg.get("speaker")
                if speaker:
                    speakers.add(speaker)

            if speakers:
                print(f"\n   ✅ Diarisation réussie !")
                print(f"   👥 {len(speakers)} speaker(s) détecté(s) : {', '.join(sorted(speakers))}\n")
            else:
                print(f"\n   ⚠️  Aucun speaker détecté (fichier mono-locuteur ?)\n")

            return resultat_diarize

        except ImportError as e:
            print("\n   ⚠️  pyannote.audio n'est pas installé")
            print("   💡 Installez avec : pip install pyannote.audio\n")
            return resultat

        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"\n   ⚠️  Erreur lors de la diarisation : {error_msg}\n")

            if "404" in error_msg or "not found" in error_msg.lower():
                print("   💡 Solutions :")
                print("      1. Acceptez les conditions sur HuggingFace :")
                print("         • https://huggingface.co/pyannote/speaker-diarization-3.1")
                print("         • https://huggingface.co/pyannote/segmentation-3.0")
                print("      2. Attendez 5-10 minutes après l'acceptation")
                print("      3. Vérifiez votre token dans .env\n")
            elif "torch" in error_msg.lower():
                print("   💡 Le problème semble lié à PyTorch")
                print("      Réinstallez : pip install torch torchaudio\n")
            else:
                print("   🐛 Trace complète :")
                traceback.print_exc()
                print()

            print("   ⏭️  La transcription continuera sans détection de speakers\n")
            return resultat

    def _attribution_manuelle_speakers(
        self,
        diarize_segments,
        resultat: dict
    ) -> dict:
        """
        Attribution manuelle des speakers aux segments (fallback)

        Args:
            diarize_segments: Résultat de pyannote
            resultat: Transcription alignée

        Returns:
            Résultat avec speakers attribués
        """
        # Convertir diarize_segments en liste de (start, end, speaker)
        speaker_intervals = []
        for turn, _, speaker in diarize_segments.itertracks(yield_label=True):
            speaker_intervals.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker
            })

        # Attribuer chaque segment au speaker majoritaire
        for segment in resultat['segments']:
            seg_start = segment['start']
            seg_end = segment['end']
            seg_mid = (seg_start + seg_end) / 2

            # Trouver le speaker au milieu du segment
            speaker = None
            max_overlap = 0

            for interval in speaker_intervals:
                # Calculer l'overlap entre le segment et l'intervalle speaker
                overlap_start = max(seg_start, interval['start'])
                overlap_end = min(seg_end, interval['end'])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    speaker = interval['speaker']

            segment['speaker'] = speaker if speaker else "SPEAKER_UNKNOWN"

        return resultat

    def _formater_resultat(self, resultat: dict, langue: str) -> dict:
        """Formate le résultat WhisperX au format attendu"""
        segments_formates = []
        texte_complet = []

        for seg in resultat.get("segments", []):
            segment = {
                'debut': seg['start'],
                'fin': seg['end'],
                'texte': seg['text'].strip()
            }

            # Ajouter le speaker si présent
            if 'speaker' in seg:
                segment['speaker'] = seg['speaker']

            segments_formates.append(segment)
            texte_complet.append(seg['text'].strip())

        return {
            'texte': ' '.join(texte_complet),
            'langue': langue,
            'segments': segments_formates
        }

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
        print(f"   📄 Texte : {fichier_texte.name}")
        print(f"   ⏱️  Avec timestamps : {fichier_timestamps.name}")

    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"