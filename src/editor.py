"""
Module principal d'édition
Orchestre les workflows automatique et manuel
"""

from pathlib import Path
from typing import List, Optional, Dict
import json

from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .ai_analyzer import AIAnalyzer
from .decoupage import Decoupage


class PodcastEditor:
    """Éditeur principal de podcast - gère les deux workflows"""

    def __init__(self, config: dict, cle_api_anthropic: Optional[str] = None):
        """
        Initialise l'éditeur

        Args:
            config: Dictionnaire de configuration
            cle_api_anthropic: Clé API Anthropic (requis pour workflow auto)
        """
        self.config = config
        self.audio_processor = AudioProcessor(config)
        self.transcriber = Transcriber(config)
        self.decoupage_manager = Decoupage(config)

        if cle_api_anthropic:
            self.ai_analyzer = AIAnalyzer(config, cle_api_anthropic)
        else:
            self.ai_analyzer = None

    def workflow_automatique(
        self,
        fichiers_entree: List[Path],
        dossier_sortie: Path,
        duree_cible: Optional[int] = None,
        ton: Optional[str] = None,
        transcription_existante: Optional[Path] = None,
        detecter_speakers: bool = False
    ) -> Path:
        """
        Workflow automatique : concat → transcription → IA → montage

        Args:
            fichiers_entree: Liste des fichiers audio à traiter
            dossier_sortie: Dossier de sortie
            duree_cible: Durée cible en minutes (optionnel)
            ton: Ton souhaité (optionnel)
            transcription_existante: Chemin vers transcription existante (Feature 3)
            detecter_speakers: Active la diarisation Pyannote (optionnel)

        Returns:
            Chemin du fichier final
        """
        if not self.ai_analyzer:
            raise ValueError(
                "Le workflow automatique nécessite une clé API Anthropic"
            )

        print("\n" + "="*60)
        print("🤖 WORKFLOW AUTOMATIQUE")
        print("="*60 + "\n")

        dossier_sortie.mkdir(parents=True, exist_ok=True)

        # Étape 1 : Concaténation
        print("\n📍 ÉTAPE 1/4 : Concaténation des fichiers")
        fichier_mix = dossier_sortie / "mix_complet.wav"

        self.audio_processor.concatener_fichiers(
            fichiers_entree,
            fichier_mix,
            methode_tri=self.config['tri_fichiers']['methode'],
            ordre_tri=self.config['tri_fichiers']['ordre']
        )

        # Étape 2 : Transcription (Feature 3: skip si transcription fournie)
        if transcription_existante:
            print("\n📍 ÉTAPE 2/4 : Chargement de la transcription existante")
            print(f"📄 Utilisation de : {transcription_existante.name}")

            # Charger la transcription depuis le fichier
            transcription = self._charger_transcription(transcription_existante)
        else:
            print("\n📍 ÉTAPE 2/4 : Transcription")

            # Récupérer le token HF si diarisation demandée
            token_hf = None
            if detecter_speakers:
                import os
                token_hf = os.getenv('HUGGINGFACE_TOKEN')
                if not token_hf:
                    print("⚠️  HUGGINGFACE_TOKEN manquant dans .env")
                    print("   La diarisation sera ignorée")
                    print("   Obtenez un token sur : https://huggingface.co/settings/tokens")

            chemin_transcription = dossier_sortie / "transcription.txt"
            transcription = self.transcriber.transcrire(
                fichier_mix,
                chemin_transcription,
                detecter_speakers=detecter_speakers,
                token_hf=token_hf
            )

        # Étape 3 : Analyse IA
        print("\n📍 ÉTAPE 3/4 : Analyse IA et génération de suggestions")
        suggestions = self.ai_analyzer.analyser_transcription(
            transcription,
            duree_cible=duree_cible,
            ton=ton
        )

        # Sauvegarder les suggestions
        fichier_suggestions = dossier_sortie / "suggestions.json"
        self.ai_analyzer.sauvegarder_suggestions(suggestions, fichier_suggestions)

        # Étape 4 : Sélection utilisateur
        print("\n📍 ÉTAPE 4/4 : Sélection et montage")
        suggestions_choisies = self._demander_selection_suggestion(suggestions)

        # Montage final - peut générer plusieurs fichiers
        fichiers_finaux = []
        for i, suggestion_choisie in enumerate(suggestions_choisies, 1):
            if len(suggestions_choisies) > 1:
                print(f"\n🎬 Montage {i}/{len(suggestions_choisies)} : {suggestion_choisie['titre']}")

            fichier_final = self._monter_depuis_suggestion(
                fichier_mix,
                suggestion_choisie,
                dossier_sortie
            )
            fichiers_finaux.append(fichier_final)

        print("\n" + "="*60)
        print("✅ WORKFLOW TERMINÉ")
        print("="*60)

        if len(fichiers_finaux) == 1:
            print(f"📁 Fichier final : {fichiers_finaux[0]}")
            return fichiers_finaux[0]
        else:
            print(f"📁 {len(fichiers_finaux)} fichiers créés :")
            for f in fichiers_finaux:
                print(f"   • {f.name}")
            return fichiers_finaux[0]  # Retourne le premier pour compatibilité

    def workflow_manuel(
        self,
        fichier_decoupage: Path,
        dossier_source: Path,
        dossier_sortie: Path
    ) -> Path:
        """
        Workflow manuel : découpage prédéfini → montage direct

        Args:
            fichier_decoupage: Fichier JSON de découpage
            dossier_source: Dossier contenant les fichiers sources
            dossier_sortie: Dossier de sortie

        Returns:
            Chemin du fichier final
        """
        print("\n" + "="*60)
        print("✂️  WORKFLOW MANUEL")
        print("="*60 + "\n")

        dossier_sortie.mkdir(parents=True, exist_ok=True)

        # Charger le découpage
        print("📍 ÉTAPE 1/3 : Chargement du découpage")
        decoupage = self.decoupage_manager.charger_depuis_fichier(fichier_decoupage)

        # Valider
        print("\n📍 ÉTAPE 2/3 : Validation")
        avertissements = self.decoupage_manager.valider_avec_fichiers(
            decoupage,
            dossier_source
        )

        if avertissements:
            print("\n⚠️  AVERTISSEMENTS DÉTECTÉS :")
            for avert in avertissements:
                print(f"   {avert}")

            reponse = input("\n❓ Continuer malgré les avertissements ? (o/N) : ")
            if reponse.lower() not in ['o', 'oui', 'y', 'yes']:
                print("❌ Montage annulé")
                return None

        # Convertir en segments
        print("\n📍 ÉTAPE 3/3 : Montage")
        segments = self.decoupage_manager.convertir_en_segments(
            decoupage,
            dossier_source
        )

        # Montage final (Feature 4: avec métadonnées)
        fichier_final = self._monter_depuis_segments(
            segments,
            decoupage,
            dossier_sortie
        )

        print("\n" + "="*60)
        print("✅ WORKFLOW TERMINÉ")
        print("="*60)
        print(f"📁 Fichier final : {fichier_final}")

        return fichier_final

    def _demander_selection_suggestion(self, suggestions: List[Dict]) -> List[Dict]:
        """
        Affiche les suggestions et demande à l'utilisateur de choisir

        Args:
            suggestions: Liste de suggestions

        Returns:
            Liste des suggestions choisies (peut être multiple)
        """
        while True:  # Boucle pour permettre le raffinement
            print("\n" + "="*60)
            print("💡 SUGGESTIONS DE MONTAGE")
            print("="*60 + "\n")

            for i, suggestion in enumerate(suggestions, 1):
                print(f"{'─'*60}")
                print(f"Suggestion {i} : {suggestion['titre']}")
                print(f"{'─'*60}")
                print(f"Durée estimée : {suggestion['duree_estimee']} min")
                print(f"\n{suggestion['commentaire']}\n")

                print("Segments :")
                for j, seg in enumerate(suggestion['segments'], 1):
                    debut_str = self._formater_temps(seg['debut'])
                    fin_str = self._formater_temps(seg['fin'])
                    duree = seg['fin'] - seg['debut']
                    print(f"  {j}. [{debut_str} → {fin_str}] ({duree:.0f}s)")
                    print(f"     {seg['description']}")
                print()

            # Options de sélection
            print("="*60)
            print("Options :")
            print(f"  1-{len(suggestions)}  : Choisir une suggestion")
            print(f"  1,3        : Choisir plusieurs suggestions (créera plusieurs fichiers)")
            print(f"  1-3        : Choisir une plage (créera plusieurs fichiers)")
            print("  p          : Créer votre propre découpage")
            print("  r          : Relancer Claude avec un feedback")
            print("  q          : Quitter")
            print("="*60)

            try:
                choix = input("\n❓ Votre choix : ").strip().lower()

                # Quitter
                if choix == 'q':
                    print("\n❌ Sélection annulée")
                    exit(0)

                # Découpage personnalisé
                elif choix == 'p':
                    return [self._creer_decoupage_personnalise(suggestions)]

                # Relancer Claude
                elif choix == 'r':
                    suggestions = self._affiner_suggestions(suggestions)
                    continue  # Reboucle pour afficher les nouvelles suggestions

                # Choix de suggestion(s)
                else:
                    selections = self._parser_selection(choix, len(suggestions))
                    if selections:
                        suggestions_choisies = [suggestions[i] for i in selections]

                        # Confirmer si sélection multiple
                        if len(suggestions_choisies) > 1:
                            titres = [s['titre'] for s in suggestions_choisies]
                            print(f"\n✅ {len(suggestions_choisies)} suggestions sélectionnées :")
                            for i, titre in enumerate(titres, 1):
                                print(f"   {i}. {titre}")
                            confirmer = input("\nConfirmer ? (O/n) : ").strip().lower()
                            if confirmer in ['n', 'non', 'no']:
                                continue

                        return suggestions_choisies
                    else:
                        print(f"⚠️  Choix invalide. Exemples : 1, 1,3, 1-3")

            except KeyboardInterrupt:
                print("\n❌ Sélection annulée")
                exit(0)

    def _parser_selection(self, choix: str, max_suggestions: int) -> List[int]:
        """
        Parse le choix utilisateur et retourne la liste des indices

        Args:
            choix: Choix utilisateur (ex: "1", "1,3", "1-3")
            max_suggestions: Nombre maximum de suggestions

        Returns:
            Liste des indices (0-based) ou None si invalide
        """
        selections = []

        try:
            # Gérer les virgules : "1,3,2"
            if ',' in choix:
                for part in choix.split(','):
                    index = int(part.strip()) - 1
                    if 0 <= index < max_suggestions:
                        if index not in selections:
                            selections.append(index)
                    else:
                        return None

            # Gérer les plages : "1-3"
            elif '-' in choix and len(choix.split('-')) == 2:
                debut, fin = choix.split('-')
                debut_idx = int(debut.strip()) - 1
                fin_idx = int(fin.strip()) - 1

                if 0 <= debut_idx <= fin_idx < max_suggestions:
                    selections = list(range(debut_idx, fin_idx + 1))
                else:
                    return None

            # Choix simple : "2"
            else:
                index = int(choix) - 1
                if 0 <= index < max_suggestions:
                    selections = [index]
                else:
                    return None

            return selections

        except ValueError:
            return None

    def _creer_decoupage_personnalise(self, suggestions: List[Dict]) -> Dict:
        """
        Permet à l'utilisateur de créer son propre découpage

        Args:
            suggestions: Liste des suggestions (comme base)

        Returns:
            Découpage personnalisé sous forme de suggestion
        """
        print("\n" + "="*60)
        print("✏️  DÉCOUPAGE PERSONNALISÉ")
        print("="*60 + "\n")

        # Créer un fichier JSON temporaire avec une suggestion comme template
        import tempfile
        import subprocess
        import platform
        from pathlib import Path

        # Utiliser la première suggestion comme template
        template = {
            "titre": "Découpage personnalisé",
            "commentaire": "Créé manuellement par l'utilisateur",
            "duree_estimee": 5,
            "segments": suggestions[0]['segments'] if suggestions else [
                {
                    "debut": 0,
                    "fin": 60,
                    "description": "Segment exemple"
                }
            ]
        }

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8'
        ) as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
            temp_path = Path(f.name)

        print(f"📝 Fichier temporaire créé : {temp_path.name}")
        print("\nFormat attendu :")
        print("""
{
  "titre": "Titre de votre découpage",
  "commentaire": "Description",
  "duree_estimee": 5,
  "segments": [
    {
      "debut": 0,
      "fin": 60,
      "description": "Description du segment"
    }
  ]
}
        """)

        # Ouvrir avec l'éditeur par défaut
        try:
            system = platform.system()
            if system == 'Windows':
                import os
                os.startfile(temp_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', str(temp_path)])
            else:  # Linux
                subprocess.run(['xdg-open', str(temp_path)])

            print("\n📂 Fichier ouvert dans l'éditeur par défaut")

        except Exception as e:
            print(f"\n⚠️  Impossible d'ouvrir l'éditeur : {e}")
            print(f"Veuillez éditer manuellement : {temp_path}")

        # Attendre la fin de l'édition
        input("\n✏️  Édition du découpage personnalisé en cours. Appuyez sur Entrée quand vous avez terminé... ")

        # Charger le fichier modifié
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                decoupage_perso = json.load(f)

            # Nettoyer le fichier temporaire
            temp_path.unlink()

            print("✅ Découpage personnalisé chargé")
            return decoupage_perso

        except json.JSONDecodeError as e:
            print(f"\n❌ Erreur JSON : {e}")
            print("Le découpage personnalisé n'a pas pu être chargé.")

            # Nettoyer
            if temp_path.exists():
                temp_path.unlink()

            # Demander de recommencer
            recommencer = input("Voulez-vous réessayer ? (o/N) : ")
            if recommencer.lower() in ['o', 'oui', 'y', 'yes']:
                return self._creer_decoupage_personnalise(suggestions)
            else:
                print("Retour aux suggestions...")
                return suggestions[0]  # Fallback sur la première suggestion

    def _affiner_suggestions(self, suggestions_precedentes: List[Dict]) -> List[Dict]:
        """
        Demande un feedback et relance Claude pour affiner les suggestions

        Args:
            suggestions_precedentes: Les suggestions précédentes

        Returns:
            Nouvelles suggestions affinées
        """
        print("\n" + "="*60)
        print("🔄 AFFINER LES SUGGESTIONS")
        print("="*60 + "\n")

        print("Exemples de feedback :")
        print("  - 'Trop long, réduis à 3 minutes'")
        print("  - 'Garde plus de moments drôles'")
        print("  - 'Moins technique, plus accessible'")
        print("  - 'Focus sur l'interview avec Charlie'\n")

        feedback = input("💬 Votre feedback pour Claude : ").strip()

        if not feedback:
            print("⚠️  Aucun feedback fourni, retour aux suggestions")
            return suggestions_precedentes

        print(f"\n🤖 Relance de Claude avec votre feedback...")

        # Construire un prompt d'affinage
        prompt_affinage = f"""Voici les suggestions précédentes que tu as générées :

{json.dumps(suggestions_precedentes, indent=2, ensure_ascii=False)}

L'utilisateur a donné ce feedback :
"{feedback}"

Génère 3 nouvelles suggestions en tenant compte de ce feedback.
Garde le même format JSON que précédemment."""

        # Appeler Claude avec le nouveau prompt
        try:
            response = self.ai_analyzer.client.messages.create(
                model=self.ai_analyzer.config['modele'],
                max_tokens=4096,
                temperature=self.ai_analyzer.config['temperature'],
                messages=[{
                    "role": "user",
                    "content": prompt_affinage
                }]
            )

            # Parser la réponse
            nouvelles_suggestions = self.ai_analyzer._parser_reponse(
                response.content[0].text
            )

            print(f"✅ {len(nouvelles_suggestions)} nouvelles suggestions générées\n")
            return nouvelles_suggestions

        except Exception as e:
            print(f"\n❌ Erreur lors de l'affinage : {e}")
            print("Retour aux suggestions précédentes...")
            return suggestions_precedentes

    def _monter_depuis_suggestion(
        self,
        fichier_source: Path,
        suggestion: Dict,
        dossier_sortie: Path
    ) -> Path:
        """
        Monte le podcast depuis une suggestion IA

        Args:
            fichier_source: Fichier audio source (mix complet)
            suggestion: Suggestion choisie
            dossier_sortie: Dossier de sortie

        Returns:
            Chemin du fichier final
        """
        # Convertir les segments de suggestion en format pour audio_processor
        segments = [
            {
                'debut': seg['debut'],
                'fin': seg['fin'],
                'description': seg['description']
            }
            for seg in suggestion['segments']
        ]

        # Créer nom de fichier basé sur le titre
        nom_fichier = self._nettoyer_nom_fichier(suggestion['titre'])
        format_export = self.config['audio']['format_export']
        fichier_sortie = dossier_sortie / f"{nom_fichier}.{format_export}"

        # Monter (retourne maintenant un tuple)
        _, fichier_final = self.audio_processor.creer_montage(
            fichier_source,
            segments,
            fichier_sortie
        )

        return fichier_final

    def _monter_depuis_segments(
        self,
        segments: List[Dict],
        decoupage: Dict,
        dossier_sortie: Path
    ) -> Path:
        """
        Monte le podcast depuis des segments préparés (workflow manuel)

        Args:
            segments: Liste de segments avec audio chargé
            decoupage: Dictionnaire de découpage original
            dossier_sortie: Dossier de sortie

        Returns:
            Chemin du fichier final
        """
        # Préparer les segments pour creer_montage
        # On doit extraire l'audio et créer la structure attendue
        from pydub import AudioSegment

        # Créer un fichier temporaire avec tous les audios concaténés
        # pour pouvoir utiliser creer_montage qui attend un fichier source unique

        # Alternative: reconstruire directement ici mais en générant les métadonnées
        duree_fondu = decoupage.get('parametres', {}).get(
            'duree_fondu',
            self.config['audio']['duree_fondu']
        )

        silence_duree = decoupage.get('parametres', {}).get(
            'silence_entre_segments',
            self.config['audio']['silence_entre_segments']
        )

        print(f"🎚️  Application des fondus ({duree_fondu}ms)...")

        # Préparer métadonnées
        metadonnees_segments = []
        position_output = 0.0

        for i, seg in enumerate(segments, 1):
            seg['audio'] = seg['audio'].fade_in(duree_fondu).fade_out(duree_fondu)
            duree = len(seg['audio']) / 1000

            # Collecter métadonnées (Suggestion 2: préserver description)
            metadonnees_segments.append({
                'index': i,
                'description': seg.get('description', f'Segment {i}'),
                'debut_source': seg['debut'],
                'fin_source': seg['fin'],
                'debut_output': position_output,
                'fin_output': position_output + duree,
                'duree': duree,
                'fichier_source': seg.get('fichier', 'unknown')
            })

            silence_sec = silence_duree / 1000
            position_output += duree + silence_sec

            print(f"  ✓ Segment {i}/{len(segments)}")

        # Assembler
        silence = AudioSegment.silent(duration=silence_duree)

        print(f"🔧 Assemblage avec {silence_duree}ms de silence entre segments...")
        final = segments[0]['audio']

        for segment in segments[1:]:
            final = final + silence + segment['audio']

        # Normaliser si configuré
        if self.config['audio']['normaliser']:
            from pydub.effects import normalize
            print("📊 Normalisation de l'audio...")
            final = normalize(final)

        # Exporter avec timestamp et métadonnées dans un dossier dédié
        from datetime import datetime

        format_export = self.config['audio']['format_export']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_podcast = f"podcast_final_{timestamp}"

        # Créer un dossier pour ce podcast
        dossier_podcast = dossier_sortie / nom_podcast
        dossier_podcast.mkdir(parents=True, exist_ok=True)

        fichier_sortie = dossier_podcast / f"{nom_podcast}.{format_export}"

        print(f"💾 Export en {format_export.upper()}...")
        print(f"📁 Dossier de sortie : {dossier_podcast.name}/")

        params_export = {'format': format_export}
        if format_export == 'mp3':
            params_export['bitrate'] = self.config['audio']['debit']
            params_export['parameters'] = ["-q:a", "2"]

        final.export(fichier_sortie, **params_export)

        duree_finale = len(final) / 1000
        taille_fichier = fichier_sortie.stat().st_size / (1024 * 1024)

        print(f"✅ Montage terminé : {duree_finale:.1f}s ({duree_finale/60:.1f}min)")
        print(f"📁 Taille : {taille_fichier:.2f} Mo")
        print(f"📄 Fichier : {fichier_sortie.name}")

        # Feature 4: Générer les métadonnées pour workflow manuel
        fichier_meta = fichier_sortie.with_suffix('.json')
        self._generer_metadonnees_json(
            fichier_meta,
            fichier_sortie.name,
            duree_finale,
            metadonnees_segments
        )

        # Générer aussi les labels Audacity
        fichier_labels = fichier_sortie.with_suffix('.txt')
        self._generer_labels_audacity(
            fichier_labels,
            metadonnees_segments
        )

        return fichier_sortie

    def _generer_metadonnees_json(
        self,
        chemin_fichier: Path,
        nom_podcast: str,
        duree_totale: float,
        segments: List[dict]
    ):
        """Génère un fichier JSON avec les métadonnées du podcast"""
        from datetime import datetime

        metadonnees = {
            'podcast': nom_podcast,
            'date_creation': datetime.now().isoformat(),
            'duree_totale_secondes': round(duree_totale, 2),
            'duree_totale_minutes': round(duree_totale / 60, 2),
            'nombre_segments': len(segments),
            'segments': segments,
            'configuration': {
                'duree_fondu_ms': self.config['audio']['duree_fondu'],
                'silence_entre_segments_ms': self.config['audio']['silence_entre_segments'],
                'normalisation': self.config['audio']['normaliser'],
                'format_export': self.config['audio']['format_export'],
                'debit': self.config['audio'].get('debit', 'N/A')
            }
        }

        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(metadonnees, f, indent=2, ensure_ascii=False)

        print(f"📊 Métadonnées sauvegardées : {chemin_fichier.name}")

    def _generer_labels_audacity(
        self,
        chemin_fichier: Path,
        segments: List[dict]
    ):
        """
        Génère un fichier de labels Audacity (.txt)

        Format : start_time\tend_time\tlabel_text

        Args:
            chemin_fichier: Chemin du fichier de labels
            segments: Liste des segments avec positions output
        """
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            for seg in segments:
                debut = seg['debut_output']
                fin = seg['fin_output']
                description = seg.get('description', f"Segment {seg['index']}")

                # Format Audacity : 6 décimales, séparé par des tabs
                f.write(f"{debut:.6f}\t{fin:.6f}\t{description}\n")

        print(f"🎵 Labels Audacity sauvegardés : {chemin_fichier.name}")

    def _charger_transcription(self, chemin_fichier: Path) -> dict:
        """
        Charge une transcription depuis un fichier texte

        Args:
            chemin_fichier: Chemin vers le fichier de transcription

        Returns:
            Dictionnaire de transcription compatible
        """
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            texte = f.read()

        # Format simple: juste le texte, pas de timestamps
        # Pour des timestamps, le format attendu est:
        # [MM:SS - MM:SS] Texte du segment

        segments = []
        if '[' in texte and ']' in texte:
            # Format avec timestamps
            import re
            pattern = r'\[(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\]\s*(.+)'

            for match in re.finditer(pattern, texte, re.MULTILINE):
                debut_str, fin_str, texte_segment = match.groups()

                # Convertir MM:SS en secondes
                debut_parts = debut_str.split(':')
                debut = int(debut_parts[0]) * 60 + int(debut_parts[1])

                fin_parts = fin_str.split(':')
                fin = int(fin_parts[0]) * 60 + int(fin_parts[1])

                segments.append({
                    'debut': debut,
                    'fin': fin,
                    'texte': texte_segment.strip()
                })

        return {
            'texte': texte,
            'langue': 'fr',
            'segments': segments
        }

    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _nettoyer_nom_fichier(nom: str) -> str:
        """Nettoie un nom pour en faire un nom de fichier valide"""
        import re
        nom = re.sub(r'[^\w\s-]', '', nom)
        nom = re.sub(r'[-\s]+', '_', nom)
        return nom[:50].lower()