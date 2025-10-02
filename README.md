# 🎙️ Podcasteur

**Éditeur de podcasts automatisé avec IA**

Podcasteur transforme vos enregistrements audio bruts en podcasts montés de qualité, avec deux modes de fonctionnement :
- **Automatique** : transcription + suggestions IA via Claude
- **Manuel** : découpage prédéfini dans un fichier JSON

---

## 📁 Structure du projet

```
podcasteur/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Interface ligne de commande
│   ├── editor.py           # Orchestration des workflows
│   ├── audio_processor.py  # Traitement audio
│   ├── transcriber.py      # Transcription Whisper
│   ├── ai_analyzer.py      # Analyse IA avec Claude
│   └── decoupage.py        # Gestion des découpages manuels
├── config/
│   └── default_config.yaml # Configuration par défaut
├── tests/
│   └── ...                 # Tests unitaires
├── .env.example            # Exemple de configuration
├── requirements.txt        # Dépendances Python
├── setup.py               # Installation du package
└── README.md              # Documentation
```

---

## 🔧 Architecture technique

### Workflow Automatique

```
Fichiers audio multiples
    ↓
[AudioProcessor] Concaténation séquentielle
    ↓
mix_complet.wav
    ↓
[Transcriber] Transcription Whisper
    ↓
transcription.txt + timestamps
    ↓
[AIAnalyzer] Analyse avec Claude API
    ↓
Suggestions de découpage (JSON)
    ↓
[Interface utilisateur] Sélection
    ↓
[AudioProcessor] Montage final
    ↓
podcast_final.mp3
```

### Workflow Manuel

```
Fichiers audio multiples + decoupage.json
    ↓
[Decoupage] Validation des timestamps
    ↓
[Decoupage] Chargement des segments
    ↓
[AudioProcessor] Montage avec fondus
    ↓
podcast_final.mp3
```

---

## 🐛 Dépannage

### Erreur : FFmpeg not found

```bash
# Vérifier l'installation
ffmpeg -version

# Si absent, installer (voir section Prérequis)
```

### Erreur : ANTHROPIC_API_KEY manquante

```bash
# Créer le fichier .env
cp .env.example .env

# Éditer et ajouter votre clé
nano .env
```

### Erreur : Modèle Whisper très lent

Le modèle `base` est rapide. Si vous avez utilisé `medium` ou `large`, essayez :

```yaml
transcription:
  modele: "base"  # Plus rapide
```

### Timestamps invalides dans le découpage manuel

L'outil valide automatiquement et vous avertit. Ajustez dans le fichier JSON :

```json
{
  "segments": [
    {
      "fichier": "audio.wav",
      "debut": 10.0,
      "fin": 50.0  // Assurez-vous que fin < durée du fichier
    }
  ]
}
```

### Qualité audio médiocre

Augmentez le bitrate dans la config :

```yaml
audio:
  debit: "320k"  # Meilleure qualité
```

---

## 🎓 Concepts clés

### Fondus (Fades)

Les fondus en entrée et sortie adoucissent les transitions entre segments :
- **Fondu d'entrée** : le volume monte progressivement
- **Fondu de sortie** : le volume descend progressivement
- Durée configurable (défaut : 500ms)

### Normalisation

La normalisation ajuste le volume pour qu'il soit constant dans tout le podcast. Recommandé pour mixer des sources avec des volumes différents.

### Transcription

Whisper transcrit l'audio en texte avec timestamps. Modèles disponibles :
- `tiny` : très rapide, moins précis
- `base` : bon compromis (recommandé)
- `small` : plus précis, plus lent
- `medium`/`large` : très précis, très lent (GPU recommandé)

### Analyse IA

Claude analyse la transcription et suggère les meilleurs segments selon :
- La durée cible
- Le ton souhaité
- La cohérence narrative
- Les moments intéressants

---

## 🚀 Développement

### Installation en mode développement

```bash
# Cloner le dépôt
git clone https://github.com/lebidul/podcasteur.git
cd podcasteur

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation en mode éditable
pip install -e .

# Installer les dépendances de développement
pip install pytest pytest-cov black flake8
```

### Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/test_audio_processor.py
```

### Formatage du code

```bash
# Formater avec Black
black src/

# Vérifier avec Flake8
flake8 src/
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork** le projet
2. Créez une **branche** pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Committez** vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. **Pushez** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une **Pull Request**

### Guidelines

- Code en français (commentaires, variables, messages)
- Suivre la convention PEP 8
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation

---

## 📝 TODO / Roadmap

- [ ] Interface graphique (GUI) avec PyQt ou Tkinter
- [ ] Support de formats audio additionnels (FLAC, AAC)
- [ ] Ajout automatique d'intro/outro musicale
- [ ] Détection automatique des silences à couper
- [ ] Égalisation audio avancée
- [ ] Export vers plateformes de podcast
- [ ] Support multi-langues pour l'interface
- [ ] Mode batch pour traiter plusieurs podcasts
- [ ] Intégration avec services de stockage cloud
- [ ] API REST pour intégration externe

---

## 📄 Licence

MIT License

Copyright (c) 2024 Projet Bidul

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Remerciements

- **Whisper** (OpenAI) pour la transcription
- **Claude** (Anthropic) pour l'analyse IA
- **PyDub** pour le traitement audio
- **Click** pour l'interface CLI
- Le collectif du **Bidul** et le **Blue Zinc** au Mans pour l'inspiration

---

## 📞 Contact

- **Projet** : https://github.com/lebidul/podcasteur
- **Issues** : https://github.com/lebidul/podcasteur/issues
- **Le Bidul** : [Fanzine culturel du Mans](https://lebidul.org)

---

## 📊 Statistiques

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-orange.svg)

---

**Fait avec ❤️ pour la communauté du Bidul**✨ Fonctionnalités

- 🔗 **Concaténation automatique** de plusieurs fichiers audio
- 🎤 **Transcription** avec Whisper (local, gratuit)
- 🤖 **Analyse IA** avec Claude pour suggérer les meilleurs découpages
- ✂️ **Montage automatique** avec fondus et silences configurables
- 📊 **Normalisation audio** pour un volume constant
- 🎚️ **Configuration flexible** via YAML
- 💾 **Export** en MP3, WAV, OGG

---

## 📋 Prérequis

- Python 3.8+
- FFmpeg
- (Optionnel) Clé API Anthropic pour le mode automatique

### Installation de FFmpeg

**Ubuntu/Debian :**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS (Homebrew) :**
```bash
brew install ffmpeg
```

**Windows :**
Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html)

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/lebidul/podcasteur.git
cd podcasteur
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer Podcasteur

```bash
pip install -e .
```

### 5. Configurer la clé API (pour mode automatique)

```bash
cp .env.example .env
# Éditez .env et ajoutez votre clé API Anthropic
```

Obtenez votre clé API sur : https://console.anthropic.com

---

## 📖 Utilisation

### Mode Automatique (avec IA)

Transcription + analyse IA + montage automatique :

```bash
# Exemple simple - dossier complet
podcasteur auto audio/ --duree 5

# Avec fichiers spécifiques
podcasteur auto enreg_01.wav enreg_02.wav --duree 5 --ton "dynamique"

# Avec wildcards
podcasteur auto *.wav --duree 5 --sortie mon_podcast/

# Avec transcription existante (skip Whisper, plus rapide)
podcasteur auto audio/ --transcription transcript.txt --duree 5

# Avec configuration personnalisée
podcasteur auto *.wav --config ma_config.yaml
```

**Options :**
- `--duree, -d` : Durée cible en minutes
- `--ton, -t` : Ton souhaité (ex: "détendu et conversationnel")
- `--transcription` : Fichier de transcription existant (pour skip la transcription Whisper)
- `--sortie, -o` : Dossier de sortie (défaut: `sortie/`)
- `--config, -c` : Fichier de configuration personnalisé

**Sortie générée :**
- `podcast_titre_20241003_143052.mp3` - Le podcast final
- `podcast_titre_20241003_143052.json` - Les métadonnées complètes

### Mode Manuel (découpage prédéfini)

