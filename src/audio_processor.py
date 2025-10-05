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
            audio_source: Union[AudioSegment, Path],  # Peut être ignoré si segments ont 'fichier'
            segments: List[dict],
            chemin_sortie: Path,
            generer_metadonnees: bool = True
    ) -> tuple[AudioSegment, Path]:
        """
        Crée la version montée avec les segments sélectionnés

        Args:
            audio_source: Audio source par défaut (peut être None si segments ont 'fichier')
            segments: Liste de segments avec 'debut', 'fin', 'fichier', 'description'
            ...
        """
        print(f"✂️ Création du montage avec {len(segments)} segments...")

        # Cache pour les fichiers audio
        cache_audio = {}

        extraits = []
        metadonnees_segments = []
        position_output = 0.0

        for i, seg in enumerate(segments, 1):
            # Déterminer le fichier source
            fichier_source = seg.get('fichier', 'mix_complet.wav')

            # Charger le fichier audio (avec cache)
            if fichier_source not in cache_audio:
                chemin_fichier = Path(fichier_source)
                if not chemin_fichier.exists():
                    # Si chemin absolu n'existe pas, essayer relatif à output/
                    chemin_fichier = Path('output') / fichier_source

                print(f"   📂 Chargement de {chemin_fichier.name}...")
                cache_audio[fichier_source] = AudioSegment.from_file(chemin_fichier)

            audio = cache_audio[fichier_source]

            # Extraire le segment
            debut_ms = int(seg['debut'] *
                           000)
            fin_ms = int(seg['fin'] * 1000)
            segment = audio[debut_ms:fin_ms]

            # Appliquer les fondus
            duree_fondu = self.audio_config['duree_fondu']
            segment = segment.fade_in(duree_fondu).fade_out(duree_fondu)

            extraits.append(segment)
            duree = (fin_ms - debut_ms) / 1000

            # Métadonnées
            if generer_metadonnees:
                metadonnees_segments.append({
                    'index': i,
                    'description': seg.get('description', f'Segment {i}'),
                    'debut_source': seg['debut'],
                    'fin_source': seg['fin'],
                    'debut_output': position_output,
                    'fin_output': position_output + duree,
                    'duree': duree,
                    'fichier_source': fichier_source  # ← Conserver le vrai fichier
                })

                silence_sec = self.audio_config['silence_entre_segments'] / 1000
                position_output += duree + silence_sec

            print(f"  ✓ Segment {i}: {fichier_source} [{seg['debut']:.1f}s → {seg['fin']:.1f}s] ({duree:.1f}s)")

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

        # Ajouter intro/outro si configuré et ajuster les métadonnées
        duree_intro = 0
        duree_outro = 0
        fichier_intro = None
        fichier_outro = None
        
        if self.config.get('elements_sonores', {}).get('activer'):
            print("\n🎵 Ajout des éléments sonores...")
            
            # Récupérer les noms de fichiers avant l'ajout
            config_elements = self.config['elements_sonores']
            if config_elements.get('generique_debut', {}).get('fichier'):
                fichier_intro = config_elements['generique_debut']['fichier']
            if config_elements.get('generique_fin', {}).get('fichier'):
                fichier_outro = config_elements['generique_fin']['fichier']
            
            final, duree_intro, duree_outro = self.ajouter_elements_sonores(
                final,
                config_elements
            )
            
            # Ajuster les timestamps des métadonnées si intro présente
            if duree_intro > 0 and generer_metadonnees:
                print(f"   📊 Ajustement des timestamps (+{duree_intro:.1f}s d'intro)")
                for seg in metadonnees_segments:
                    seg['debut_output'] += duree_intro
                    seg['fin_output'] += duree_intro

        # Exporter
        format_export = self.audio_config['format_export']
        debit = self.audio_config['debit']

        # Feature 1: Nom de fichier horodaté avec dossier dédié
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_base = chemin_sortie.stem
        nom_avec_timestamp = f"{nom_base}_{timestamp}"

        # Créer un dossier pour ce podcast
        dossier_podcast = chemin_sortie.parent / nom_avec_timestamp
        dossier_podcast.mkdir(parents=True, exist_ok=True)

        # Fichier de sortie dans ce dossier
        chemin_sortie_horodate = dossier_podcast / f"{nom_avec_timestamp}{chemin_sortie.suffix}"

        print(f"\n💾 Export en {format_export.upper()}...")
        print(f"📁 Dossier de sortie : {dossier_podcast.name}/")

        params_export = {'format': format_export}
        if format_export == 'mp3':
            params_export['bitrate'] = debit
            params_export['parameters'] = ["-q:a", "2"]

        final.export(chemin_sortie_horodate, **params_export)

        duree_finale = len(final) / 1000
        taille_fichier = chemin_sortie_horodate.stat().st_size / (1024 * 1024)

        print(f"✅ Montage terminé : {duree_finale:.1f}s ({duree_finale/60:.1f}min)")
        print(f"📏 Taille du fichier : {taille_fichier:.2f} Mo")
        print(f"📄 Fichier : {chemin_sortie_horodate.name}")

        # Feature 2: Générer les métadonnées avec info intro/outro
        if generer_metadonnees:
            fichier_meta = chemin_sortie_horodate.with_suffix('.json')
            self._generer_metadonnees(
                fichier_meta,
                chemin_sortie_horodate.name,
                duree_finale,
                metadonnees_segments,
                duree_intro,
                duree_outro,
                fichier_intro,
                fichier_outro
            )

            # Générer aussi les labels Audacity avec intro/outro
            fichier_labels = chemin_sortie_horodate.with_suffix('.txt')
            self._generer_labels_audacity(
                fichier_labels,
                metadonnees_segments,
                duree_intro,
                duree_outro
            )

        return final, chemin_sortie_horodate

    def ajouter_elements_sonores(
        self,
        audio_principal: AudioSegment,
        config_elements: dict
    ) -> tuple[AudioSegment, float, float]:
        """
        Ajoute intro et/ou outro au podcast
        
        Args:
            audio_principal: L'audio du podcast monté
            config_elements: Configuration des éléments sonores
            
        Returns:
            Tuple (AudioSegment avec intro/outro, durée intro, durée outro)
        """
        resultat = audio_principal
        duree_intro = 0
        duree_outro = 0
        
        # Ajouter l'intro
        generique_debut = config_elements.get('generique_debut', {})
        if generique_debut.get('fichier'):
            intro_path = Path(generique_debut['fichier'])
            
            if intro_path.exists():
                print(f"   🎵 Ajout de l'intro : {intro_path.name}")
                intro = AudioSegment.from_file(intro_path)
                
                # Récupérer le fondu avec valeur par défaut
                fondu_sortie = generique_debut.get('duree_fondu_sortie', 1000)
                if fondu_sortie and fondu_sortie > 0:
                    intro = intro.fade_out(fondu_sortie)
                
                resultat = intro + resultat
                duree_intro = len(intro) / 1000
                print(f"   ✅ Intro ajoutée ({duree_intro:.1f}s)")
            else:
                print(f"   ⚠️  Intro non trouvée : {intro_path}")
        
        # Ajouter l'outro
        generique_fin = config_elements.get('generique_fin', {})
        if generique_fin.get('fichier'):
            outro_path = Path(generique_fin['fichier'])
            
            if outro_path.exists():
                print(f"   🎵 Ajout de l'outro : {outro_path.name}")
                outro = AudioSegment.from_file(outro_path)
                
                # Récupérer le fondu avec valeur par défaut
                fondu_entree = generique_fin.get('duree_fondu_entree', 1000)
                if fondu_entree and fondu_entree > 0:
                    outro = outro.fade_in(fondu_entree)
                
                resultat = resultat + outro
                duree_outro = len(outro) / 1000
                print(f"   ✅ Outro ajoutée ({duree_outro:.1f}s)")
            else:
                print(f"   ⚠️  Outro non trouvée : {outro_path}")
        
        duree_totale_elements = duree_intro + duree_outro
        if duree_totale_elements > 0:
            print(f"   📊 Durée totale des éléments sonores : {duree_totale_elements:.1f}s")
        
        return resultat, duree_intro, duree_outro

    def _generer_metadonnees(
        self,
        chemin_fichier: Path,
        nom_podcast: str,
        duree_totale: float,
        segments: List[dict],
        duree_intro: float = 0,
        duree_outro: float = 0,
        fichier_intro: str = None,
        fichier_outro: str = None
    ):
        """Génère un fichier JSON avec les métadonnées du podcast"""

        # Construire la liste complète des segments incluant intro/outro
        tous_segments = []
        
        # Ajouter l'intro comme premier segment si présente
        if duree_intro > 0:
            tous_segments.append({
                'index': 0,
                'description': '[INTRO]',
                'debut_source': None,
                'fin_source': None,
                'debut_output': 0.0,
                'fin_output': duree_intro,
                'duree': duree_intro,
                'fichier_source': fichier_intro if fichier_intro else 'intro'
            })
        
        # Ajouter les segments de contenu
        tous_segments.extend(segments)
        
        # Ajouter l'outro comme dernier segment si présente
        if duree_outro > 0:
            if segments:
                debut_outro = segments[-1]['fin_output']
            else:
                debut_outro = duree_intro
            
            tous_segments.append({
                'index': len(segments) + 1,
                'description': '[OUTRO]',
                'debut_source': None,
                'fin_source': None,
                'debut_output': debut_outro,
                'fin_output': debut_outro + duree_outro,
                'duree': duree_outro,
                'fichier_source': fichier_outro if fichier_outro else 'outro'
            })

        metadonnees = {
            'podcast': nom_podcast,
            'date_creation': datetime.now().isoformat(),
            'duree_totale_secondes': round(duree_totale, 2),
            'duree_totale_minutes': round(duree_totale / 60, 2),
            'nombre_segments': len(tous_segments),
            'nombre_segments_contenu': len(segments),
            'elements_sonores': {
                'intro_duree_secondes': round(duree_intro, 2) if duree_intro > 0 else None,
                'outro_duree_secondes': round(duree_outro, 2) if duree_outro > 0 else None
            },
            'segments': tous_segments,
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

    def _generer_labels_audacity(
        self,
        chemin_fichier: Path,
        segments: List[dict],
        duree_intro: float = 0,
        duree_outro: float = 0
    ):
        """
        Génère un fichier de labels Audacity (.txt)

        Format : start_time\tend_time\tlabel_text

        Args:
            chemin_fichier: Chemin du fichier de labels
            segments: Liste des segments avec positions output
            duree_intro: Durée de l'intro (pour label séparé)
            duree_outro: Durée de l'outro (pour label séparé)
        """
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            # Label pour l'intro si présente
            if duree_intro > 0:
                f.write(f"0.000000\t{duree_intro:.6f}\t[INTRO]\n")
            
            # Labels pour les segments de contenu
            for seg in segments:
                debut = seg['debut_output']
                fin = seg['fin_output']
                description = seg.get('description', f"Segment {seg['index']}")

                # Format Audacity : 6 décimales, séparé par des tabs
                f.write(f"{debut:.6f}\t{fin:.6f}\t{description}\n")
            
            # Label pour l'outro si présente
            if duree_outro > 0:
                # Calculer le début de l'outro (fin du dernier segment)
                if segments:
                    debut_outro = segments[-1]['fin_output']
                    fin_outro = debut_outro + duree_outro
                    f.write(f"{debut_outro:.6f}\t{fin_outro:.6f}\t[OUTRO]\n")

        print(f"🎵 Labels Audacity sauvegardés : {chemin_fichier.name}")

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