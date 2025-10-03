# Notes de version - Podcasteur

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

### 📝 Format des labels

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