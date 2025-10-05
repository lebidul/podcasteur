# Notes de version - Podcasteur

## v1.4.0 - 2024-10-05

### 🎉 Détection des speakers et habillage sonore

Mise à jour majeure ajoutant la diarisation (détection des intervenants) et les éléments sonores (intro/outro).

### ✨ Nouvelles fonctionnalités

#### 1. Détection des speakers avec WhisperX + Pyannote
- **Diarisation automatique** : Identifie qui parle quand dans vos enregistrements
- **WhisperX** remplace Whisper classique pour une meilleure précision des timestamps
- **Pyannote.audio** pour l'identification des intervenants
- Option `--detect-speakers` dans le CLI
- Transcription enrichie avec labels `[SPEAKER_00]`, `[SPEAKER_01]`, etc.
- Support GPU pour performances optimales
- Fallback intelligent en cas d'erreur

**Utilisation :**
```bash
podcasteur auto audio/ --duree 5 --detect-speakers
```

**Configuration requise :**
- Token HuggingFace dans `.env`
- Acceptation des conditions sur HuggingFace :
  - https://huggingface.co/pyannote/speaker-diarization-3.1
  - https://huggingface.co/pyannote/segmentation-3.0

#### 2. Éléments sonores (intro/outro)
- **Ajout automatique d'intro et outro** au montage final
- Fondus d'entrée et de sortie configurables
- Configuration via YAML
- Support de tous formats audio (MP3, WAV, OGG, etc.)
- Métadonnées et labels Audacity incluent intro/outro
- Timestamps ajustés automatiquement

**Configuration :**
```yaml
elements_sonores:
  activer: true
  generique_debut:
    fichier: "assets/intro.mp3"
    duree_fondu_sortie: 1000  # ms
  generique_fin:
    fichier: "assets/outro.mp3"
    duree_fondu_entree: 1000  # ms
```

**Structure des fichiers :**
```
podcasteur/
├── assets/
│   ├── intro.mp3
│   └── outro.mp3
```

#### 3. Option --mix pour workflow accéléré
- **Skip la concaténation** en fournissant directement un fichier déjà mixé
- Gain de temps pour itérations multiples
- Combinable avec `--transcription` pour workflow ultra-rapide

**Utilisation :**
```bash
# Utiliser un fichier déjà concaténé
podcasteur auto --mix sortie/mix_complet.wav --duree 5

# Combo ultra-rapide : skip concat + skip transcription
podcasteur auto --mix sortie/mix_complet.wav \
                --transcription sortie/transcription.txt \
                --duree 3
```

### 🔧 Améliorations

#### WhisperX (remplacement de Whisper)
- **70% plus rapide** que Whisper classique
- **Timestamps précis au mot** grâce à l'alignement forcé
- **Diarisation intégrée** sans librairie supplémentaire
- **Optimisé pour le français** avec modèles d'alignement dédiés
- **Meilleure gestion mémoire** avec libération automatique

#### Métadonnées enrichies
- Section `elements_sonores` avec durées intro/outro
- Intro et outro inclus comme segments dans la liste
- Vrais chemins de fichiers pour intro/outro
- `nombre_segments_contenu` vs `nombre_segments` (total)
- Timestamps ajustés tenant compte de l'intro

**Exemple de métadonnées :**
```json
{
  "nombre_segments": 13,
  "nombre_segments_contenu": 11,
  "elements_sonores": {
    "intro_duree_secondes": 8.5,
    "outro_duree_secondes": 12.3
  },
  "segments": [
    {
      "index": 0,
      "description": "[INTRO]",
      "fichier_source": "assets/intro.wav",
      "debut_output": 0.0,
      "fin_output": 8.5
    },
    {
      "index": 1,
      "description": "Segment 1",
      "debut_output": 8.5,
      "fin_output": 40.5
    },
    ...
    {
      "index": 12,
      "description": "[OUTRO]",
      "fichier_source": "assets/outro.wav"
    }
  ]
}
```

#### Labels Audacity améliorés
- Labels `[INTRO]` et `[OUTRO]` distincts
- Timestamps précis avec l'offset de l'intro
- Tous les segments visibles et bien positionnés

