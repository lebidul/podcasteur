# 📋 Checklist de Release - Podcasteur

Guide complet pour créer une nouvelle release de Podcasteur.

---

## 🎯 Avant de commencer

### Prérequis

- [ ] Vous avez les droits d'écriture sur le dépôt
- [ ] Toutes les modifications sont mergées dans `main`
- [ ] Les tests passent localement
- [ ] La branche `main` est à jour

### Décider du numéro de version

Suivre [Semantic Versioning](https://semver.org/lang/fr/) :

- **MAJOR** (X.0.0) : Changements incompatibles (breaking changes)
- **MINOR** (0.X.0) : Nouvelles fonctionnalités (compatibles)
- **PATCH** (0.0.X) : Corrections de bugs

**Exemples :**
- Ajout d'une GUI → `1.1.0` (minor)
- Correction d'un bug → `1.0.1` (patch)
- Refonte de l'API CLI → `2.0.0` (major)

---

## 📝 Étape 1 : Préparation

### 1.1 Mettre à jour la branche locale

```bash
git checkout main
git pull origin main
```

### 1.2 Vérifier l'état du code

```bash
# Lancer tous les tests
make test

# Vérifier le formatage
make format

# Vérifier le style
make lint

# Ou tout en une commande
make all
```

### 1.3 Mettre à jour RELEASE_NOTES.md

Ajouter une nouvelle section en **haut** du fichier :

```markdown
## vX.Y.Z - YYYY-MM-DD

### 🎉 Titre de la version

Description générale des changements.

### ✨ Nouvelles fonctionnalités

- Feature 1 : Description
- Feature 2 : Description

### 🐛 Corrections de bugs

- Bug 1 : Description de la correction
- Bug 2 : Description de la correction

### 🔧 Améliorations

- Amélioration 1
- Amélioration 2

### ⚠️ Breaking Changes (si applicable)

- Changement incompatible 1
- Migration nécessaire : ...

### 📝 Notes

Notes additionnelles importantes.
```

**Exemple concret :**

```markdown
## v1.1.0 - 2024-10-15

### 🎉 Ajout de l'export vers plateformes de podcast

Cette version ajoute la possibilité d'exporter directement vers Spotify, Apple Podcasts, etc.

### ✨ Nouvelles fonctionnalités

- Export direct vers plateformes de podcast
- Support du format FLAC en entrée
- Nouveau mode batch pour traiter plusieurs podcasts

### 🐛 Corrections de bugs

- Fix : Crash lors de fichiers audio corrompus
- Fix : Timestamps incorrects avec certains formats

### 🔧 Améliorations

- Performance : Transcription 2x plus rapide
- UX : Meilleurs messages d'erreur
- Docs : Guide d'utilisation avancée
```

### 1.4 Committer les changements

```bash
git add RELEASE_NOTES.md
git commit -m "Doc: Notes de version pour v1.1.0"
git push origin main
```

---

## 🏷️ Étape 2 : Créer le tag

### Option A : Avec le Makefile (recommandé)

```bash
make release VERSION=1.1.0
```

Cette commande va :
1. Vérifier que tout est prêt
2. Créer le tag
3. Le pousser vers GitHub

### Option B : Manuellement

```bash
# Créer le tag localement
git tag -a v1.1.0 -m "Release v1.1.0"

# Pousser le tag
git push origin v1.1.0
```

---

## 🤖 Étape 3 : Surveiller le workflow GitHub Actions

### 3.1 Accéder aux Actions

1. Aller sur https://github.com/lebidul/podcasteur/actions
2. Le workflow "Build and Release - Podcasteur" devrait se lancer automatiquement
3. Cliquer dessus pour voir les détails

### 3.2 Vérifier les étapes

Le workflow va exécuter :

- ✅ **Checkout code** : Récupération du code
- ✅ **Set up Python** : Installation de Python 3.10
- ✅ **Install dependencies** : Installation des dépendances
- ✅ **Determine Version** : Extraction du numéro de version
- ✅ **Inject Version** : Injection dans le code
- ✅ **Run tests** : Exécution des tests
- ✅ **Build package** : Construction du package
- ✅ **Package artifact** : Création de l'archive
- ✅ **Upload artifact** : Upload de l'artefact
- ✅ **Extract Release Notes** : Extraction des notes
- ✅ **Create Release** : Création de la release GitHub

### 3.3 En cas d'erreur

Si une étape échoue :

1. **Consulter les logs** : Cliquer sur l'étape en erreur
2. **Corriger localement** :
   ```bash
   git checkout main
   # Faire les corrections
   git add .
   git commit -m "Fix: Correction pour release"
   git push origin main
   ```
3. **Supprimer et recréer le tag** :
   ```bash
   # Supprimer localement
   git tag -d v1.1.0

   # Supprimer sur GitHub
   git push origin :refs/tags/v1.1.0

   # Recréer et pousser
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

---

## 🎉 Étape 4 : Vérifier la release

### 4.1 Accéder à la page de release

1. Aller sur https://github.com/lebidul/podcasteur/releases
2. Vous devriez voir "Podcasteur vX.Y.Z"

### 4.2 Vérifier le contenu

- [ ] Le titre est correct : "Podcasteur vX.Y.Z"
- [ ] Les notes de version sont affichées
- [ ] Les fichiers sont présents :
  - [ ] `podcasteur-X.Y.Z.tar.gz` (archive complète)
  - [ ] `podcasteur-X.Y.Z-py3-none-any.whl` (wheel Python)
  - [ ] `podcasteur-X.Y.Z.tar.gz` (source dist)

### 4.3 Tester la release

```bash
# Télécharger l'archive
wget https://github.com/lebidul/podcasteur/releases/download/vX.Y.Z/podcasteur-X.Y.Z.tar.gz

# Extraire
tar -xzf podcasteur-X.Y.Z.tar.gz
cd podcasteur-X.Y.Z

# Installer
pip install -r requirements.txt
pip install -e .

# Tester
podcasteur info
podcasteur exemple test.json
```

---

## 📢 Étape 5 : Communication

### 5.1 Annoncer la release

- [ ] Créer un post sur les réseaux sociaux du projet
- [ ] Mettre à jour la documentation si nécessaire
- [ ] Notifier les utilisateurs actifs

### 5.2 Mettre à jour la documentation

Si la release contient des changements majeurs :

```bash
# Mettre à jour README.md si nécessaire
# Mettre à jour QUICKSTART.md si nécessaire

git add README.md QUICKSTART.md
git commit -m "Doc: Mise à jour pour v1.1.0"
git push origin main
```

---

## 🔄 Étape 6 : Post-release

### 6.1 Préparer la prochaine version

Créer une section placeholder dans RELEASE_NOTES.md :

```markdown
## v1.2.0 - TBD

### 🚧 En développement

- Fonctionnalités à venir...
```

### 6.2 Créer un milestone GitHub

1. Aller sur https://github.com/lebidul/podcasteur/milestones
2. Créer "v1.2.0" (ou la prochaine version)
3. Assigner les issues correspondantes

### 6.3 Fermer les issues résolues

Vérifier que toutes les issues résolues dans cette release sont fermées et taggées.

---

## 🐛 Correction d'urgence (Hotfix)

Si un bug critique est découvert après une release :

### 1. Créer une branche hotfix

```bash
git checkout -b hotfix/v1.1.1 v1.1.0
```

### 2. Corriger le bug

```bash
# Faire les corrections
git add .
git commit -m "Fix: Correction bug critique X"
```

### 3. Merger dans main

```bash
git checkout main
git merge hotfix/v1.1.1
git push origin main
```

### 4. Créer la release de patch

```bash
# Mettre à jour RELEASE_NOTES.md
git add RELEASE_NOTES.md
git commit -m "Doc: Notes de version v1.1.1"
git push origin main

# Créer le tag
make release VERSION=1.1.1
```

---

## ⚠️ En cas de problème

### Supprimer une release (si vraiment nécessaire)

```bash
# Sur GitHub
# 1. Aller sur la page de la release
# 2. Cliquer "Delete this release"

# Supprimer le tag
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0
```

### Recréer une release

Suivre toutes les étapes depuis le début avec le même numéro de version.

---

## 📊 Checklist finale

Avant de considérer la release comme terminée :

- [ ] Le tag est créé et poussé
- [ ] GitHub Actions a réussi
- [ ] La release est visible sur GitHub
- [ ] Les fichiers sont téléchargeables
- [ ] Installation testée depuis l'archive
- [ ] RELEASE_NOTES.md est à jour
- [ ] Documentation mise à jour si nécessaire
- [ ] Annonce faite (si applicable)
- [ ] Issues fermées
- [ ] Milestone suivant créé

---

## 🎓 Ressources

- [Semantic Versioning](https://semver.org/lang/fr/)
- [Keep a Changelog](https://keepachangelog.com/fr/)
- [GitHub Releases](https://docs.github.com/fr/repositories/releasing-projects-on-github)
- [GitHub Actions](https://docs.github.com/fr/actions)

---

**Bon release ! 🚀**