Montage direct depuis un fichier JSON :

```bash
# 1. Créer un fichier de découpage d'exemple
podcasteur exemple mon_decoupage.json

# 2. Éditer le fichier JSON selon vos besoins

# 3. Lancer le montage
podcasteur manuel mon_decoupage.json dossier_audio/ --sortie mon_podcast/
```

**Format du fichier de découpage :**

```json
{
  "segments": [
    {
      "fichier": "enregistrement_01.wav",
      "debut": 166.0,
      "fin": 268.0,
      "description": "Introduction"
    },
    {
      "fichier": "enregistrement_02.wav",
      "debut": 45.0,
      "fin": 120.0,
      "description": "Interview principale"
    }
  ],
  "parametres": {
    "duree_fondu": 500,
    "silence_entre_segments": 1000
  }
}
```

### Autres commandes

```bash
# Créer une configuration personnalisée
podcasteur init-config --sortie ma_config.yaml

# Afficher les informations
podcasteur info

# Aide
podcasteur --help
podcasteur auto --help
podcasteur manuel --help
```

---

## ⚙️ Configuration

### Fichier de configuration (YAML)

Créez votre configuration personnalisée :

```bash
podcasteur init-config --sortie config/ma_config.yaml
```

Éditez ensuite le fichier pour ajuster :

```yaml
# Paramètres audio
audio:
  format_export: "mp3"        # mp3, wav, ogg
  debit: "192k"               # 128k, 192k, 256k, 320k
  duree_fondu: 500            # Durée des fondus (ms)
  silence_entre_segments: 1000 # Silence entre segments (ms)
  normaliser: true            # Normaliser le volume

# Transcription
transcription:
  modele: "base"              # tiny, base, small, medium, large
  langue: "fr"                # Code langue ou null pour auto-détection
  dossier_sortie: "transcriptions"

# Analyse IA
analyse_ia:
  modele: "claude-sonnet-4-5-20250929"
  duree_cible: 5              # Durée cible en minutes
  ton: "informatif et dynamique"
  nombre_suggestions: 3       # Nombre de propositions
  temperature: 0.7            # Créativité (0.0-1.0)

# Validation
validation:
  verifier_timestamps: true
  tolerance_timestamps: 0.5   # Tolérance en secondes
```

---

## 🎯 Exemples d'utilisation

### Cas d'usage 1 : Reportage au pliage du Bidul

```bash
# Workflow automatique avec dossier
podcasteur auto audio_bidul/ --duree 5 --ton "détendu et convivial" --sortie bidul_octobre/

# L'outil va :
# 1. Concaténer tous les fichiers du dossier
# 2. Transcrire l'audio
# 3. Analyser avec Claude
# 4. Proposer 3 découpages
# 5. Vous laisser choisir
# 6. Créer le montage final avec métadonnées
```

### Cas d'usage 2 : Réutiliser une transcription

```bash
# Si vous avez déjà transcrit avec Whisper
podcasteur auto audio/ --transcription ma_transcription.txt --duree 5

# Gain de temps : skip la transcription (peut prendre plusieurs minutes)
```

### Cas d'usage 3 : Rééditer un podcast

```bash
# Utiliser le JSON généré comme base
# Le fichier podcast_20241003_143052.json contient tous les segments

# Éditer le JSON pour ajuster les découpes
# Puis relancer en workflow manuel
podcasteur manuel podcast_20241003_143052.json audio/ --sortie nouvelle_version/
```

### Cas d'usage 2 : Interview en plusieurs parties

```bash
# Créer le découpage
podcasteur exemple interview_decoupage.json

# Éditer le fichier pour définir les segments

# Monter
podcasteur manuel interview_decoupage.json enregistrements/ --sortie interview_finale/
```

### Cas d'usage 3 : Série de podcasts avec même configuration

```bash
# Créer votre config une fois
podcasteur init-config --sortie serie_config.yaml

# Utiliser pour chaque épisode
podcasteur auto episode1/*.wav --config serie_config.yaml --sortie ep1/
podcasteur auto episode2/*.wav --config serie_config.yaml --sortie ep2/
```

---

##