#### Suppression des warnings
- Filtrage automatique des warnings verbeux de torchaudio
- Messages de progression clairs et structurés
- Console plus lisible

### 📦 Nouvelles dépendances

```bash
# WhisperX (remplace openai-whisper)
pip install git+https://github.com/m-bain/whisperx.git

# Pyannote pour diarisation (optionnel)
pip install pyannote.audio
```

### 🔄 Migration depuis v1.3.0

1. **Installer WhisperX** :
```bash
pip uninstall openai-whisper -y
pip install git+https://github.com/m-bain/whisperx.git
```

2. **Pour la diarisation (optionnel)** :
```bash
pip install pyannote.audio
# Ajouter dans .env :
HUGGINGFACE_TOKEN=votre_token_hf
```

3. **Pour intro/outro (optionnel)** :
```bash
mkdir assets
# Placer intro.mp3 et outro.mp3 dans assets/
```

4. **Mettre à jour la config** :
```yaml
# Dans config/default_config.yaml
elements_sonores:
  activer: true  # ou false si non utilisé
```

### 🎯 Cas d'usage

**Podcast avec identification des speakers :**
```bash
podcasteur auto audio/ --duree 5 --detect-speakers
# → Transcription avec [SPEAKER_00], [SPEAKER_01]
# → Métadonnées incluent les speakers
```

**Podcast avec habillage sonore :**
```bash
# Activer elements_sonores dans la config
podcasteur auto audio/ --duree 5
# → [Intro 8s] + [Contenu 5min] + [Outro 12s] = 5min20s total
```

**Workflow ultra-rapide (ré-édition) :**
```bash
podcasteur auto --mix sortie/mix_complet.wav \
                --transcription sortie/transcription.txt \
                --duree 3
# → Skip concat + transcription = analyse IA directe
```

**Podcast complet avec tout :**
```bash
podcasteur auto audio/ --duree 5 --detect-speakers
# → WhisperX + Diarisation + IA + Montage + Intro/Outro
```

### ⚠️ Breaking Changes

- **Whisper → WhisperX** : L'API de transcription a changé (compatible en interne)
- **Métadonnées** : Nouvelle structure avec `elements_sonores` et `nombre_segments_contenu`

### 🐛 Corrections de bugs

- Fix : Gestion robuste des fondus avec valeurs None dans la config
- Fix : Attribution manuelle des speakers en fallback si WhisperX échoue
- Fix : Timestamps correctement ajustés avec intro/outro

### 📚 Documentation ajoutée

- `assets/README.md` : Guide des éléments sonores
- `GUIDE_ELEMENTS_SONORES.md` : Utilisation détaillée intro/outro
- `README_WHISPERX.md` : Migration et utilisation de WhisperX

### 🙏 Remerciements

- **WhisperX** (Max Bain) pour la transcription améliorée
- **Pyannote** (Hervé Bredin) pour la diarisation

---

## v1.3.0 - 2024-10-03

### 🎵 Intégration Audacity et organisation améliorée

Mise à jour axée sur l'intégration avec Audacity et une meilleure organisation des fichiers de sortie.

### ✨ Nouvelles fonctionnalités

- **Export de labels Audacity** : Génération automatique d'un fichier .txt de labels compatible Audacity
  - Format natif Audacity (start_time, end_time, label)
  - Importable directement via `Fichier > Importer > Labels`
  - Permet de visualiser tous les segments avec leurs descriptions
- **Organisation par dossier** : Chaque podcast est maintenant créé dans son propre sous-dossier horodaté
  - Structure claire : un dossier = un podcast complet
  - Tous les fichiers groupés (MP3, JSON, TXT)
  - Facilite l'archivage et le partage

### 🔧 Améliorations

- Affichage du nom du fichier concaténé dans la console (étape 1)
- Messages console plus clairs avec indication du dossier de sortie
- Les deux workflows (auto et manuel) génèrent maintenant les labels Audacity

### 📁 Structure de sortie

```
sortie/
└── podcast_titre_20241003_143052/
    ├── podcast_titre_20241003_143052.mp3   # Audio final
    ├── podcast_titre_20241003_143052.json  # Métadonnées
    └── podcast_titre_20241003_143052.txt   # Labels Audacity
```

