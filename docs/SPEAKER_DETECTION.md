# 🎙️ Podcasteur avec WhisperX

## ⚡ Pourquoi WhisperX ?

Podcasteur utilise maintenant **WhisperX** au lieu de Whisper classique :

- ✅ **Plus rapide** : jusqu'à 70% plus rapide que Whisper
- ✅ **Meilleurs timestamps** : précision au mot près grâce à l'alignement
- ✅ **Diarisation intégrée** : détection des speakers sans pyannote séparé
- ✅ **Optimisé pour le français** : modèles d'alignement spécifiques
- ✅ **Meilleure gestion mémoire** : libération automatique

## 📦 Installation

```bash
# Installer WhisperX
pip install git+https://github.com/m-bain/whisperx.git

# Optionnel : Support GPU pour 10x plus rapide
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🚀 Utilisation

### Sans détection de speakers (aucune config requise)

```bash
podcasteur auto audio/ --duree 5
```

### Avec détection de speakers (nécessite token HuggingFace)

```bash
podcasteur auto audio/ --duree 5 --detect-speakers
```

## 🔑 Configuration pour la diarisation

Si vous voulez la détection des speakers :

1. **Créez un compte** sur https://huggingface.co

2. **Acceptez les conditions** (une seule fois) :
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

3. **Créez un token** : https://huggingface.co/settings/tokens
   - Type : "Read"
   - Copiez le token

4. **Ajoutez-le dans .env** :
   ```
   ANTHROPIC_API_KEY=votre_cle_claude
   HUGGINGFACE_TOKEN=votre_token_hf
   ```

## 🎯 Choix du modèle (config/default_config.yaml)

```yaml
transcription:
  modele: "base"  # Recommandé pour le français
```

### Modèles disponibles (temps pour 1h d'audio)

| Modèle | CPU | GPU | Précision | Mémoire |
|--------|-----|-----|-----------|---------|
| tiny | ~40min | ~2min | 85% | 1 GB |
| base | **~1h** | **~5min** | **90%** | **1.5 GB** |
| small | ~2h | ~10min | 94% | 2.5 GB |
| medium | ~4h | ~20min | 96% | 5 GB |
| large-v2 | ~8h | ~40min | 98% | 10 GB |

💡 **Pour Le Bidul** : `base` est parfait (rapide + précis)

## 📊 Comparaison Whisper vs WhisperX

### Exemple : 30 minutes d'audio

**Whisper classique :**
```
Transcription : 5 minutes
Timestamps : ±2-3 secondes
Diarisation : Non incluse (nécessite pyannote séparé)
Total : ~5-10 minutes
```

**WhisperX :**
```
Transcription : 3 minutes
Alignement : 1 minute
Timestamps : ±0.1 seconde (précis au mot)
Diarisation : 2 minutes (intégrée)
Total : ~6 minutes (tout inclus)
```

## 🎬 Sortie générée

Après transcription avec `--detect-speakers`, vous obtenez :

```
sortie/
└── transcription.txt                    # Texte complet
└── transcription_timestamps.txt         # Avec timestamps et speakers
```

**Exemple de transcription_timestamps.txt :**
```
[00:00 - 00:15] [SPEAKER_00] Bienvenue au Blue Zinc pour le pliage du Bidul
[00:16 - 00:32] [SPEAKER_01] Merci d'être là, on a plein de choses à partager
[00:33 - 00:58] [SPEAKER_00] Aujourd'hui on va parler de la programmation culturelle
```

## 🐛 Dépannage

### "No module named 'whisperx'"

```bash
pip install git+https://github.com/m-bain/whisperx.git
```

### "CUDA out of memory"

Réduisez la taille du modèle dans la config :
```yaml
transcription:
  modele: "tiny"  # Au lieu de "base"
```

### Diarisation ne fonctionne pas

1. Vérifiez que vous avez accepté les conditions sur HuggingFace
2. Attendez 5 minutes après l'acceptation
3. Vérifiez votre token dans `.env`
4. Essayez de régénérer un nouveau token

### WhisperX très lent (CPU)

WhisperX est optimisé pour GPU. Sur CPU :
- Utilisez `modele: "tiny"` ou `"base"`
- Comptez ~1h de traitement pour 1h d'audio avec "base"

Avec GPU (NVIDIA) :
- Installez PyTorch CUDA
- 10-20x plus rapide !

## 💡 Astuces

### Réutiliser une transcription

Si vous avez déjà transcrit, évitez de recommencer :

```bash
# 1ère fois : transcription complète
podcasteur auto audio/ --duree 5

# Réédition : utiliser la transcription existante
podcasteur auto audio/ --transcription sortie/transcription.txt --duree 3
```

### Comparer plusieurs versions rapidement

```bash
# Générer 3 versions en une commande
podcasteur auto audio/ --duree 5

# Aux suggestions, tapez : 1-3
# → Crée 3 fichiers MP3 différents
```

### Affiner avec feedback

```bash
podcasteur auto audio/ --duree 5

# Option : r (refine)
# Feedback : "Plus court, 3min max, garde les moments drôles"
# → Claude génère de nouvelles suggestions
```

## 🔬 Technique : Comment fonctionne WhisperX ?

1. **Transcription Whisper** : Génère le texte et timestamps approximatifs
2. **Forced alignment** : Aligne précisément chaque mot avec l'audio (modèle français spécifique)
3. **Diarisation** (optionnel) : Pyannote identifie qui parle quand
4. **Assignment** : Chaque mot est attribué à un speaker

Résultat : transcription parfaitement synchronisée avec identification des intervenants !

## 📚 Ressources

- WhisperX : https://github.com/m-bain/whisperx
- Pyannote : https://github.com/pyannote/pyannote-audio
- HuggingFace : https://huggingface.co