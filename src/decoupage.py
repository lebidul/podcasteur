"""
Module de gestion des découpages
Charge, valide et convertit les fichiers de découpage
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from pydub import AudioSegment


class Decoupage:
    """Gère les fichiers de découpage pour le montage manuel"""
    
    def __init__(self, config: dict):
        """
        Initialise le gestionnaire de découpage
        
        Args:
            config: Dictionnaire de configuration
        """
        self.config = config
        self.validation_config = config.get('validation', {})
    
    def charger_depuis_fichier(self, chemin_fichier: Path) -> Dict:
        """
        Charge un fichier de découpage JSON
        
        Args:
            chemin_fichier: Chemin vers le fichier JSON
            
        Returns:
            Dictionnaire de découpage
        """
        print(f"📄 Chargement du découpage depuis {chemin_fichier.name}...")
        
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            decoupage = json.load(f)
        
        # Valider la structure
        self._valider_structure(decoupage)
        
        nb_segments = len(decoupage['segments'])
        print(f"✅ Découpage chargé : {nb_segments} segments")
        
        return decoupage
    
    def _valider_structure(self, decoupage: Dict):
        """Valide la structure du fichier de découpage"""
        if 'segments' not in decoupage:
            raise ValueError("Le fichier de découpage doit contenir une clé 'segments'")
        
        if not isinstance(decoupage['segments'], list):
            raise ValueError("'segments' doit être une liste")
        
        if len(decoupage['segments']) == 0:
            raise ValueError("Le découpage doit contenir au moins un segment")
        
        # Valider chaque segment
        for i, segment in enumerate(decoupage['segments']):
            self._valider_segment(segment, i)
    
    def _valider_segment(self, segment: Dict, index: int):
        """Valide un segment individuel"""
        champs_requis = ['fichier', 'debut', 'fin']
        
        for champ in champs_requis:
            if champ not in segment:
                raise ValueError(
                    f"Segment {index + 1} : champ '{champ}' manquant"
                )
        
        # Vérifier que debut < fin
        if segment['debut'] >= segment['fin']:
            raise ValueError(
                f"Segment {index + 1} : 'debut' ({segment['debut']}) doit être "
                f"inférieur à 'fin' ({segment['fin']})"
            )
        
        # Vérifier que les valeurs sont positives
        if segment['debut'] < 0 or segment['fin'] < 0:
            raise ValueError(
                f"Segment {index + 1} : les timestamps doivent être positifs"
            )
    
    def valider_avec_fichiers(
        self, 
        decoupage: Dict, 
        dossier_source: Path
    ) -> List[str]:
        """
        Valide que les fichiers référencés existent et que les timestamps sont valides
        
        Args:
            decoupage: Dictionnaire de découpage
            dossier_source: Dossier contenant les fichiers audio sources
            
        Returns:
            Liste des avertissements (vide si tout est OK)
        """
        if not self.validation_config.get('verifier_timestamps', True):
            return []
        
        print("🔍 Validation des segments avec les fichiers audio...")
        
        avertissements = []
        tolerance = self.validation_config.get('tolerance_timestamps', 0.5)
        
        # Charger les durées des fichiers
        durees_fichiers = {}
        
        for segment in decoupage['segments']:
            nom_fichier = segment['fichier']
            
            # Vérifier que le fichier existe
            chemin_fichier = dossier_source / nom_fichier
            if not chemin_fichier.exists():
                avertissements.append(
                    f"⚠️  Fichier non trouvé : {nom_fichier}"
                )
                continue
            
            # Obtenir la durée du fichier (cache)
            if nom_fichier not in durees_fichiers:
                try:
                    audio = AudioSegment.from_file(chemin_fichier)
                    durees_fichiers[nom_fichier] = len(audio) / 1000
                except Exception as e:
                    avertissements.append(
                        f"⚠️  Impossible de lire {nom_fichier} : {e}"
                    )
                    continue
            
            duree = durees_fichiers[nom_fichier]
            
            # Vérifier les timestamps
            if segment['fin'] > duree:
                depassement = segment['fin'] - duree
                if depassement > tolerance:
                    avertissements.append(
                        f"⚠️  {nom_fichier} : fin ({segment['fin']:.1f}s) dépasse "
                        f"la durée du fichier ({duree:.1f}s) de {depassement:.1f}s"
                    )
                else:
                    # Ajustement automatique dans la tolérance
                    segment['fin'] = duree
                    print(f"   ℹ️  Ajustement automatique : fin → {duree:.1f}s")
        
        if avertissements:
            print(f"⚠️  {len(avertissements)} avertissement(s) détecté(s)")
        else:
            print("✅ Validation réussie : tous les segments sont valides")
        
        return avertissements
    
    def convertir_en_segments(
        self, 
        decoupage: Dict,
        dossier_source: Path
    ) -> List[Dict]:
        """
        Convertit le découpage en liste de segments prêts pour le montage
        
        Args:
            decoupage: Dictionnaire de découpage
            dossier_source: Dossier contenant les fichiers sources
            
        Returns:
            Liste de segments avec les AudioSegments chargés
        """
        print(f"📦 Préparation des segments pour le montage...")
        
        segments_prepares = []
        cache_audio = {}
        
        for i, segment in enumerate(decoupage['segments'], 1):
            nom_fichier = segment['fichier']
            chemin_fichier = dossier_source / nom_fichier
            
            # Charger le fichier audio (avec cache)
            if nom_fichier not in cache_audio:
                print(f"   Chargement de {nom_fichier}...")
                cache_audio[nom_fichier] = AudioSegment.from_file(chemin_fichier)
            
            audio_source = cache_audio[nom_fichier]
            
            # Extraire le segment
            debut_ms = int(segment['debut'] * 1000)
            fin_ms = int(segment['fin'] * 1000)
            audio_segment = audio_source[debut_ms:fin_ms]
            
            segments_prepares.append({
                'audio': audio_segment,
                'debut': segment['debut'],
                'fin': segment['fin'],
                'fichier': nom_fichier,
                'description': segment.get('description', f'Segment {i}')
            })
        
        print(f"✅ {len(segments_prepares)} segments prêts")
        
        return segments_prepares
    
    @staticmethod
    def creer_exemple(chemin_sortie: Path, avec_commentaires: bool = True):
        """
        Crée un fichier de découpage d'exemple
        
        Args:
            chemin_sortie: Chemin où créer le fichier
            avec_commentaires: Inclure des commentaires explicatifs
        """
        exemple = {
            "segments": [
                {
                    "fichier": "enregistrement_01.wav",
                    "debut": 166.0,
                    "fin": 268.0,
                    "description": "Introduction et contexte"
                },
                {
                    "fichier": "enregistrement_01.wav",
                    "debut": 281.0,
                    "fin": 393.0,
                    "description": "Interview principale"
                },
                {
                    "fichier": "enregistrement_03.wav",
                    "debut": 45.0,
                    "fin": 120.0,
                    "description": "Conclusion"
                }
            ],
            "parametres": {
                "duree_fondu": 500,
                "silence_entre_segments": 1000
            }
        }
        
        if avec_commentaires:
            exemple["_commentaires"] = {
                "fichier": "Nom du fichier audio source (relatif au dossier d'entrée)",
                "debut": "Temps de début en secondes (peut avoir des décimales)",
                "fin": "Temps de fin en secondes",
                "description": "Description optionnelle du segment",
                "parametres": "Paramètres optionnels (remplacent la config par défaut)"
            }
        
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
        
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump(exemple, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Fichier d'exemple créé : {chemin_sortie}")