### 🎯 Utilisation avec Audacity

1. Ouvrir Audacity
2. `Fichier > Ouvrir` → Sélectionner le MP3
3. `Fichier > Importer > Labels...` → Sélectionner le fichier .txt
4. Tous les segments apparaissent délimités visuellement

### 📊 Format des labels

```
0.000000	102.000000	Segment 1 - Introduction
103.000000	215.000000	Segment 2 - Interview
216.000000	291.000000	Segment 3 - Conclusion
```

Simple, stable, et parfaitement compatible avec toutes les versions d'Audacity.

---

## v1.2.0 - 2024-10-03

### 🎉 Sélection avancée et workflow interactif

Mise à jour majeure avec une interface de sélection complètement repensée pour plus de flexibilité et d'interactivité.

### ✨ Nouvelles fonctionnalités

- **Sélection multiple de suggestions** : Choisissez plusieurs suggestions en une seule commande (`1,3` ou `1-3`) et créez autant de fichiers de sortie
- **Découpage personnalisé interactif** : Option `p` pour créer votre propre découpage via l'éditeur système (JSON)
- **Affinage avec Claude** : Option `r` pour donner un feedback texte libre et obtenir de nouvelles suggestions affinées
- **Parser intelligent** : Support de multiples formats de sélection (simple, virgules, plages)
- **Confirmation automatique** : Demande de confirmation pour les sélections multiples

### 🔧 Améliorations

- Interface de sélection plus claire avec exemples
- Messages de progression pour sélection multiple
- Template JSON pré-rempli pour découpage personnalisé
- Gestion des erreurs JSON avec possibilité de réessayer
- Nettoyage automatique des fichiers temporaires

### 📝 Exemples d'usage

**Sélection multiple :**
```bash
Options :
  1-3  : Choisir une suggestion
  1,3  : Choisir plusieurs suggestions (créera plusieurs fichiers)
  1-3  : Choisir une plage (créera plusieurs fichiers)
  p    : Créer votre propre découpage
  r    : Relancer Claude avec un feedback
  q    : Quitter

Votre choix : 1,3
→ Crée 2 fichiers (suggestions 1 et 3)
```

**Affinage :**
```bash
Votre choix : r
Votre feedback : "Trop long, réduis à 3 minutes et garde plus de moments drôles"
→ Claude génère 3 nouvelles suggestions affinées
```

**Découpage personnalisé :**
```bash
Votre choix : p
→ Ouvre un fichier JSON dans votre éditeur
→ Éditez les segments selon vos besoins
→ Sauvegardez et validez
→ Le montage utilise votre découpage
```

### 🎯 Cas d'usage

Parfait pour tester rapidement plusieurs versions d'un même podcast en une seule passe, ou pour affiner progressivement les suggestions de Claude jusqu'au résultat idéal.

### ⚠️ Notes techniques

- L'affinage Claude consomme des tokens API supplémentaires (contrôlé, ~1-2€ max par podcast)
- Le découpage personnalisé nécessite un éditeur de texte par défaut configuré
- Les fichiers multiples sont nommés d'après le titre de chaque suggestion

---

## v1.1.0 - 2024-10-03

### 🎉 Améliorations majeures du workflow

Première mise à jour après la version initiale avec des fonctionnalités très demandées.

### ✨ Nouvelles fonctionnalités

- **Sortie horodatée** : Les fichiers générés incluent maintenant un timestamp (`podcast_20241003_143052.mp3`) pour éviter l'écrasement accidentel
- **Fichier de métadonnées JSON** : Chaque podcast génère un fichier `.json` contenant :
  - Durée totale et nombre de segments
  - Position de chaque segment dans le fichier source ET dans le fichier de sortie
  - Description et durée de chaque segment
  - Configuration utilisée pour le montage
- **Workflow semi-automatique** : Option `--transcription` pour fournir une transcription existante et éviter la phase Whisper (gain de temps considérable)
- **Support des dossiers en entrée** : `podcasteur auto dossier_audio/` fonctionne maintenant directement sans wildcards
- **Métadonnées réutilisables** : Le fichier JSON de métadonnées peut être utilisé comme fichier de découpage pour le workflow manuel

