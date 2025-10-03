# 👥 Détection de speakers (Diarisation)

Guide pour utiliser la fonctionnalité optionnelle de détection et identification des speakers dans Podcasteur.

---

## 📋 Qu'est-ce que la diarisation ?

La diarisation audio est le processus d'identification des différents speakers (interlocuteurs) dans un enregistrement audio. Au lieu d'avoir simplement :

```
[00:30 - 02:45] Bonjour, je suis très heureux d'être ici...
```

Vous obtenez :

```
[00:30 - 02:45] [SPEAKER_00] Bonjour, je suis très heureux d'être ici...
[02:46 - 05:10] [SPEAKER_01] Merci de nous recevoir...
```

---

## ⚙️ Installation

### 1. Installer pyannote.audio

```bash
pip install pyannote.audio
```

### 2. Créer un compte HuggingFace

1. Aller sur https://huggingface.co
2. Créer un compte gratuit
3. Aller sur https://huggingface.co/settings/tokens
4. Créer un nouveau token (Read access suffit)
5. Copier le token

### 3. Accepter les conditions du modèle

1. Aller sur https://huggingface.co/pyannote/speaker-diarization-3.1
2. Cliquer sur "Agree and access repository"
3. Accepter les conditions d'utilisation

### 4. Configurer le token

Dans votre fichier `.env` :

```bash
ANTHROPIC_API_KEY=votre_cle_api_ici
HUGGINGFACE_TOKEN=votre_token_hf_ici
```

---

## 🚀 Utilisation

### Activation de la détection

Ajoutez simplement le flag `--detect-speakers` :

```bash
podcasteur auto audio/ --duree 5 --detect-speakers
```

### Exemples d'usage

**Interview avec 2 personnes :**
```bash
podcasteur auto interview.wav --duree 10 --detect-speakers --ton "informatif"
```

**Table ronde :**
```bash
podcasteur auto table_ronde/ --duree 15 --detect-speakers
```

**Avec transcription existante (skip la diarisation) :**
```bash
podcasteur auto audio/ --transcription transcript_avec_speakers.txt --duree 5
```

---

## 📊 Sortie

### Format de transcription

Le fichier `transcription_timestamps.txt` contiendra :

```
[00:00 - 00:15] [SPEAKER_00] Bonjour à tous
[00:16 - 00:32] [SPEAKER_01] Merci d'être là
[00:33 - 01:05] [SPEAKER_00] Aujourd'hui nous allons parler de...
[01:06 - 01:28] [SPEAKER_02] C'est très intéressant
```

### Utilisation par Claude

Claude recevra la transcription avec les identifiants de speakers et pourra :
- Identifier les segments où un speaker spécifique parle
- Créer des montages centrés sur certains speakers
- Équilibrer les temps de parole

---

## ⏱️ Performance

**Temps de traitement estimé :**

| Durée audio | Whisper seul | Whisper + Diarisation |
|-------------|--------------|----------------------|
| 5 min       | ~30s         | ~1-2 min             |
| 15 min      | ~1-2 min     | ~4-6 min             |
| 30 min      | ~3-5 min     | ~10-15 min           |

La diarisation double environ le temps de traitement.

**Optimisation :**
Une fois la transcription avec speakers générée, vous pouvez la réutiliser :

```bash
# 1ère fois : avec détection (lent)
podcasteur auto audio/ --detect-speakers --duree 5

# Fois suivantes : réutiliser la transcription (rapide)
podcasteur auto audio/ --transcription sortie/podcast_XXX/transcription_timestamps.txt --duree 5
```

---

## 💡 Cas d'usage

### Quand utiliser la diarisation ?

✅ **Utile pour :**
- Interviews longues (>10 min) avec 2-3 personnes fixes
- Tables rondes ou débats
- Podcasts conversationnels réguliers
- Montages centrés sur un speaker spécifique

❌ **Moins utile pour :**
- Vox pop avec beaucoup de personnes différentes
- Enregistrements courts (<5 min)
- Narration solo
- Reportages avec intervention brève de plusieurs personnes

### Exemples de feedback à Claude

Avec la diarisation, vous pouvez donner des feedbacks plus précis :

```
"Garde seulement les segments où SPEAKER_00 parle"
"Équilibre entre SPEAKER_00 et SPEAKER_01"
"Focus sur l'interview de SPEAKER_02"
```

---

## 🔧 Dépannage

### Erreur "pyannote.audio not installed"

```bash
pip install pyannote.audio
```

### Erreur "401 Unauthorized"

Vérifiez que :
1. Votre token HuggingFace est correct dans `.env`
2. Vous avez accepté les conditions sur https://huggingface.co/pyannote/speaker-diarization-3.1

### Erreur "CUDA out of memory"

Pyannote utilise beaucoup de mémoire GPU. Solutions :
- Réduire la durée des fichiers audio
- Utiliser CPU uniquement (plus lent) en désactivant CUDA

### La détection ne fonctionne pas bien

La qualité de la diarisation dépend de :
- **Qualité audio** : Meilleure avec peu de bruit de fond
- **Séparation des voix** : Difficile si les speakers se coupent
- **Nombre de speakers** : Plus précis avec 2-3 speakers qu'avec 10+

---

## 📚 Ressources

- [Pyannote.audio documentation](https://github.com/pyannote/pyannote-audio)
- [HuggingFace tokens](https://huggingface.co/settings/tokens)
- [Modèle de diarisation](https://huggingface.co/pyannote/speaker-diarization-3.1)

---

## ⚖️ Considérations éthiques

La diarisation identifie les speakers mais **ne les nomme pas**. Les speakers sont étiquetés SPEAKER_00, SPEAKER_01, etc.

Pour des raisons de confidentialité :
- Ne partagez pas les transcriptions avec identification de speakers sans consentement
- Les identifiants de speakers sont basés sur les voix, pas sur l'identité réelle
- Respectez la vie privée des personnes enregistrées

---

**Bon podcasting avec détection de speakers ! 🎙️👥**