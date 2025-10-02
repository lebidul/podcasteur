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
        ton: Optional[str] = None
    ) -> Path:
        """
        Workflow automatique : concat → transcription → IA → montage
        
        Args:
            fichiers_entree: Liste des fichiers audio à traiter
            dossier_sortie: Dossier de sortie
            duree_cible: Durée cible en minutes (optionnel)
            ton: Ton souhaité (optionnel)
            
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
        
        # Étape 2 : Transcription
        print("\n📍 ÉTAPE 2/4 : Transcription")
        chemin_transcription = dossier_sortie / "transcription.txt"
        transcription = self.transcriber.transcrire(
            fichier_mix,
            chemin_transcription
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
        suggestion_choisie = self._demander_selection_suggestion(suggestions)
        
        # Montage final
        fichier_final = self._monter_depuis_suggestion(
            fichier_mix,
            suggestion_choisie,
            dossier_sortie
        )
        
        print("\n" + "="*60)
        print("✅ WORKFLOW TERMINÉ")
        print("="*60)
        print(f"📁 Fichier final : {fichier_final}")
        
        return fichier_final
    
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
        
        # Montage final
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
    
    def _demander_selection_suggestion(self, suggestions: List[Dict]) -> Dict:
        """
        Affiche les suggestions et demande à l'utilisateur de choisir
        
        Args:
            suggestions: Liste de suggestions
            
        Returns:
            Suggestion choisie
        """
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
        
        # Demander le choix
        while True:
            try:
                choix = input(f"❓ Choisissez une suggestion (1-{len(suggestions)}) : ")
                index = int(choix) - 1
                
                if 0 <= index < len(suggestions):
                    return suggestions[index]
                else:
                    print(f"⚠️  Veuillez choisir un nombre entre 1 et {len(suggestions)}")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Sélection annulée")
                exit(0)
    
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
                'fin': seg['fin']
            }
            for seg in suggestion['segments']
        ]
        
        # Créer nom de fichier basé sur le titre
        nom_fichier = self._nettoyer_nom_fichier(suggestion['titre'])
        format_export = self.config['audio']['format_export']
        fichier_sortie = dossier_sortie / f"{nom_fichier}.{format_export}"
        
        # Monter
        self.audio_processor.creer_montage(
            fichier_source,
            segments,
            fichier_sortie
        )
        
        return fichier_sortie
    
    def _monter_depuis_segments(
        self,
        segments: List[Dict],
        decoupage: Dict,
        dossier_sortie: Path
    ) -> Path:
        """
        Monte le podcast depuis des segments préparés
        
        Args:
            segments: Liste de segments avec audio chargé
            decoupage: Dictionnaire de découpage original
            dossier_sortie: Dossier de sortie
            
        Returns:
            Chemin du fichier final
        """
        # Appliquer les fondus
        duree_fondu = decoupage.get('parametres', {}).get(
            'duree_fondu',
            self.config['audio']['duree_fondu']
        )
        
        print(f"🎚️  Application des fondus ({duree_fondu}ms)...")
        for i, seg in enumerate(segments, 1):
            seg['audio'] = seg['audio'].fade_in(duree_fondu).fade_out(duree_fondu)
            print(f"  ✓ Segment {i}/{len(segments)}")
        
        # Assembler
        from pydub import AudioSegment
        
        silence_duree = decoupage.get('parametres', {}).get(
            'silence_entre_segments',
            self.config['audio']['silence_entre_segments']
        )
        
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
        
        # Exporter
        format_export = self.config['audio']['format_export']
        fichier_sortie = dossier_sortie / f"podcast_final.{format_export}"
        
        print(f"💾 Export en {format_export.upper()}...")
        
        params_export = {'format': format_export}
        if format_export == 'mp3':
            params_export['bitrate'] = self.config['audio']['debit']
            params_export['parameters'] = ["-q:a", "2"]
        
        final.export(fichier_sortie, **params_export)
        
        duree_finale = len(final) / 1000
        taille_fichier = fichier_sortie.stat().st_size / (1024 * 1024)
        
        print(f"✅ Montage terminé : {duree_finale:.1f}s ({duree_finale/60:.1f}min)")
        print(f"📁 Taille : {taille_fichier:.2f} Mo")
        
        return fichier_sortie
    
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
        # Remplacer les caractères spéciaux
        nom = re.sub(r'[^\w\s-]', '', nom)
        # Remplacer les espaces par des underscores
        nom = re.sub(r'[-\s]+', '_', nom)
        # Limiter la longueur
        return nom[:50].lower()
            