### 🔧 Améliorations

- Meilleurs messages dans la console avec affichage du nom du fichier créé
- Support de 8 formats audio en entrée (WAV, MP3, OGG, FLAC, M4A, AAC, WMA, OPUS)
- Workflow manuel génère maintenant aussi les métadonnées JSON
- Préservation des descriptions du découpage d'entrée dans les métadonnées de sortie
- Gestion des imports relatifs pour faciliter le debug dans PyCharm

### 📝 Changements techniques

- `AudioProcessor.creer_montage()` retourne maintenant un tuple `(AudioSegment, Path)` au lieu de juste `AudioSegment`
- Nouvelle méthode `_collecter_fichiers_audio()` dans le CLI pour gérer fichiers et dossiers
- Nouvelle méthode `_charger_transcription()` dans PodcastEditor pour le workflow semi-auto
- Format de transcription supporté : `[MM:SS - MM:SS] Texte` ou texte brut

### 🎯 Cas d'usage

**Gain de temps avec transcription existante :**
```bash
podcasteur auto audio/ --transcription ma_transcription.txt --duree 5
```

**Navigation facilitée dans le podcast :**
Le fichier JSON permet de savoir exactement où se trouve chaque segment pour l'édition post-production.

**Réédition simplifiée :**
Utilisez le JSON généré comme base pour un nouveau découpage manuel.

---

## v1.0.0 - 2024-10-02

### 🎉 Améliorations majeures du workflow

Première mise à jour après la version initiale avec des fonctionnalités très demandées.

### ✨ Nouvelles fonctionnalités

- **Sortie horodatée** : Les fichiers générés incluent maintenant un timestamp (`podcast_20241003_143052.mp3`) pour éviter l'écrasement accidentel
- **Fichier de métadonnées JSON** : Chaque podcast génère un fichier `.json` contenant :
  - Durée totale et nombre de segments
  - Position de chaque segment dans le fichier source ET dans le fichier de sortie
  - Description et durée de chaque segment
  - Configuration utilisée pour le montage
- **Workflow semi-automatique** : Option `--transcription` pour fournir une transcription existante et éviter la phase Whisper (gain de temps considérable)
- **Support des dossiers en entrée** : `podcasteur auto dossier_audio/` fonctionne maintenant directement sans wildcards
- **Métadonnées réutilisables** : Le fichier JSON de métadonnées peut être utilisé comme fichier de découpage pour le workflow manuel

### 🔧 Améliorations

- Meilleurs messages dans la console avec affichage du nom du fichier créé
- Support de 8 formats audio en entrée (WAV, MP3, OGG, FLAC, M4A, AAC, WMA, OPUS)
- Workflow manuel génère maintenant aussi les métadonnées JSON
- Préservation des descriptions du découpage d'entrée dans les métadonnées de sortie
- Gestion des imports relatifs pour faciliter le debug dans PyCharm

### 📝 Changements techniques

- `AudioProcessor.creer_montage()` retourne maintenant un tuple `(AudioSegment, Path)` au lieu de juste `AudioSegment`
- Nouvelle méthode `_collecter_fichiers_audio()` dans le CLI pour gérer fichiers et dossiers
- Nouvelle méthode `_charger_transcription()` dans PodcastEditor pour le workflow semi-auto
- Format de transcription supporté : `[MM:SS - MM:SS] Texte` ou texte brut

### 🎯 Cas d'usage

**Gain de temps avec transcription existante :**
```bash
podcasteur auto audio/ --transcription ma_transcription.txt --duree 5
```

**Navigation facilitée dans le podcast :**
Le fichier JSON permet de savoir exactement où se trouve chaque segment pour l'édition post-production.

**Réédition simplifiée :**
Utilisez le JSON généré comme base pour un nouveau découpage manuel.

---

## v1.0.0 - 2024-10-02

### 🎉 Première version stable

Première version publique de Podcasteur, l'éditeur de podcasts automatisé avec IA.

### ✨ Fonctionnalités

