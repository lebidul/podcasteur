# 🎵 Guide : Ajouter intro et outro à vos podcasts

## Installation rapide

### 1. Créer le dossier assets

```bash
mkdir assets
```

### 2. Ajouter vos fichiers audio

Placez vos fichiers dans `assets/` :
- `assets/intro.mp3` → Générique de début
- `assets/outro.mp3` → Générique de fin

### 3. Activer dans la configuration

**Option A - Modifier la config par défaut** :
```bash
# Ouvrir config/default_config.yaml
# Changer cette ligne :
elements_sonores:
  activer: true  # Passer de false à true
```

**Option B - Créer une config personnalisée** :
```bash
podcasteur init-config --sortie ma_config.yaml

# Éditer ma_config.yaml
# Activer : elements_sonores.activer: true

# Utiliser avec :
podcasteur auto audio/ --duree 5 --config ma_config.yaml
```

## Utilisation

Une fois activé, utilisez normalement :

```bash
podcasteur auto audio/ --duree 5
```

Le podcast final aura automatiquement :
```
[Intro 10s] → [Contenu 5min] → [Outro 15s] = Total ~5min25s
```

## Personnalisation avancée

### Chemins personnalisés

```yaml
elements_sonores:
  activer: true
  generique_debut:
    fichier: "mes_sons/intro_custom.mp3"
    duree_fondu_sortie: 2000  # 2 secondes de fondu
  generique_fin:
    fichier: "mes_sons/outro_custom.wav"
    duree_fondu_entree: 1500  # 1.5 secondes de fondu
```

### Désactiver temporairement

**Sans modifier la config** :
```yaml
elements_sonores:
  activer: false  # Désactive tout
```

**Ou supprimer un élément** :
```yaml
elements_sonores:
  activer: true
  generique_debut:
    fichier: "assets/intro.mp3"
    duree_fondu_sortie: 1000
  # Pas de generique_fin → pas d'outro
```

## Différentes configs pour différents podcasts

Créez plusieurs configurations :

**config/bidul_config.yaml** :
```yaml
elements_sonores:
  activer: true
  generique_debut:
    fichier: "assets/intro_bidul.mp3"
    duree_fondu_sortie: 1000
  generique_fin:
    fichier: "assets/outro_bidul.mp3"
    duree_fondu_entree: 1000
```

**config/bluezinc_config.yaml** :
```yaml
elements_sonores:
  activer: true
  generique_debut:
    fichier: "assets/intro_bluezinc.mp3"
    duree_fondu_sortie: 1500
  generique_fin:
    fichier: "assets/outro_bluezinc.mp3"
    duree_fondu_entree: 1500
```

Puis utiliser :
```bash
podcasteur auto audio/ --config config/bidul_config.yaml --duree 5
podcasteur auto audio/ --config config/bluezinc_config.yaml --duree 3
```

## Formats supportés

- MP3
- WAV
- OGG
- FLAC
- M4A
- Tous les formats audio supportés par FFmpeg

## Conseils de production

### 1. Durée idéale
- **Intro** : 5-15 secondes maximum
- **Outro** : 10-20 secondes maximum
- Plus long = risque de lasser l'auditeur

### 2. Volume
Normalisez vos intro/outro pour qu'ils aient le même niveau sonore que votre contenu principal.

### 3. Fondus
Les fondus assurent des transitions douces :
- Fondu de sortie de l'intro → enchaîne avec le contenu
- Fondu d'entrée de l'outro → transition depuis le contenu

### 4. Cohérence
Utilisez les mêmes éléments sonores pour tous vos épisodes → crée une identité auditive.

## Exemples d'intro/outro

### Podcast informatif
```
Intro : Jingle instrumental 8s + "Le Bidul présente..." (voix)
Outro : "Retrouvez-nous sur lebidul.org" + musique 12s
```

### Podcast musical
```
Intro : Extrait signature musicale 10s
Outro : Fade out de la dernière musique + remerciements 15s
```

### Podcast interview
```
Intro : Ambiance sonore + annonce de l'invité 12s
Outro : Appel à l'action + générique 18s
```

## Dépannage

### "Fichier non trouvé"
Vérifiez le chemin dans la config :
```yaml
fichier: "assets/intro.mp3"  # Relatif à la racine du projet
```

### "Transition brusque"
Augmentez la durée des fondus :
```yaml
duree_fondu_sortie: 2000  # 2 secondes au lieu de 1
```

### "Volume trop fort/faible"
Normalisez vos fichiers audio avec Audacity ou un outil similaire avant de les ajouter.

## Workflow complet avec éléments sonores

```bash
# 1. Préparer les assets
mkdir -p assets
# Copier intro.mp3 et outro.mp3 dans assets/

# 2. Activer dans la config
vim config/default_config.yaml
# elements_sonores.activer: true

# 3. Lancer le workflow
podcasteur auto audio/ --duree 5 --detect-speakers

# 4. Résultat
# sortie/podcast_YYYYMMDD_HHMMSS/
#   ├── podcast_YYYYMMDD_HHMMSS.mp3  ← Avec intro + contenu + outro
#   ├── podcast_YYYYMMDD_HHMMSS.json
#   └── podcast_YYYYMMDD_HHMMSS.txt
```

Voilà ! Vos podcasts ont maintenant un habillage sonore professionnel ! 🎧