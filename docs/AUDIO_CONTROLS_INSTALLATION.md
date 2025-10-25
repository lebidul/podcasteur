# 📦 Guide d'installation - Contrôles Audio Avancés

## 🚀 Installation rapide (recommandée)

### Option 1 : Remplacement direct

```bash
# Depuis le dossier racine de podcasteur/
cp segment_editor_dialog.py src/gui/segment_editor_dialog.py

# Tester
python -m src.gui.main  # ou votre commande habituelle
```

✅ **Aucune dépendance supplémentaire nécessaire !**

---

## 🔍 Vérification avant installation

### Vérifier la version actuelle

```bash
# Afficher les premières lignes
head -20 src/gui/segment_editor_dialog.py
```

Cherchez la version :
- **Sans mention "Version améliorée"** → Ancienne version
- **Avec "Version améliorée avec contrôles audio avancés"** → Nouvelle version déjà installée

### Sauvegarder l'ancienne version (recommandé)

```bash
# Créer une sauvegarde horodatée
cp src/gui/segment_editor_dialog.py \
   src/gui/segment_editor_dialog.py.backup-$(date +%Y%m%d-%H%M%S)
```

---

## 📝 Installation manuelle (si problème)

### Étape 1 : Copier le nouveau fichier

```bash
# Méthode 1 : Copie simple
cp segment_editor_dialog.py src/gui/segment_editor_dialog.py

# Méthode 2 : Avec confirmation
cp -i segment_editor_dialog.py src/gui/segment_editor_dialog.py
```

### Étape 2 : Vérifier les imports

Le nouveau fichier utilise ces imports PyQt6 :

```python
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
    QTimeEdit, QLineEdit, QSpinBox, QWidget,
    QDialogButtonBox, QFileDialog, QFormLayout, QStatusBar,
    QSlider, QGroupBox  # ← NOUVEAUX
)
from PyQt6.QtCore import Qt, QTime, QUrl, QTimer  # ← QTimer NOUVEAU
```

✅ Si PyQt6 est installé, pas besoin d'installer quoi que ce soit d'autre.

### Étape 3 : Tester l'interface

```bash
# Lancer l'application GUI
python src/gui/main.py

# Ou selon votre configuration
python -m src.gui.main
podcasteur-gui
```

---

## 🧪 Tests de validation

### Test 1 : Ouverture du dialogue

```python
# Dans l'application, après avoir lancé un workflow automatique :
1. Sélectionner une suggestion
2. Cliquer sur "Modifier les segments"
3. ✅ La nouvelle section "🎵 Contrôles de lecture" doit apparaître
```

### Test 2 : Contrôles de base

```
1. Cliquer sur ▶️ dans le tableau (première ligne)
2. ✅ Les boutons doivent s'activer : [⏸️ Pause] [⏹️ Stop] [⏪] [⏩]
3. ✅ Le slider doit bouger automatiquement
4. ✅ Le temps doit s'afficher : "00:03" / "01:23"
```

### Test 3 : Navigation

```
1. Pendant la lecture, cliquer sur [⏸️ Pause]
2. Cliquer sur [⏩ +5s]
3. ✅ Le temps doit augmenter de 5 secondes
4. Cliquer sur [▶️ Play]
5. ✅ La lecture doit reprendre à la nouvelle position
```

### Test 4 : Slider

```
1. Pendant la lecture, drag le slider vers 50%
2. Relâcher
3. ✅ La lecture doit continuer à 50% du segment
```

### Test 5 : Volume

```
1. Bouger le slider de volume
2. ✅ Le label doit afficher le pourcentage
3. ✅ Le volume audio doit changer
```

---

## ⚠️ Résolution de problèmes

### Problème : ImportError sur QTimer

```
ImportError: cannot import name 'QTimer' from 'PyQt6.QtCore'
```

**Solution** : Vérifier la version de PyQt6

```bash
pip show PyQt6
# Version minimum : 6.0.0

# Si version trop ancienne :
pip install --upgrade PyQt6
```

### Problème : Les contrôles n'apparaissent pas

**Cause possible** : Cache Python ou fichier mal copié

```bash
# Supprimer les fichiers .pyc
find src/gui -name "*.pyc" -delete
find src/gui -name "__pycache__" -type d -exec rm -rf {} +

# Relancer
python src/gui/main.py
```

### Problème : "Fichier audio introuvable"

**Cause** : Le chemin du fichier source est incorrect

**Solutions** :
1. Vérifier que le workflow automatique a bien créé `mix_complet.wav` dans `output/`
2. Vérifier la colonne "Fichier source" dans le tableau
3. Cliquer sur 📁 pour sélectionner manuellement le bon fichier

### Problème : Le player ne démarre pas

**Vérifications** :

```python
# Dans segment_editor_dialog.py, ligne ~267
if not self.audio_player:
    self.audio_player = QMediaPlayer()
    self.audio_output = QAudioOutput()
    self.audio_player.setAudioOutput(self.audio_output)
```

✅ Vérifier que PyQt6.QtMultimedia est installé :

```bash
python -c "from PyQt6.QtMultimedia import QMediaPlayer; print('OK')"
```