- **Workflow automatique** : Transcription Whisper + analyse IA Claude pour suggérer les meilleurs découpages
- **Workflow manuel** : Découpage prédéfini via fichier JSON avec validation des timestamps
- **Traitement audio** :
  - Concaténation automatique de plusieurs fichiers
  - Fondus d'entrée et de sortie configurables
  - Normalisation du volume
  - Export en MP3, WAV, OGG
- **Interface CLI** complète avec Click
- **Configuration flexible** via fichiers YAML
- **Messages en français** pour une meilleure accessibilité

### 📦 Formats supportés

- **Entrée** : WAV, MP3, OGG, FLAC, M4A, AAC
- **Sortie** : MP3, WAV, OGG

### 🔧 Modèles Whisper supportés

- tiny (rapide, moins précis)
- base (recommandé, bon compromis)
- small (plus précis)
- medium (très précis, nécessite GPU)
- large (maximum de précision, nécessite GPU puissant)

### 📖 Documentation

- Guide de démarrage rapide (QUICKSTART.md)
- Documentation complète (README.md)
- Exemples d'utilisation
- Configuration détaillée

### 🙏 Remerciements

Développé pour le collectif du Bidul et le Blue Zinc au Mans.

---

## v0.9.0-beta - 2024-09-28

### 🧪 Version bêta

Version de test interne avant la release 1.0.

### Changements

- Tests du workflow automatique
- Ajustements de l'interface CLI
- Optimisations de performance
- Corrections de bugs mineurs

---

## Format des futures versions

Chaque release suivra ce format :

```markdown
## vX.Y.Z - YYYY-MM-DD

### 🎉 Titre de la version

Description générale.

### ✨ Nouvelles fonctionnalités

- Fonctionnalité 1
- Fonctionnalité 2

### 🐛 Corrections de bugs

- Bug 1 corrigé
- Bug 2 corrigé

### 🔧 Améliorations

- Amélioration 1
- Amélioration 2

### ⚠️ Breaking Changes

- Changement incompatible 1 (si applicable)

### 📝 Notes

Notes additionnelles.
```

### 🎉 Première version stable

Première version publique de Podcasteur, l'éditeur de podcasts automatisé avec IA.

### ✨ Fonctionnalités

- **Workflow automatique** : Transcription Whisper + analyse IA Claude pour suggérer les meilleurs découpages
- **Workflow manuel** : Découpage prédéfini via fichier JSON avec validation des timestamps
- **Traitement audio** :
  - Concaténation automatique de plusieurs fichiers
  - Fondus d'entrée et de sortie configurables
  - Normalisation du volume
  - Export en MP3, WAV, OGG
- **Interface CLI** complète avec Click
- **Configuration flexible** via fichiers YAML
- **Messages en français** pour une meilleure accessibilité

### 📦 Formats supportés

- **Entrée** : WAV, MP3, OGG, FLAC, M4A, AAC
- **Sortie** : MP3, WAV, OGG

### 🔧 Modèles Whisper supportés

- tiny (rapide, moins précis)
- base (recommandé, bon compromis)
- small (plus précis)
- medium (très précis, nécessite GPU)
- large (maximum de précision, nécessite GPU puissant)

### 📖 Documentation

- Guide de démarrage rapide (QUICKSTART.md)
- Documentation complète (README.md)
- Exemples d'utilisation
- Configuration détaillée

### 🙏 Remerciements

Développé pour le collectif du Bidul et le Blue Zinc au Mans.

---

## v0.9.0-beta - 2024-09-28

### 🧪 Version bêta

Version de test interne avant la release 1.0.

### Changements

- Tests du workflow automatique
- Ajustements de l'interface CLI
- Optimisations de performance
- Corrections de bugs mineurs

---

## Format des futures versions

Chaque release suivra ce format :

```markdown
## vX.Y.Z - YYYY-MM-DD

### 🎉 Titre de la version

Description générale.

### ✨ Nouvelles fonctionnalités

- Fonctionnalité 1
- Fonctionnalité 2

### 🐛 Corrections de bugs

- Bug 1 corrigé
- Bug 2 corrigé

### 🔧 Améliorations

- Amélioration 1
- Amélioration 2

### ⚠️ Breaking Changes

- Changement incompatible 1 (si applicable)

### 📝 Notes

Notes additionnelles.
```