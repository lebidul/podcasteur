# Notes de version - Podcasteur

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