Si erreur :
```bash
pip install PyQt6-QtMultimedia
```

---

## 🔄 Rollback (retour en arrière)

### Si vous avez fait une sauvegarde

```bash
# Restaurer depuis la sauvegarde
cp src/gui/segment_editor_dialog.py.backup-YYYYMMDD-HHMMSS \
   src/gui/segment_editor_dialog.py
```

### Si pas de sauvegarde

Récupérer depuis Git (si versionné) :

```bash
git checkout src/gui/segment_editor_dialog.py
```

---

## 📊 Comparaison des versions

### Ancienne version

```python
Lignes de code : ~629
Contrôles audio : ❌ Basique (play/stop uniquement)
Navigation temporelle : ❌ Non
Slider de position : ❌ Non
Contrôle de volume : ❌ Non
Timer de mise à jour : ❌ Non
```

### Nouvelle version

```python
Lignes de code : ~1050 (+421 lignes)
Contrôles audio : ✅ Complets (play/pause/stop/skip)
Navigation temporelle : ✅ Oui (±5s)
Slider de position : ✅ Oui (avec drag)
Contrôle de volume : ✅ Oui (0-100%)
Timer de mise à jour : ✅ Oui (100ms)
```

**Augmentation** : +67% de fonctionnalités, +0% de dépendances ! 🎉

---

## 🎓 Comprendre les changements

### Nouveaux attributs (lignes 34-38)

```python
self.segment_duration = 0
self.position_update_timer = QTimer()
self.is_slider_pressed = False
```

**Rôle** : Gérer la mise à jour en temps réel de la position

### Nouvelle méthode principale (ligne ~70)

```python
def _create_audio_controls(self, parent_layout):
    """Crée la barre de contrôles audio avancés"""
```

**Rôle** : Créer tous les widgets de contrôle (boutons, sliders, labels)

### Nouvelles méthodes de contrôle (lignes ~150-250)

```python
_toggle_play_pause()     # Play/Pause
_skip_backward()         # -5s
_skip_forward()          # +5s
_change_volume()         # Volume
_update_position()       # Mise à jour temps réel
_on_slider_pressed()     # Début drag
_on_slider_released()    # Fin drag
_on_slider_moved()       # Pendant drag
_enable_audio_controls() # Activer/désactiver
_on_duration_changed()   # Durée connue
_format_time_ms()        # Formatage temps
```

### Modifications dans les méthodes existantes

**`_play_segment()` (ligne ~278)** :
- ✅ Active les contrôles
- ✅ Démarre le timer
- ✅ Affiche l'info du segment

**`_stop_playback()` (ligne ~350)** :
- ✅ Arrête le timer
- ✅ Réinitialise l'affichage
- ✅ Désactive les contrôles

**`closeEvent()` (ligne ~380)** :
- ✅ Arrête le timer avant fermeture

---

## 📚 Ressources complémentaires

### Documentation créée

- **segment_editor_dialog.py** : Le fichier source
- **AUDIO_CONTROLS_README.md** : Documentation technique complète
- **GUIDE_RAPIDE_AUDIO.md** : Guide utilisateur visuel
- **INSTALLATION.md** : Ce fichier

### Documentation Qt

- [QMediaPlayer](https://doc.qt.io/qt-6/qmediaplayer.html)
- [QSlider](https://doc.qt.io/qt-6/qslider.html)
- [QTimer](https://doc.qt.io/qt-6/qtimer.html)

---

## ✅ Checklist d'installation

- [ ] Sauvegarde de l'ancien fichier créée
- [ ] Nouveau fichier copié dans `src/gui/`
- [ ] PyQt6 à jour (version ≥ 6.0.0)
- [ ] Test 1 : Dialogue s'ouvre
- [ ] Test 2 : Contrôles visibles
- [ ] Test 3 : Play/Pause fonctionne
- [ ] Test 4 : Skip ±5s fonctionne
- [ ] Test 5 : Slider fonctionne
- [ ] Test 6 : Volume fonctionne
- [ ] Aucune erreur dans la console

---

## 🎯 Prochaines étapes recommandées

### Immédiat
1. Tester avec des segments réels
2. Vérifier les performances sur de longs segments (>5min)
3. Recueillir le feedback utilisateur

### Court terme
- [ ] Ajouter des raccourcis clavier (Espace, Flèches)
- [ ] Permettre de configurer l'intervalle de skip (±5s, ±10s, etc.)
- [ ] Ajouter un bouton "Rejouer le segment depuis le début"

### Moyen terme
- [ ] Visualisation de forme d'onde
- [ ] Marqueurs personnalisables
- [ ] Export d'un segment seul

---

## 🆘 Support

### En cas de problème

1. **Vérifier les logs** : Regarder la sortie console
2. **Tester avec un fichier simple** : Utiliser un petit fichier audio (30s)
3. **Isoler le problème** : Tester chaque contrôle individuellement

### Besoin d'aide ?

- 📧 Ouvrir une issue sur GitHub
- 💬 Partager les logs d'erreur
- 📸 Capturer des screenshots si nécessaire

---

**Installation réussie ? Profite des nouveaux contrôles audio ! 🎵🎉**