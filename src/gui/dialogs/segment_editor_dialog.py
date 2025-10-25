"""
Éditeur interactif de segments avant montage final
Version améliorée avec contrôles audio avancés
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
    QTimeEdit, QLineEdit, QSpinBox, QWidget,
    QDialogButtonBox, QFileDialog, QFormLayout, QStatusBar,
    QSlider, QGroupBox
)

from src.gui.widgets import (
    PrimaryButton, SecondaryButton, DangerButton,
    SuccessButton, NeutralButton, StyledCheckBox,
    StyledComboBox, StyledSlider, StyledSpinBox,
    StyledDoubleSpinBox, StyledComboBox
)

from PyQt6.QtCore import Qt, QTime, QUrl, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from pydub import AudioSegment
from pathlib import Path
import tempfile
import os


class SegmentEditorDialog(QDialog):
    """Éditeur de segments avec ajout/suppression/modification"""

    def __init__(self, suggestion, parent=None, fichier_mix=None):
        super().__init__(parent)
        self.suggestion = suggestion
        self.segments = [seg.copy() for seg in suggestion['segments']]  # Copie pour modification
        self.fichier_mix = fichier_mix

        # Audio playback
        self.audio_player = None
        self.audio_output = None
        self.current_playing_row = -1
        self.temp_audio_files = []  # Pour nettoyer les fichiers temporaires

        # Nouveaux attributs pour les contrôles audio
        self.segment_duration = 0  # Durée du segment en cours (ms)
        self.position_update_timer = QTimer()
        self.position_update_timer.timeout.connect(self._update_position)
        self.is_slider_pressed = False  # Pour éviter les conflits lors du drag

        self.init_ui()

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle(f"✂️ Éditeur de segments - {self.suggestion['titre']}")
        self.setMinimumSize(900, 700)  # Augmenté pour les contrôles audio

        layout = QVBoxLayout(self)

        # En-tête
        header = QLabel(f"Modifiez les segments avant le montage final")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Info
        info_layout = QHBoxLayout()
        self.duree_label = QLabel()
        self._update_duree_totale()
        info_layout.addWidget(self.duree_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Tableau des segments
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "▶️", "Début (MM:SS)", "Fin (MM:SS)", "Durée", "Fichier source", "Description", "Actions"
        ])

        # Configuration du tableau
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Bouton play
        self.table.setColumnWidth(0, 45)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        layout.addWidget(self.table)

        # ========== NOUVEAUX CONTRÔLES AUDIO ==========
        self._create_audio_controls(layout)
        # =============================================

        # Boutons d'action sur les segments
        segment_buttons = QHBoxLayout()

        btn_add = SecondaryButton("➕ Ajouter segment")
        btn_add.clicked.connect(self._add_segment)

        btn_edit = SecondaryButton("✏️ Modifier segment")
        btn_edit.clicked.connect(self._edit_segment)

        btn_delete = DangerButton("🗑️ Supprimer segment")
        btn_delete.clicked.connect(self._delete_segment)

        btn_up = SecondaryButton("⬆️ Monter")
        btn_up.clicked.connect(self._move_up)

        btn_down = SecondaryButton("⬇️ Descendre")
        btn_down.clicked.connect(self._move_down)

        segment_buttons.addWidget(btn_add)
        segment_buttons.addWidget(btn_edit)
        segment_buttons.addWidget(btn_delete)
        segment_buttons.addWidget(btn_up)
        segment_buttons.addWidget(btn_down)
        segment_buttons.addStretch()

        layout.addLayout(segment_buttons)

        # Status bar pour les messages de lecture
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        # Boutons de validation
        buttons_layout = QHBoxLayout()

        btn_reset = SecondaryButton("🔄 Réinitialiser")
        btn_reset.clicked.connect(self._reset_segments)

        btn_cancel = DangerButton("Annuler")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = SuccessButton("✅ Créer le podcast")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._validate_and_accept)
        btn_ok.setStyleSheet("padding: 8px; font-weight: bold; background-color: #4CAF50; color: white;")

        buttons_layout.addWidget(btn_reset)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_ok)

        layout.addLayout(buttons_layout)

        # Remplir le tableau
        self._populate_table()

    def _create_audio_controls(self, parent_layout):
        """Crée la barre de contrôles audio avancés"""
        audio_group = QGroupBox("🎵 Contrôles de lecture")
        audio_layout = QVBoxLayout()

        # Ligne 1 : Boutons de contrôle
        controls_layout = QHBoxLayout()

        # Bouton Play/Pause principal
        self.btn_play_pause = PrimaryButton("▶️ Play")
        self.btn_play_pause.setMinimumWidth(100)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        self.btn_play_pause.setEnabled(False)
        controls_layout.addWidget(self.btn_play_pause)

        # Bouton Stop
        self.btn_stop = SecondaryButton("⏹️ Stop")
        self.btn_stop.clicked.connect(self._stop_playback)
        self.btn_stop.setEnabled(False)
        controls_layout.addWidget(self.btn_stop)

        controls_layout.addSpacing(20)

        # Bouton Reculer -5s
        self.btn_backward = NeutralButton("⏪ -5s")
        self.btn_backward.clicked.connect(self._skip_backward)
        self.btn_backward.setEnabled(False)
        controls_layout.addWidget(self.btn_backward)

        # Bouton Avancer +5s
        self.btn_forward = NeutralButton("⏩ +5s")
        self.btn_forward.clicked.connect(self._skip_forward)
        self.btn_forward.setEnabled(False)
        controls_layout.addWidget(self.btn_forward)

        controls_layout.addSpacing(20)

        # Contrôle de volume
        volume_label = QLabel("🔊 Volume:")
        controls_layout.addWidget(volume_label)

        self.volume_slider = StyledSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self._change_volume)
        controls_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(40)
        controls_layout.addWidget(self.volume_label)

        controls_layout.addStretch()

        audio_layout.addLayout(controls_layout)

        # Ligne 2 : Slider de position + temps
        position_layout = QHBoxLayout()

        # Temps écoulé
        self.time_label = QLabel("00:00")
        self.time_label.setMinimumWidth(50)
        position_layout.addWidget(self.time_label)

        # Slider de position
        self.position_slider = StyledSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)  # On utilisera des millièmes
        self.position_slider.setValue(0)
        self.position_slider.sliderPressed.connect(self._on_slider_pressed)
        self.position_slider.sliderReleased.connect(self._on_slider_released)
        self.position_slider.sliderMoved.connect(self._on_slider_moved)
        position_layout.addWidget(self.position_slider)

        # Temps total
        self.duration_label = QLabel("00:00")
        self.duration_label.setMinimumWidth(50)
        position_layout.addWidget(self.duration_label)

        audio_layout.addLayout(position_layout)

        # Info segment en cours
        self.current_segment_label = QLabel("Aucun segment en lecture")
        self.current_segment_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        audio_layout.addWidget(self.current_segment_label)

        audio_group.setLayout(audio_layout)
        parent_layout.addWidget(audio_group)

    def _toggle_play_pause(self):
        """Gère le bouton Play/Pause principal"""
        if not self.audio_player:
            return

        if self.audio_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.audio_player.pause()
            self.btn_play_pause.setText("▶️ Play")
            self.position_update_timer.stop()
        else:
            self.audio_player.play()
            self.btn_play_pause.setText("⏸️ Pause")
            self.position_update_timer.start(100)  # Mise à jour toutes les 100ms

    def _skip_backward(self):
        """Recule de 5 secondes"""
        if self.audio_player:
            current_pos = self.audio_player.position()
            new_pos = max(0, current_pos - 5000)  # -5000ms
            self.audio_player.setPosition(new_pos)

    def _skip_forward(self):
        """Avance de 5 secondes"""
        if self.audio_player:
            current_pos = self.audio_player.position()
            duration = self.audio_player.duration()
            new_pos = min(duration, current_pos + 5000)  # +5000ms
            self.audio_player.setPosition(new_pos)

    def _change_volume(self, value):
        """Change le volume"""
        if self.audio_output:
            self.audio_output.setVolume(value / 100.0)
        self.volume_label.setText(f"{value}%")

    def _update_position(self):
        """Met à jour l'affichage de la position"""
        if not self.audio_player or self.is_slider_pressed:
            return

        position = self.audio_player.position()
        duration = self.audio_player.duration()

        if duration > 0:
            # Mettre à jour le slider
            slider_position = int((position / duration) * 1000)
            self.position_slider.setValue(slider_position)

            # Mettre à jour les labels de temps
            self.time_label.setText(self._format_time_ms(position))
            self.duration_label.setText(self._format_time_ms(duration))

    def _on_slider_pressed(self):
        """Appelé quand l'utilisateur commence à drag le slider"""
        self.is_slider_pressed = True

    def _on_slider_released(self):
        """Appelé quand l'utilisateur relâche le slider"""
        self.is_slider_pressed = False
        if self.audio_player:
            duration = self.audio_player.duration()
            if duration > 0:
                new_position = int((self.position_slider.value() / 1000) * duration)
                self.audio_player.setPosition(new_position)

    def _on_slider_moved(self, value):
        """Appelé pendant le drag du slider"""
        if self.audio_player:
            duration = self.audio_player.duration()
            if duration > 0:
                position = int((value / 1000) * duration)
                self.time_label.setText(self._format_time_ms(position))

    @staticmethod
    def _format_time_ms(milliseconds):
        """Formate les millisecondes en MM:SS"""
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _populate_table(self):
        """Remplit le tableau avec les segments"""
        self.table.setRowCount(len(self.segments))

        for i, seg in enumerate(self.segments):
            # Colonne 0 : Bouton play
            play_btn = QPushButton("▶️")
            play_btn.setMaximumWidth(35)
            play_btn.setMaximumHeight(25)
            play_btn.setProperty('row', i)
            play_btn.clicked.connect(self._play_segment)
            play_btn.setToolTip("Écouter ce segment")
            self.table.setCellWidget(i, 0, play_btn)

            # Début (colonne 1)
            debut_item = QTableWidgetItem(self._formater_temps(seg['debut']))
            debut_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            debut_item.setFlags(debut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, debut_item)

            # Fin (colonne 2)
            fin_item = QTableWidgetItem(self._formater_temps(seg['fin']))
            fin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            fin_item.setFlags(fin_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, fin_item)

            # Durée (colonne 3)
            duree = seg['fin'] - seg['debut']
            duree_item = QTableWidgetItem(self._formater_temps(duree))
            duree_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            duree_item.setFlags(duree_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, duree_item)

            # Fichier source (colonne 4) - Widget personnalisé
            fichier_widget = QWidget()
            fichier_layout = QHBoxLayout(fichier_widget)
            fichier_layout.setContentsMargins(2, 0, 2, 0)

            fichier_edit = QLineEdit(seg.get('fichier', 'mix_complet.wav'))
            fichier_edit.setProperty('row', i)

            fichier_btn = NeutralButton("📁")
            fichier_btn.setMaximumWidth(35)
            fichier_btn.setMaximumHeight(25)
            fichier_btn.setProperty('row', i)
            fichier_btn.clicked.connect(self._browse_fichier_source)

            fichier_layout.addWidget(fichier_edit)
            fichier_layout.addWidget(fichier_btn)

            self.table.setCellWidget(i, 4, fichier_widget)

            # Description (colonne 5)
            desc_item = QTableWidgetItem(seg.get('description', ''))
            self.table.setItem(i, 5, desc_item)

            # Actions (colonne 6)
            actions_item = QTableWidgetItem("🔧")
            actions_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            actions_item.setFlags(actions_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, actions_item)

        self._update_duree_totale()

    def _play_segment(self):
        """Joue le segment audio correspondant"""
        button = self.sender()
        row = button.property('row')

        if row < 0 or row >= len(self.segments):
            return

        segment = self.segments[row]

        # Obtenir le fichier source depuis le widget
        fichier_widget = self.table.cellWidget(row, 4)
        fichier_source = 'mix_complet.wav'

        if fichier_widget:
            fichier_edit = fichier_widget.findChild(QLineEdit)
            if fichier_edit:
                fichier_source = fichier_edit.text()

        # Vérifier que le fichier existe
        fichier_path = Path(fichier_source)
        if not fichier_path.exists():
            # Essayer dans le dossier output
            fichier_path = Path('output') / fichier_source
            if not fichier_path.exists():
                QMessageBox.warning(
                    self,
                    "Fichier introuvable",
                    f"Le fichier audio '{fichier_source}' n'existe pas.\n\n"
                    "Assurez-vous que le fichier source est accessible."
                )
                return

        try:
            # Si déjà en train de jouer ce segment, pause/play
            if self.current_playing_row == row and self.audio_player and self.audio_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self._toggle_play_pause()
                return

            # Arrêter toute lecture en cours
            self._stop_playback()

            # Changer le bouton en "en cours de lecture"
            button.setText("⏸️")
            self.current_playing_row = row

            # Extraire le segment avec pydub
            self.status_bar.showMessage(f"📀 Extraction du segment {row + 1}...", 2000)

            audio = AudioSegment.from_file(str(fichier_path))
            debut_ms = int(segment['debut'] * 1000)
            fin_ms = int(segment['fin'] * 1000)
            segment_audio = audio[debut_ms:fin_ms]

            # Créer un fichier temporaire
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()

            # Exporter le segment
            segment_audio.export(temp_path, format='wav')
            self.temp_audio_files.append(temp_path)

            # Créer le player si nécessaire
            if not self.audio_player:
                self.audio_player = QMediaPlayer()
                self.audio_output = QAudioOutput()
                self.audio_player.setAudioOutput(self.audio_output)

                # Connecter les signaux
                self.audio_player.playbackStateChanged.connect(self._on_playback_state_changed)
                self.audio_player.errorOccurred.connect(self._on_player_error)
                self.audio_player.durationChanged.connect(self._on_duration_changed)

            # Définir le volume initial
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)

            # Charger et jouer
            self.audio_player.setSource(QUrl.fromLocalFile(temp_path))
            self.audio_player.play()

            # Activer les contrôles
            self._enable_audio_controls(True)

            # Démarrer le timer de mise à jour
            self.position_update_timer.start(100)

            # Mettre à jour le label du segment en cours
            self.current_segment_label.setText(
                f"🎵 Segment {row + 1}: {segment.get('description', 'Sans titre')} "
                f"({self._formater_temps(segment['debut'])} → {self._formater_temps(segment['fin'])})"
            )

            self.status_bar.showMessage(f"▶️ Lecture du segment {row + 1}...", 3000)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur de lecture",
                f"Impossible de lire le segment :\n{str(e)}"
            )
            self._reset_play_button(row)

    def _enable_audio_controls(self, enable):
        """Active/désactive les contrôles audio"""
        self.btn_play_pause.setEnabled(enable)
        self.btn_stop.setEnabled(enable)
        self.btn_backward.setEnabled(enable)
        self.btn_forward.setEnabled(enable)

        if enable:
            self.btn_play_pause.setText("⏸️ Pause")
        else:
            self.btn_play_pause.setText("▶️ Play")

    def _on_duration_changed(self, duration):
        """Appelé quand la durée du média est connue"""
        self.segment_duration = duration
        self.duration_label.setText(self._format_time_ms(duration))

    def _stop_playback(self):
        """Arrête la lecture en cours"""
        if self.audio_player:
            self.audio_player.stop()
            self.position_update_timer.stop()

        if self.current_playing_row >= 0:
            self._reset_play_button(self.current_playing_row)
            self.current_playing_row = -1

        # Réinitialiser l'affichage
        self.position_slider.setValue(0)
        self.time_label.setText("00:00")
        self.duration_label.setText("00:00")
        self.current_segment_label.setText("Aucun segment en lecture")

        # Désactiver les contrôles
        self._enable_audio_controls(False)

    def _reset_play_button(self, row):
        """Remet le bouton play à son état initial"""
        if row >= 0 and row < self.table.rowCount():
            play_btn = self.table.cellWidget(row, 0)
            if play_btn:
                play_btn.setText("▶️")

    def _on_playback_state_changed(self, state):
        """Gère les changements d'état de lecture"""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            # Lecture terminée, réinitialiser le bouton
            if self.current_playing_row >= 0:
                self._reset_play_button(self.current_playing_row)
                self.current_playing_row = -1
                self.status_bar.showMessage("⏹️ Lecture terminée", 2000)

            self.position_update_timer.stop()
            self._enable_audio_controls(False)
            self.current_segment_label.setText("Aucun segment en lecture")

        elif state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play_pause.setText("⏸️ Pause")

        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.btn_play_pause.setText("▶️ Play")

    def _on_player_error(self, error, error_string):
        """Gère les erreurs du player"""
        QMessageBox.warning(
            self,
            "Erreur de lecture",
            f"Erreur lors de la lecture audio :\n{error_string}"
        )
        if self.current_playing_row >= 0:
            self._reset_play_button(self.current_playing_row)
            self.current_playing_row = -1

    def closeEvent(self, event):
        """Nettoie les ressources avant fermeture"""
        # Arrêter la lecture
        self._stop_playback()

        # Arrêter le timer
        self.position_update_timer.stop()

        # Supprimer les fichiers temporaires
        for temp_file in self.temp_audio_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass

        event.accept()

    def _browse_fichier_source(self):
        """Parcourir un fichier source pour un segment"""
        button = self.sender()
        row = button.property('row')

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier source",
            "",
            "Fichiers audio (*.wav *.mp3 *.flac *.m4a)"
        )

        if file:
            # Mettre à jour le QLineEdit dans le widget
            fichier_widget = self.table.cellWidget(row, 4)
            fichier_edit = fichier_widget.findChild(QLineEdit)
            if fichier_edit:
                fichier_edit.setText(file)

    def _add_segment(self):
        """Ajoute un nouveau segment"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un segment")
        layout = QFormLayout(dialog)

        # Champs de saisie
        debut_edit = QTimeEdit()
        debut_edit.setDisplayFormat("mm:ss")
        debut_edit.setTime(QTime(0, 0))

        fin_edit = QTimeEdit()
        fin_edit.setDisplayFormat("mm:ss")
        fin_edit.setTime(QTime(0, 30))

        # Fichier source avec bouton parcourir
        fichier_layout = QHBoxLayout()

        # Fichier source avec bouton parcourir
        fichier_defaut = "mix_complet.wav"
        if self.segments and len(self.segments) > 0:
            # Prendre le fichier du premier segment (qui a le chemin complet)
            fichier_defaut = self.segments[0].get('fichier', 'mix_complet.wav')

        fichier_edit = QLineEdit(fichier_defaut)
        fichier_btn = NeutralButton("📁")

        def browse_file():
            file, _ = QFileDialog.getOpenFileName(
                dialog, "Sélectionner fichier source", "",
                "Fichiers audio (*.wav *.mp3 *.flac *.m4a)"
            )
            if file:
                fichier_edit.setText(file)

        fichier_btn.clicked.connect(browse_file)
        fichier_layout.addWidget(fichier_edit)
        fichier_layout.addWidget(fichier_btn)

        desc_edit = QLineEdit("Nouveau segment")

        layout.addRow("Début (MM:SS):", debut_edit)
        layout.addRow("Fin (MM:SS):", fin_edit)
        layout.addRow("Fichier source:", fichier_layout)
        layout.addRow("Description:", desc_edit)

        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec():
            debut_sec = debut_edit.time().minute() * 60 + debut_edit.time().second()
            fin_sec = fin_edit.time().minute() * 60 + fin_edit.time().second()

            if debut_sec >= fin_sec:
                QMessageBox.warning(self, "Erreur", "Le début doit être avant la fin")
                return

            nouveau_segment = {
                'debut': float(debut_sec),
                'fin': float(fin_sec),
                'fichier': fichier_edit.text(),
                'description': desc_edit.text()
            }

            self.segments.append(nouveau_segment)
            self._populate_table()

    def _edit_segment(self):
        """Modifie le segment sélectionné"""
        current_row = self.table.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "Aucune sélection", "Sélectionnez un segment à modifier")
            return

        segment = self.segments[current_row]

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier le segment")
        layout = QFormLayout(dialog)

        # Pré-remplir avec les valeurs actuelles
        debut_edit = QTimeEdit()
        debut_edit.setDisplayFormat("mm:ss")
        debut_min = int(segment['debut'] // 60)
        debut_sec = int(segment['debut'] % 60)
        debut_edit.setTime(QTime(0, debut_min, debut_sec))

        fin_edit = QTimeEdit()
        fin_edit.setDisplayFormat("mm:ss")
        fin_min = int(segment['fin'] // 60)
        fin_sec = int(segment['fin'] % 60)
        fin_edit.setTime(QTime(0, fin_min, fin_sec))

        # Fichier source avec bouton parcourir
        fichier_layout = QHBoxLayout()
        fichier_edit = QLineEdit(segment.get('fichier', 'mix_complet.wav'))
        fichier_btn = NeutralButton("📁")

        def browse_file():
            file, _ = QFileDialog.getOpenFileName(
                dialog, "Sélectionner fichier source", "",
                "Fichiers audio (*.wav *.mp3 *.flac *.m4a)"
            )
            if file:
                fichier_edit.setText(file)

        fichier_btn.clicked.connect(browse_file)
        fichier_layout.addWidget(fichier_edit)
        fichier_layout.addWidget(fichier_btn)

        desc_edit = QLineEdit(segment['description'])

        layout.addRow("Début (MM:SS):", debut_edit)
        layout.addRow("Fin (MM:SS):", fin_edit)
        layout.addRow("Fichier source:", fichier_layout)
        layout.addRow("Description:", desc_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec():
            debut_sec = debut_edit.time().minute() * 60 + debut_edit.time().second()
            fin_sec = fin_edit.time().minute() * 60 + fin_edit.time().second()

            if debut_sec >= fin_sec:
                QMessageBox.warning(self, "Erreur", "Le début doit être avant la fin")
                return

            # Si un segment est en cours de lecture, l'arrêter
            if self.current_playing_row == current_row:
                self._stop_playback()

            self.segments[current_row] = {
                'debut': float(debut_sec),
                'fin': float(fin_sec),
                'fichier': fichier_edit.text(),
                'description': desc_edit.text()
            }

            self._populate_table()

    def _delete_segment(self):
        """Supprime le segment sélectionné"""
        current_row = self.table.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "Aucune sélection", "Sélectionnez un segment à supprimer")
            return

        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Supprimer le segment {current_row + 1} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Si c'est le segment en cours de lecture, arrêter
            if self.current_playing_row == current_row:
                self._stop_playback()

            del self.segments[current_row]
            self._populate_table()

    def _move_up(self):
        """Monte le segment dans la liste"""
        current_row = self.table.currentRow()

        if current_row <= 0:
            return

        self.segments[current_row], self.segments[current_row - 1] = \
            self.segments[current_row - 1], self.segments[current_row]

        self._populate_table()
        self.table.selectRow(current_row - 1)

    def _move_down(self):
        """Descend le segment dans la liste"""
        current_row = self.table.currentRow()

        if current_row < 0 or current_row >= len(self.segments) - 1:
            return

        self.segments[current_row], self.segments[current_row + 1] = \
            self.segments[current_row + 1], self.segments[current_row]

        self._populate_table()
        self.table.selectRow(current_row + 1)

    def _reset_segments(self):
        """Réinitialise aux segments originaux"""
        reply = QMessageBox.question(
            self, "Confirmer la réinitialisation",
            "Revenir aux segments suggérés par Claude ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Arrêter la lecture si en cours
            if self.current_playing_row >= 0:
                self._stop_playback()

            self.segments = [seg.copy() for seg in self.suggestion['segments']]
            self._populate_table()

    def _validate_and_accept(self):
        """Valide les segments et ferme le dialogue"""
        if not self.segments:
            QMessageBox.warning(self, "Aucun segment",
                              "Ajoutez au moins un segment avant de continuer")
            return

        # Vérifier que les segments ne se chevauchent pas (optionnel)
        segments_tries = sorted(self.segments, key=lambda s: s['debut'])
        for i in range(len(segments_tries) - 1):
            if segments_tries[i]['fin'] > segments_tries[i + 1]['debut']:
                reply = QMessageBox.question(
                    self, "Segments qui se chevauchent",
                    "Certains segments se chevauchent. Continuer quand même ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
                break

        self.accept()

    def _update_duree_totale(self):
        """Met à jour la durée totale affichée"""
        duree_totale = sum(seg['fin'] - seg['debut'] for seg in self.segments)
        nb_segments = len(self.segments)

        self.duree_label.setText(
            f"📊 {nb_segments} segment(s) • Durée totale : {duree_totale/60:.1f} min ({duree_totale:.0f}s)"
        )

    def get_segments(self):
        """Retourne les segments modifiés"""
        segments_finaux = []

        for i in range(self.table.rowCount()):
            fichier_widget = self.table.cellWidget(i, 4)
            fichier = 'mix_complet.wav'

            if fichier_widget:
                fichier_edit = fichier_widget.findChild(QLineEdit)
                if fichier_edit:
                    fichier = fichier_edit.text()

            desc_item = self.table.item(i, 5)
            description = desc_item.text() if desc_item else ''

            if i < len(self.segments):
                segments_finaux.append({
                    'debut': self.segments[i]['debut'],
                    'fin': self.segments[i]['fin'],
                    'fichier': fichier,
                    'description': description
                })

        return segments_finaux

    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"