"""
Éditeur interactif de segments avant montage final
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
    QTimeEdit, QLineEdit, QSpinBox, QWidget,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QColor


class SegmentEditorDialog(QDialog):
    """Éditeur de segments avec ajout/suppression/modification"""

    def __init__(self, suggestion, parent=None):
        super().__init__(parent)
        self.suggestion = suggestion
        self.segments = [seg.copy() for seg in suggestion['segments']]  # Copie pour modification
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle(f"✂️ Éditeur de segments - {self.suggestion['titre']}")
        self.setMinimumSize(900, 600)

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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Début (MM:SS)", "Fin (MM:SS)", "Durée", "Fichier source", "Description", "Actions"
        ])

        # Configuration du tableau
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        layout.addWidget(self.table)

        # Boutons d'action sur les segments
        segment_buttons = QHBoxLayout()

        btn_add = QPushButton("➕ Ajouter segment")
        btn_add.clicked.connect(self._add_segment)

        btn_edit = QPushButton("✏️ Modifier segment")
        btn_edit.clicked.connect(self._edit_segment)

        btn_delete = QPushButton("🗑️ Supprimer segment")
        btn_delete.clicked.connect(self._delete_segment)

        btn_up = QPushButton("⬆️ Monter")
        btn_up.clicked.connect(self._move_up)

        btn_down = QPushButton("⬇️ Descendre")
        btn_down.clicked.connect(self._move_down)

        segment_buttons.addWidget(btn_add)
        segment_buttons.addWidget(btn_edit)
        segment_buttons.addWidget(btn_delete)
        segment_buttons.addWidget(btn_up)
        segment_buttons.addWidget(btn_down)
        segment_buttons.addStretch()

        layout.addLayout(segment_buttons)

        # Boutons de validation
        buttons_layout = QHBoxLayout()

        btn_reset = QPushButton("🔄 Réinitialiser")
        btn_reset.clicked.connect(self._reset_segments)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("✅ Créer le podcast")
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

    def _populate_table(self):
        """Remplit le tableau avec les segments"""
        self.table.setRowCount(len(self.segments))

        for i, seg in enumerate(self.segments):
            # Début (colonne 0)
            debut_item = QTableWidgetItem(self._formater_temps(seg['debut']))
            debut_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            debut_item.setFlags(debut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, debut_item)

            # Fin (colonne 1)
            fin_item = QTableWidgetItem(self._formater_temps(seg['fin']))
            fin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            fin_item.setFlags(fin_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, fin_item)

            # Durée (colonne 2)
            duree = seg['fin'] - seg['debut']
            duree_item = QTableWidgetItem(f"{duree:.1f}s")
            duree_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            duree_item.setFlags(duree_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, duree_item)

            # Fichier source (colonne 3) - Widget personnalisé
            fichier_widget = QWidget()
            fichier_layout = QHBoxLayout(fichier_widget)
            fichier_layout.setContentsMargins(2, 0, 2, 0)

            fichier_edit = QLineEdit(seg.get('fichier', 'mix_complet.wav'))
            fichier_edit.setProperty('row', i)  # Stocker l'indice de ligne

            fichier_btn = QPushButton("📁")
            fichier_btn.setMaximumWidth(30)
            fichier_btn.setProperty('row', i)
            fichier_btn.clicked.connect(self._browse_fichier_source)

            fichier_layout.addWidget(fichier_edit)
            fichier_layout.addWidget(fichier_btn)

            self.table.setCellWidget(i, 3, fichier_widget)

            # Description (colonne 4)
            desc_item = QTableWidgetItem(seg.get('description', ''))
            self.table.setItem(i, 4, desc_item)

            # Actions (colonne 5)
            actions_item = QTableWidgetItem("🔍")
            actions_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            actions_item.setFlags(actions_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, actions_item)

        self._update_duree_totale()

    def _browse_fichier_source(self):
        """Parcourir un fichier source pour un segment"""
        from PyQt6.QtWidgets import QFileDialog

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
            fichier_widget = self.table.cellWidget(row, 3)
            fichier_edit = fichier_widget.findChild(QLineEdit)
            if fichier_edit:
                fichier_edit.setText(file)

    def _add_segment(self):
        """Ajoute un nouveau segment"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

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
        fichier_edit = QLineEdit("mix_complet.wav")
        fichier_btn = QPushButton("📁")

        def browse_file():
            from PyQt6.QtWidgets import QFileDialog
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

        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

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
        fichier_btn = QPushButton("📁")

        def browse_file():
            from PyQt6.QtWidgets import QFileDialog
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
            fichier_widget = self.table.cellWidget(i, 3)
            fichier = 'mix_complet.wav'

            if fichier_widget:
                fichier_edit = fichier_widget.findChild(QLineEdit)
                if fichier_edit:
                    fichier = fichier_edit.text()
                    print(f"Segment {i}: fichier = {fichier}")  # DEBUG

            desc_item = self.table.item(i, 4)
            description = desc_item.text() if desc_item else ''

            if i < len(self.segments):
                segments_finaux.append({
                    'debut': self.segments[i]['debut'],
                    'fin': self.segments[i]['fin'],
                    'fichier': fichier,
                    'description': description
                })

        print(f"Segments finaux: {segments_finaux}")  # DEBUG
        return segments_finaux

    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"