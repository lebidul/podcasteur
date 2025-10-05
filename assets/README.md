# 🎵 Éléments sonores pour Podcasteur

Ce dossier contient les fichiers audio statiques utilisés pour habiller vos podcasts.

## 📂 Structure

```
assets/
├── intro.mp3      # Générique de début
├── outro.mp3      # Générique de fin
└── README.md      # Ce fichier
```

## 🎼 Spécifications recommandées

### Intro (générique de début)
- **Durée** : 5-15 secondes
- **Format** : MP3, WAV, OGG
- **Contenu** : Jingle, musique de signature, annonce vocale
- **Conseil** : Terminer en fondu ou sur une note calme pour bien enchaîner avec le contenu

### Outro (générique de fin)
- **Durée** : 5-20 secondes
- **Format** : MP3, WAV, OGG
- **Contenu** : Musique de sortie, remerciements, appel à l'action
- **Conseil** : Commencer doucement pour un fondu d'entrée fluide

## ⚙️ Configuration

Les éléments sonores sont configurés dans `config/default_config.yaml` :

```yaml
elements_sonores:
  activer: true  # true pour activer, false pour désactiver
  generique_debut:
    fichier: "assets/intro.mp3"
    duree_fondu_sortie: 1000  # Fondu de sortie en ms
  generique_fin:
    fichier: "assets/outro.mp3"
    duree_fondu_entree: 1000  # Fondu d'entrée en ms
```

## 🎯 Utilisation

1. **Placez vos fichiers** dans ce dossier `assets/`
2. **Nommez-les** `intro.mp3` et `outro.mp3` (ou modifiez le chemin dans la config)
3. **Activez** dans la config : `elements_sonores.activer: true`
4. **Lancez** le workflow normalement :
   ```bash
   podcasteur auto audio/ --duree 5
   ```

L'intro et l'outro seront automatiquement ajoutés au montage final !

## 📊 Impact sur la durée

**Important** : Les éléments sonores s'ajoutent à la durée du contenu.

Exemple :
- Durée cible demandée à Claude : 5 minutes
- Intro : 10 secondes
- Outro : 15 secondes
- **Durée finale** : ~5 min 25 sec

## 🎨 Où trouver des éléments sonores ?

### Musiques libres de droits
- [Incompetech](https://incompetech.com/) - Kevin MacLeod
- [Free Music Archive](https://freemusicarchive.org/)
- [YouTube Audio Library](https://www.youtube.com/audiolibrary)
- [Bensound](https://www.bensound.com/)

### Sound design / Jingles
- [Freesound](https://freesound.org/)
- [Zapsplat](https://www.zapsplat.com/)
- [BBC Sound Effects](https://sound-effects.bbcrewind.co.uk/)

### ⚠️ Attention aux licences
Vérifiez toujours les conditions d'utilisation :
- Usage commercial autorisé ?
- Attribution requise ?
- Modifications permises ?

## 💡 Conseils de production

1. **Volume cohérent** : Normalisez vos intro/outro au même niveau que votre contenu
2. **Transition fluide** : Utilisez des fondus pour éviter les coupures brusques
3. **Identité sonore** : Gardez les mêmes éléments pour tous vos épisodes
4. **Durée raisonnable** : 5-15s pour l'intro, ne pas dépasser 20s pour l'outro

## 🔧 Personnalisation avancée

Pour utiliser des chemins personnalisés ou plusieurs versions :

```yaml
# Dans votre config personnalisée
elements_sonores:
  activer: true
  generique_debut:
    fichier: "mes_sons/intro_bidul_v2.mp3"
    duree_fondu_sortie: 2000
  generique_fin:
    fichier: "mes_sons/outro_bluezinc.wav"
    duree_fondu_entree: 1500
```

## 📝 Exemple pour Le Bidul

```
assets/
├── intro_bidul.mp3        # "Le Bidul présente..."
├── outro_bidul.mp3        # "Retrouvez-nous sur lebidul.org"
├── intro_bluezinc.mp3     # Variante Blue Zinc
└── outro_bluezinc.mp3
```

Puis créez différentes configs pour chaque émission :
- `config/bidul_config.yaml`
- `config/bluezinc_config.yaml`