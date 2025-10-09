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
        
        # Calculer quelques statistiques pour aider Claude
        duree_totale_sec = transcription['segments'][-1]['fin'] if transcription['segments'] else 0
        duree_totale_min = duree_totale_sec / 60

        prompt = f"""Tu es un expert en montage de podcasts et en storytelling audio. Analyse cette transcription d'un reportage audio et propose {nombre_suggestions} découpages différents et SPÉCIFIQUES.

📊 INFORMATIONS SUR L'AUDIO:
- Durée totale: {duree_totale_min:.1f} minutes ({duree_totale_sec:.0f} secondes)
- Nombre de segments: {len(transcription['segments'])}

🎯 OBJECTIFS:
- Durée cible du podcast final: {duree_cible} minutes
- Ton souhaité: {ton}

📝 TRANSCRIPTION COMPLÈTE AVEC TIMESTAMPS:
{transcription_formatee}

⚠️ RÈGLES CRITIQUES:
1. **SPÉCIFICITÉ OBLIGATOIRE**: Chaque segment DOIT citer des PASSAGES PRÉCIS de la transcription
2. **CONTEXTE RÉEL**: Utilise les VRAIS contenus, phrases, et moments de la transcription ci-dessus
3. **PAS DE GÉNÉRALITÉS**: Interdiction de dire "moments intéressants" ou "passages clés" sans les citer
4. **CITATIONS EXACTES**: Dans chaque description, cite au moins UNE phrase ou expression exacte de ce segment
5. **JUSTIFICATION CONCRÈTE**: Explique POURQUOI ce passage précis est important (avec citation)

📋 EXEMPLES DE CE QU'IL FAUT FAIRE:
✅ BON: "Segment [02:15-03:45] où il explique 'la technique du micro-caché permet...' - moment clé car révèle sa méthode"
✅ BON: "Garder l'anecdote [05:20-06:10] sur 'le jour où j'ai interviewé...' - apporte de l'émotion"
❌ MAUVAIS: "Segment intéressant sur la technique" (trop vague, pas de citation)
❌ MAUVAIS: "Passage sur une anecdote" (aucun contexte précis)

🎬 VARIÉTÉ DES SUGGESTIONS:
- Suggestion 1: Version "Best-of" - Les moments les plus forts avec impact maximal
- Suggestion 2: Version "Narrative" - Une histoire cohérente du début à la fin
- Suggestion 3: Version "Thématique" - Focalisée sur un angle ou thème particulier

IMPORTANT: Ta réponse doit être au format JSON suivant (et UNIQUEMENT du JSON valide):

{{
  "suggestions": [
    {{
      "titre": "Titre descriptif et accrocheur",
      "commentaire": "Explication détaillée: pourquoi ces segments? Quelle histoire racontent-ils? Quel est l'angle éditorial?",
      "duree_estimee": durée_en_minutes,
      "segments": [
        {{
          "debut": temps_debut_en_secondes,
          "fin": temps_fin_en_secondes,
          "description": "Description SPÉCIFIQUE avec CITATION d'une phrase ou expression exacte de ce segment pour prouver que tu as lu la transcription"
        }}
      ]
    }}
  ]
}}

🚀 Génère maintenant les {nombre_suggestions} suggestions en étant TRÈS SPÉCIFIQUE sur le contenu réel de la transcription."""

        return prompt

    def _formater_transcription_pour_prompt(self, transcription: dict) -> str:
        """Formate la transcription avec timestamps pour le prompt"""
        lignes = []

        # Ajouter un en-tête si la transcription a des speakers
        has_speakers = any('speaker' in seg for seg in transcription['segments'])

        for seg in transcription['segments']:
            debut = self._formater_temps(seg['debut'])
            fin = self._formater_temps(seg['fin'])

            # Ajouter le speaker si disponible
            if has_speakers and 'speaker' in seg:
                speaker = seg['speaker']
                lignes.append(f"[{debut} - {fin}] [{speaker}] {seg['texte']}")
            else:
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