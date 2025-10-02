"""
Module d'analyse IA utilisant l'API Claude
"""

import anthropic
import json
from typing import List, Dict, Optional
from pathlib import Path


class AIAnalyzer:
    """Analyse les transcriptions et suggère des points de montage avec Claude"""
    
    def __init__(self, config: dict, cle_api: str):
        """
        Initialise l'analyseur IA
        
        Args:
            config: Dictionnaire de configuration
            cle_api: Clé API Anthropic
        """
        self.config = config['analyse_ia']
        self.client = anthropic.Anthropic(api_key=cle_api)
    
    def analyser_transcription(
        self, 
        transcription: dict,
        duree_cible: Optional[int] = None,
        ton: Optional[str] = None,
        nombre_suggestions: Optional[int] = None
    ) -> List[Dict]:
        """
        Analyse la transcription et suggère des segments de montage
        
        Args:
            transcription: Dictionnaire de transcription avec 'texte' et 'segments'
            duree_cible: Durée cible en minutes (remplace la config)
            ton: Ton souhaité (remplace la config)
            nombre_suggestions: Nombre de suggestions (remplace la config)
            
        Returns:
            Liste de dictionnaires de suggestions
        """
        # Utiliser les valeurs fournies ou celles de la config
        duree_cible = duree_cible or self.config['duree_cible']
        ton = ton or self.config['ton']
        nombre_suggestions = nombre_suggestions or self.config['nombre_suggestions']
        
        print(f"🤖 Analyse de la transcription avec Claude...")
        print(f"   Durée cible : {duree_cible} minutes")
        print(f"   Ton souhaité : {ton}")
        print(f"   Suggestions à générer : {nombre_suggestions}")
        
        # Construire le prompt
        prompt = self._construire_prompt(
            transcription, 
            duree_cible, 
            ton, 
            nombre_suggestions
        )
        
        # Appeler l'API Claude
        reponse = self.client.messages.create(
            model=self.config['modele'],
            max_tokens=4096,
            temperature=self.config['temperature'],
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parser la réponse
        suggestions = self._parser_reponse(reponse.content[0].text)
        
        print(f"✅ Analyse terminée : {len(suggestions)} suggestions générées")
        
        return suggestions
    
    def _construire_prompt(
        self, 
        transcription: dict, 
        duree_cible: int, 
        ton: str, 
        nombre_suggestions: int
    ) -> str:
        """Construit le prompt pour Claude"""
        
        # Formater la transcription avec timestamps
        transcription_formatee = self._formater_transcription_pour_prompt(transcription)
        
        prompt = f"""Tu es un expert en montage de podcasts. Analyse cette transcription d'un reportage audio et propose {nombre_suggestions} découpages différents.

TRANSCRIPTION AVEC TIMESTAMPS:
{transcription_formatee}

CONSIGNES:
- Durée cible du podcast final: {duree_cible} minutes
- Ton souhaité: {ton}
- Identifie les moments les plus intéressants, dynamiques, et pertinents
- Pour chaque suggestion, fournis:
  1. Un titre descriptif
  2. Une liste de segments à garder (avec timestamps debut/fin en secondes)
  3. Un commentaire expliquant les choix de montage
  4. La durée totale estimée

IMPORTANT: Ta réponse doit être au format JSON suivant (et UNIQUEMENT du JSON valide, sans texte avant ou après):

{{
  "suggestions": [
    {{
      "titre": "Titre de la suggestion",
      "commentaire": "Explication des choix de montage",
      "duree_estimee": duree_en_minutes,
      "segments": [
        {{"debut": temps_debut_en_secondes, "fin": temps_fin_en_secondes, "description": "Description du segment"}},
        ...
      ]
    }},
    ...
  ]
}}

Génère maintenant les {nombre_suggestions} suggestions."""

        return prompt
    
    def _formater_transcription_pour_prompt(self, transcription: dict) -> str:
        """Formate la transcription avec timestamps pour le prompt"""
        lignes = []
        for seg in transcription['segments']:
            debut = self._formater_temps(seg['debut'])
            fin = self._formater_temps(seg['fin'])
            lignes.append(f"[{debut} - {fin}] {seg['texte']}")
        return "\n".join(lignes)

    def _parser_reponse(self, texte_reponse: str) -> List[Dict]:
        """Parse la réponse JSON de Claude"""
        try:
            # Nettoyer les balises markdown si présentes
            texte = texte_reponse.strip()

            # Supprimer ```json au début et ``` à la fin
            if texte.startswith('```'):
                # Trouver la première ligne (qui contient ```json ou juste ```)
                premiere_ligne = texte.split('\n')[0]
                texte = texte[len(premiere_ligne):].strip()

                # Supprimer ``` de fin
                if texte.endswith('```'):
                    texte = texte[:-3].strip()

            # Essayer d'extraire le JSON
            idx_debut = texte.find('{')
            idx_fin = texte.rfind('}') + 1

            # Si on trouve des crochets avant les accolades, c'est un array
            idx_debut_array = texte.find('[')
            if idx_debut_array != -1 and idx_debut_array < idx_debut:
                idx_debut = idx_debut_array
                idx_fin = texte.rfind(']') + 1

            if idx_debut == -1 or idx_fin == 0:
                raise ValueError("Aucun JSON trouvé dans la réponse")

            texte_json = texte[idx_debut:idx_fin]
            donnees = json.loads(texte_json)

            # Si c'est un array direct, retourner tel quel
            if isinstance(donnees, list):
                return donnees

            # Sinon chercher la clé 'suggestions'
            return donnees.get('suggestions', [])

        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing de la réponse Claude : {e}")
            print(f"Texte de la réponse : {texte_reponse[:500]}...")
            raise
    
    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def sauvegarder_suggestions(self, suggestions: List[Dict], chemin_sortie: Path):
        """Sauvegarde les suggestions dans un fichier JSON"""
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
        
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump({"suggestions": suggestions}, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Suggestions sauvegardées dans {chemin_sortie}")
