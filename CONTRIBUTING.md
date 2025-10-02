# Guide de contribution - Podcasteur

Merci de votre intérêt pour contribuer à Podcasteur ! 🎙️

---

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Structure du projet](#structure-du-projet)
- [Processus de développement](#processus-de-développement)
- [Créer une release](#créer-une-release)
- [Standards de code](#standards-de-code)

---

## 🤝 Code de conduite

- Soyez respectueux et bienveillant
- Acceptez les critiques constructives
- Concentrez-vous sur ce qui est meilleur pour la communauté
- Faites preuve d'empathie envers les autres membres

---

## 💡 Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans [Issues](https://github.com/lebidul/podcasteur/issues)
2. Créez une nouvelle issue avec le template "Bug Report"
3. Décrivez le problème de manière détaillée :
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Version de Podcasteur
   - Système d'exploitation
   - Logs d'erreur

### Proposer une fonctionnalité

1. Créez une issue avec le template "Feature Request"
2. Expliquez clairement :
   - Le problème que cela résout
   - Comment cela devrait fonctionner
   - Des exemples d'utilisation

### Soumettre du code

1. **Fork** le projet
2. Créez une **branche** depuis `main` :
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. Faites vos modifications en suivant les [standards de code](#standards-de-code)
4. Ajoutez des **tests** si applicable
5. **Committez** avec des messages clairs :
   ```bash
   git commit -m "Ajout : Nouvelle fonctionnalité X"
   ```
6. **Pushez** vers votre fork :
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
7. Ouvrez une **Pull Request** vers `main`

---

## 📁 Structure du projet

```
podcasteur/
├── .github/
│   └── workflows/
│       └── release.yml      # CI/CD pour releases
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI principale
│   ├── editor.py           # Orchestration
│   ├── audio_processor.py  # Traitement audio
│   ├── transcriber.py      # Transcription
│   ├── ai_analyzer.py      # Analyse IA
│   └── decoupage.py        # Découpages manuels
├── config/
│   └── default_config.yaml
├── tests/
│   └── ...
├── docs/
│   └── ...
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🔄 Processus de développement

### Configuration de l'environnement

```bash
# Cloner votre fork
git clone https://github.com/VOTRE-USERNAME/podcasteur.git
cd podcasteur

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer en mode développement
pip install -e .
pip install pytest pytest-cov black flake8

# Installer FFmpeg (si pas déjà fait)
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### Lancer les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=src tests/

# Un test spécifique
pytest tests/test_audio_processor.py -v
```

### Formater le code

```bash
# Formater avec Black
black src/ tests/

# Vérifier avec Flake8
flake8 src/ tests/ --max-line-length=100
```

### Tester localement

```bash
# Workflow manuel
podcasteur exemple test.json
podcasteur manuel test.json test_audio/

# Workflow automatique (nécessite clé API)
podcasteur auto test_audio/*.wav --duree 3
```

---

## 🚀 Créer une release

### Prérequis

- Droits d'écriture sur le dépôt principal
- Modifications mergées dans `main`
- Tests passent

### Processus de release

#### 1. Mettre à jour RELEASE_NOTES.md

Ajoutez une nouvelle section en haut du fichier :

```markdown
## vX.Y.Z - YYYY-MM-DD

### 🎉 Titre de la version

Description des changements majeurs.

### ✨ Nouvelles fonctionnalités

- Fonctionnalité 1
- Fonctionnalité 2

### 🐛 Corrections

- Bug 1 corrigé
- Bug 2 corrigé
```

#### 2. Créer et pousser le tag

```bash
# S'assurer d'être sur main à jour
git checkout main
git pull origin main

# Créer le tag (format: vX.Y.Z)
git tag -a v1.2.3 -m "Release v1.2.3"

# Pousser le tag
git push origin v1.2.3
```

#### 3. GitHub Actions s'occupe du reste

Le workflow `.github/workflows/release.yml` va automatiquement :
1. ✅ Construire le package
2. ✅ Lancer les tests
3. ✅ Créer l'archive de release
4. ✅ Extraire les notes de version
5. ✅ Créer la release GitHub
6. ✅ Uploader les artifacts
7. ✅ (Optionnel) Publier sur PyPI

#### 4. Vérifier la release

1. Allez sur https://github.com/lebidul/podcasteur/releases
2. Vérifiez que la release est créée
3. Téléchargez et testez l'archive

### Versioning

Nous suivons [Semantic Versioning](https://semver.org/lang/fr/) :

- **MAJOR** (X.0.0) : Changements incompatibles
- **MINOR** (0.X.0) : Nouvelles fonctionnalités compatibles
- **PATCH** (0.0.X) : Corrections de bugs

Exemples :
- `v1.0.0` : Première release stable
- `v1.1.0` : Ajout d'une nouvelle fonctionnalité
- `v1.1.1` : Correction d'un bug
- `v2.0.0` : Changement majeur incompatible

### Build manuel (sans release)

Pour tester le workflow sans créer de release :

1. Allez dans l'onglet "Actions" sur GitHub
2. Sélectionnez "Build and Release - Podcasteur"
3. Cliquez sur "Run workflow"
4. Sélectionnez la branche
5. Cliquez sur "Run workflow"

Cela créera un artifact téléchargeable sans créer de release.

---

## ✅ Standards de code

### Python

- **PEP 8** pour le style
- **Black** pour le formatage automatique
- **Type hints** recommandés
- **Docstrings** pour toutes les fonctions publiques
- **Noms en français** pour variables et commentaires (accessibilité)

### Docstrings

Format Google :

```python
def ma_fonction(param1: str, param2: int) -> bool:
    """
    Description courte de la fonction.
    
    Description plus détaillée si nécessaire.
    
    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2
        
    Returns:
        Description de la valeur de retour
        
    Raises:
        ValueError: Quand param2 est négatif
    """
    pass
```

### Messages de commit

Format recommandé :

```
Type: Titre court (50 caractères max)

Description détaillée si nécessaire (72 caractères par ligne).

Types:
- Ajout: Nouvelle fonctionnalité
- Fix: Correction de bug
- Doc: Documentation
- Style: Formatage, pas de changement de code
- Refactor: Refactorisation
- Test: Ajout/modification de tests
- CI: Changements CI/CD
```

Exemples :
```
Ajout: Support du format FLAC pour l'import

Fix: Correction crash lors de fichiers vides

Doc: Mise à jour du guide de contribution
```

### Tests

- Tests unitaires dans `tests/`
- Nommer les tests `test_<fonctionnalite>.py`
- Utiliser `pytest`
- Viser >80% de couverture

Exemple :

```python
# tests/test_audio_processor.py
import pytest
from src.audio_processor import AudioProcessor

def test_concatenation_deux_fichiers():
    """Teste la concaténation de deux fichiers audio"""
    # Arrange
    config = {...}
    processor = AudioProcessor(config)
    
    # Act
    result = processor.concatener_fichiers([...])
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

---

## 📚 Ressources

- [Documentation Python](https://docs.python.org/fr/3/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Semantic Versioning](https://semver.org/lang/fr/)
- [Keep a Changelog](https://keepachangelog.com/fr/)
- [GitHub Actions](https://docs.github.com/fr/actions)

---

## ❓ Questions

Si vous avez des questions, n'hésitez pas à :
- Ouvrir une issue sur GitHub
- Consulter la [documentation](README.md)
- Contacter les mainteneurs

**Merci de contribuer à Podcasteur ! 🎉**