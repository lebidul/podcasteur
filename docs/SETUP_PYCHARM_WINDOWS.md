# 🖥️ Configuration PyCharm sur Windows 11 - Podcasteur

Guide complet pour développer Podcasteur avec PyCharm sur Windows 11.

---

## 📋 Prérequis

### 1. Installer Python

- Télécharger Python 3.10+ depuis [python.org](https://www.python.org/downloads/)
- ⚠️ **Important** : Cocher "Add Python to PATH" lors de l'installation

### 2. Installer FFmpeg

**Option A : Avec Chocolatey (recommandé)**
```powershell
# Ouvrir PowerShell en administrateur
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installer FFmpeg
choco install ffmpeg
```

**Option B : Installation manuelle**
1. Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extraire dans `C:\ffmpeg`
3. Ajouter `C:\ffmpeg\bin` au PATH :
   - Rechercher "Variables d'environnement" dans Windows
   - Éditer la variable PATH
   - Ajouter `C:\ffmpeg\bin`

### 3. Installer Git

- Télécharger depuis [git-scm.com](https://git-scm.com/download/win)
- Utiliser les options par défaut

### 4. Installer PyCharm

- Télécharger [PyCharm Community](https://www.jetbrains.com/pycharm/download/#section=windows) (gratuit)
- Ou PyCharm Professional si vous l'avez

---

## 🚀 Configuration initiale du projet

### 1. Cloner le projet dans PyCharm

1. Ouvrir PyCharm
2. `Get from VCS` sur l'écran d'accueil
3. Ou `File > New > Project from Version Control`
4. URL : `https://github.com/lebidul/podcasteur.git`
5. Choisir le dossier de destination
6. Cliquer `Clone`

### 2. Configurer l'interpréteur Python

1. `File > Settings` (ou `Ctrl+Alt+S`)
2. `Project: podcasteur > Python Interpreter`
3. Cliquer sur l'icône ⚙️ > `Add`
4. Sélectionner `Virtualenv Environment`
5. Choisir `New environment`
6. Location : `venv` (dans le dossier du projet)
7. Base interpreter : Python 3.10+
8. Cocher `Make available to all projects` (optionnel)
9. Cliquer `OK`

### 3. Installer les dépendances

**Dans le terminal PyCharm** (en bas de l'écran) :

```powershell
# Activer l'environnement virtuel (automatique dans PyCharm)
# Sinon : .\venv\Scripts\activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Installer le package en mode développement
pip install -e .

# Installer les outils de développement
pip install pytest pytest-cov black flake8
```

### 4. Configurer les variables d'environnement

1. Copier `.env.example` vers `.env` :
   ```powershell
   Copy-Item .env.example .env
   ```

2. Éditer `.env` dans PyCharm :
   ```
   ANTHROPIC_API_KEY=votre_cle_api_ici
   ```

3. Configurer PyCharm pour charger `.env` :
   - `Run > Edit Configurations`
   - Cliquer `Edit configuration templates...`
   - Sélectionner `Python`
   - Dans `Environment variables`, cliquer sur l'icône dossier
   - Cocher `Load from .env file`
   - Sélectionner votre fichier `.env`

---

## 🔧 Configuration PyCharm

### 1. Configurer Black (formateur de code)

1. `File > Settings > Tools > Black`
2. Cocher `On code reformat`
3. Cocher `On save`
4. Path to Black : `<venv>\Scripts\black.exe`

**Ou installer le plugin Black :**
1. `File > Settings > Plugins`
2. Chercher "Black"
3. Installer et redémarrer

### 2. Configurer Flake8 (linter)

1. `File > Settings > Tools > External Tools`
2. Cliquer `+` pour ajouter un outil
3. Name : `Flake8`
4. Program : `$PyInterpreterDirectory$\Scripts\flake8.exe`
5. Arguments : `$FilePath$ --max-line-length=100`
6. Working directory : `$ProjectFileDir$`
7. Output filters : `$FILE_PATH$:$LINE$:$COLUMN$:.*`

### 3. Configurer les tests

1. `File > Settings > Tools > Python Integrated Tools`
2. Testing > Default test runner : `pytest`
3. Cliquer `OK`

### 4. Structure du projet

PyCharm devrait automatiquement reconnaître :
- `src/` comme dossier source (marqué en bleu)
- `tests/` comme dossier de tests (marqué en vert)

Si ce n'est pas le cas :
1. Clic droit sur `src/` > `Mark Directory as > Sources Root`
2. Clic droit sur `tests/` > `Mark Directory as > Test Sources Root`

---

## ▶️ Lancer l'application

### 1. Via le terminal PyCharm

```powershell
# Workflow manuel
podcasteur exemple test.json
podcasteur manuel test.json audio\

# Workflow automatique
podcasteur auto audio\*.wav --duree 5

# Afficher l'aide
podcasteur --help
```

### 2. Créer une configuration de Run

1. `Run > Edit Configurations`
2. Cliquer `+` > `Python`
3. Name : `Podcasteur - Exemple`
4. Script path : Cliquer sur l'icône dossier et sélectionner `src\cli.py`
5. Parameters : `exemple test.json`
6. Working directory : `$ProjectFileDir$`
7. Python interpreter : Votre venv
8. Cliquer `OK`

Vous pouvez créer plusieurs configurations :
- `Podcasteur - Manuel` : `manuel test.json audio\`
- `Podcasteur - Auto` : `auto audio\*.wav --duree 5`
- `Podcasteur - Info` : `info`

---

## 🧪 Lancer les tests

### Dans PyCharm

1. Clic droit sur le dossier `tests/`
2. `Run 'pytest in tests'`

**Ou utiliser le terminal :**
```powershell
# Tous les tests
pytest

# Avec couverture
pytest --cov=src tests\

# Un test spécifique
pytest tests\test_audio_processor.py -v
```

### Créer une configuration de test

1. `Run > Edit Configurations`
2. Cliquer `+` > `Python tests > pytest`
3. Name : `All Tests`
4. Target : `Custom`
5. Folder : `tests`
6. Cliquer `OK`

---

## 🐛 Déboguer

### 1. Déboguer le CLI

1. Créer une configuration de Run (voir ci-dessus)
2. Placer des breakpoints en cliquant dans la marge (à gauche du numéro de ligne)
3. Cliquer sur l'icône debug (🐛) à côté du bouton Run
4. Le débogueur s'arrêtera aux breakpoints

### 2. Déboguer les tests

1. Placer des breakpoints dans le code de test
2. Clic droit sur le test > `Debug 'pytest in ...'`

---

## 📦 Créer une release (sur Windows)

### 1. Tester localement

**Avec PowerShell :**
```powershell
# Version Windows du script test_release.sh
# Créer un fichier scripts\test_release.ps1

$VERSION = "1.0.0"

Write-Host "Test de release v$VERSION" -ForegroundColor Green

# Créer un venv temporaire
python -m venv .venv_test
.\.venv_test\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
pip install build wheel

# Injecter la version
"__version__ = '$VERSION'" | Out-File -FilePath "src\_version.py" -Encoding utf8

# Tests
pytest tests\

# Build
python -m build

# Nettoyage
deactivate
Remove-Item -Recurse -Force .venv_test

Write-Host "Test réussi !" -ForegroundColor Green
```

### 2. Créer le tag

**Dans le terminal PyCharm :**
```powershell
# Vérifier l'état
git status

# Mettre à jour RELEASE_NOTES.md
# Puis committer
git add RELEASE_NOTES.md
git commit -m "Doc: Notes de version v1.0.0"
git push origin main

# Créer et pousser le tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 3. Suivre le workflow GitHub Actions

1. Ouvrir https://github.com/lebidul/podcasteur/actions dans votre navigateur
2. Surveiller le workflow "Build and Release"

---

## 🔨 Outils utiles dans PyCharm

### 1. Terminal intégré

- `Alt+F12` : Ouvrir/fermer le terminal
- Supporte PowerShell par défaut
- L'environnement virtuel est automatiquement activé

### 2. Version Control

- `Alt+9` : Ouvrir l'onglet Git
- `Ctrl+K` : Commit
- `Ctrl+Shift+K` : Push
- `Ctrl+T` : Update Project (pull)

### 3. Structure du projet

- `Alt+1` : Ouvrir/fermer l'arborescence du projet
- Double-cliquer sur un fichier pour l'ouvrir

### 4. Recherche

- `Ctrl+Shift+F` : Rechercher dans tout le projet
- `Ctrl+Shift+R` : Rechercher et remplacer

### 5. Refactoring

- `Shift+F6` : Renommer
- `Ctrl+Alt+M` : Extraire en méthode
- `Ctrl+Alt+V` : Extraire en variable

---

## ⚙️ Configuration recommandée

### 1. Encodage

`File > Settings > Editor > File Encodings`
- Global Encoding : UTF-8
- Project Encoding : UTF-8
- Default encoding for properties files : UTF-8

### 2. Line Separators

`File > Settings > Editor > Code Style`
- Line separator : Unix and macOS (\n)

(Pour éviter les problèmes avec Git)

### 3. Auto-save

`File > Settings > Appearance & Behavior > System Settings`
- Cocher `Save files automatically if application is idle for X sec`

### 4. Plugins recommandés

`File > Settings > Plugins` :
- `.env files support`
- `Markdown`
- `YAML`
- `Black` (formateur)
- `GitToolBox` (améliorations Git)

---

## 🐛 Problèmes courants sur Windows

### Erreur : "python not found"

```powershell
# Vérifier l'installation
python --version

# Si erreur, réinstaller Python en cochant "Add to PATH"
```

### Erreur : "ffmpeg not found"

```powershell
# Vérifier l'installation
ffmpeg -version

# Si erreur, vérifier le PATH ou réinstaller
```

### Erreur : Scripts disabled

```powershell
# Exécuter en PowerShell admin
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Environnement virtuel ne s'active pas

Dans PyCharm Terminal :
```powershell
# Activer manuellement
.\venv\Scripts\Activate.ps1

# Ou utiliser cmd
venv\Scripts\activate.bat
```

### Problème de permissions Git

```powershell
# Configurer Git
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"

# Configurer les credentials
git config --global credential.helper wincred
```

---

## 📚 Raccourcis clavier utiles

| Action | Raccourci |
|--------|-----------|
| Run | `Shift+F10` |
| Debug | `Shift+F9` |
| Terminal | `Alt+F12` |
| Git | `Alt+9` |
| Search Everywhere | `Double Shift` |
| Format Code | `Ctrl+Alt+L` |
| Optimize Imports | `Ctrl+Alt+O` |
| Comment/Uncomment | `Ctrl+/` |
| Duplicate Line | `Ctrl+D` |
| Delete Line | `Ctrl+Y` |

---

## ✅ Checklist de configuration

- [ ] Python 3.10+ installé
- [ ] FFmpeg installé et dans le PATH
- [ ] Git installé et configuré
- [ ] PyCharm installé
- [ ] Projet cloné
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] `.env` configuré avec clé API
- [ ] Tests passent
- [ ] `podcasteur info` fonctionne

---

**Vous êtes prêt à développer avec PyCharm ! 🎉**

Pour toute question, consultez la [documentation PyCharm](https://www.jetbrains.com/help/pycharm/) ou ouvrez une issue sur GitHub.