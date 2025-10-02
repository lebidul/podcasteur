# Notes de version - Podcasteur

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