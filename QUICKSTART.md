# 🚀 Guide de démarrage rapide - Podcasteur

**Créez votre premier podcast en 5 minutes !**

---

## ⚡ Installation rapide

```bash
# 1. Cloner le projet
git clone https://github.com/lebidul/podcasteur.git
cd podcasteur

# 2. Installer
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install -e .

# 3. Vérifier l'installation
podcasteur info
```

---

## 🎯 Premier podcast (Mode Manuel)

**Le plus simple pour commencer :**

```bash
# 1. Créer un fichier de découpage d'exemple
podcasteur exemple mon_decoupage.json

# 2. Éditer le fichier (remplacer par vos vrais fichiers)
nano mon_decoupage.json

# 3. Créer le podcast
podcasteur manuel mon_decoupage.json dossier_audio/
```

**Exemple de fichier de découpage :**

```json
{
  "segments": [
    {
      "fichier": "intro.wav",
      "debut": 0.0,
      "fin": 30.0,
      "description": "Introduction"
    },
    {
      "fichier": "interview.wav",
      "debut": 120.0,
      "fin": 250.0,
      "description": "Meilleur moment de l'interview"
    }
  ]
}
```

✅ **Votre podcast est prêt dans `sortie/podcast_final.mp3` !**

---

## 🤖 Premier podcast (Mode Automatique)

**Avec l'aide de l'IA :**

```bash
# 1. Configurer la clé API
cp .env.example .env
nano .env  # Ajouter votre clé API Anthropic

# 2. Lancer le workflow automatique
podcasteur auto enreg1.wav enreg2.wav --duree 5

# 3. Choisir parmi les suggestions
# L'outil vous propose 3 découpages, choisissez celui qui vous plaît
```

✅ **Votre podcast est créé automatiquement !**

---

## 📝 Exemples pratiques

### Cas 1 : Plusieurs fichiers à assembler

```bash
podcasteur auto *.wav --sortie mon_podcast/
```

### Cas 2 : Podcast de 3 minutes, ton détendu

```bash
podcasteur auto audio/*.wav --duree 3 --ton "détendu et conversationnel"
```

### Cas 3 : Découpage précis et manuel

```bash
# Créer le découpage
cat > decoupage.json << EOF
{
  "segments": [
    {"fichier": "audio.wav", "debut": 10.0, "fin": 70.0, "description": "Intro"},
    {"fichier": "audio.wav", "debut": 120.0, "fin": 200.0, "description": "Corps"}
  ]
}
EOF

# Monter
podcasteur manuel decoupage.json .
```

---

## 🔧 Configuration rapide

```bash
# Créer votre config
podcasteur init-config --sortie ma_config.yaml

# Éditer les paramètres clés
nano ma_config.yaml

# Utiliser
podcasteur auto *.wav --config ma_config.yaml
```

**Paramètres à ajuster en priorité :**

```yaml
audio:
  debit: "256k"              # Qualité MP3
  duree_fondu: 800           # Fondus plus longs

transcription:
  modele: "small"            # Plus précis que 'base'

analyse_ia:
  duree_cible: 4             # Votre durée préférée
  nombre_suggestions: 2      # Moins de choix
```

---

## ❓ Aide rapide

```bash
# Aide générale
podcasteur --help

# Aide pour une commande
podcasteur auto --help
podcasteur manuel --help

# Informations sur l'outil
podcasteur info
```

---

## 🐛 Problèmes fréquents

### "FFmpeg not found"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### "ANTHROPIC_API_KEY manquante"
```bash
# Créer .env et ajouter la clé
echo "ANTHROPIC_API_KEY=votre_cle" > .env
```

### Transcription trop lente
```yaml
# Dans config, utiliser le modèle 'tiny' ou 'base'
transcription:
  modele: "base"
```

---

## 🎓 Prochaines étapes

1. **Explorez les options** : `podcasteur auto --help`
2. **Personnalisez votre config** : `podcasteur init-config`
3. **Lisez la doc complète** : [README.md](README.md)
4. **Rejoignez la communauté** : [GitHub Issues](https://github.com/lebidul/podcasteur/issues)

---

**Besoin d'aide ? Ouvrez une issue sur GitHub !**

🎙️ Bon montage avec Podcasteur !