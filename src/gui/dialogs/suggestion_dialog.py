"""
Dialogue de sélection des suggestions Claude
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget, QGroupBox,
    QRadioButton, QButtonGroup, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt


class SuggestionsDialog(QDialog):
    """Dialogue pour afficher et sélectionner les suggestions IA"""

    def __init__(self, suggestions, parent=None, ai_analyzer=None, transcription=None, duree_cible=None, ton=None):
        super().__init__(parent)
        self.suggestions = suggestions
        self.suggestion_selectionnee = None
        self.ai_analyzer = ai_analyzer
        self.transcription = transcription
        self.duree_cible = duree_cible
        self.ton = ton
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("💡 Suggestions de montage Claude")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # En-tête
        header = QLabel(f"Claude a généré {len(self.suggestions)} suggestions de montage")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Zone scrollable pour les suggestions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Groupe de boutons radio
        self.button_group = QButtonGroup(self)

        # Afficher chaque suggestion
        for i, suggestion in enumerate(self.suggestions):
            suggestion_box = self._create_suggestion_box(suggestion, i)
            scroll_layout.addWidget(suggestion_box)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Boutons d'action
        buttons_layout = QHBoxLayout()

        btn_refine = QPushButton("🔄 Affiner avec feedback")
        btn_refine.clicked.connect(self._affiner_suggestions)

        btn_custom = QPushButton("✏️ Découpage personnalisé")
        btn_custom.clicked.connect(self._decoupage_perso)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("✅ Monter cette suggestion")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._valider_selection)
        btn_ok.setStyleSheet("padding: 8px; font-weight: bold;")

        buttons_layout.addWidget(btn_refine)
        buttons_layout.addWidget(btn_custom)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_ok)

        layout.addLayout(buttons_layout)

    def _create_suggestion_box(self, suggestion, index):
        """Crée une box pour une suggestion"""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Radio button avec titre
        radio = QRadioButton(f"Suggestion {index + 1} : {suggestion['titre']}")
        radio.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.button_group.addButton(radio, index)

        # Sélectionner la première par défaut
        if index == 0:
            radio.setChecked(True)

        layout.addWidget(radio)

        # Infos
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"⏱️ Durée: {suggestion['duree_estimee']} min"))
        info_layout.addWidget(QLabel(f"📝 {len(suggestion['segments'])} segments"))
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Commentaire
        comment = QLabel(suggestion['commentaire'])
        comment.setWordWrap(True)
        comment.setStyleSheet("color: #555; margin: 10px 0; padding: 8px; background-color: #f9f9f9; border-radius: 4px;")
        layout.addWidget(comment)

        # Liste des segments (avec scroll area pour éviter les problèmes d'affichage)
        segments_widget = QWidget()
        segments_widget.setStyleSheet("background-color: white;")  # Fond blanc
        segments_layout = QVBoxLayout(segments_widget)
        segments_layout.setContentsMargins(5, 5, 5, 5)

        for j, seg in enumerate(suggestion['segments'], 1):
            debut_str = self._formater_temps(seg['debut'])
            fin_str = self._formater_temps(seg['fin'])
            duree = seg['fin'] - seg['debut']

            seg_label = QLabel(f"{j}. [{debut_str} → {fin_str}] ({duree:.0f}s) - {seg['description']}")
            seg_label.setWordWrap(True)
            seg_label.setStyleSheet("padding: 2px; color: #333; background-color: transparent;")
            segments_layout.addWidget(seg_label)

        segments_scroll = QScrollArea()
        segments_scroll.setWidget(segments_widget)
        segments_scroll.setWidgetResizable(True)
        segments_scroll.setMaximumHeight(150)
        segments_scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                width: 10px;
                background-color: #f0f0f0;
            }
            QScrollBar::handle:vertical {
                background-color: #888;
                border-radius: 5px;
            }
        """)
        layout.addWidget(segments_scroll)

        group.setLayout(layout)
        return group

    def _valider_selection(self):
        """Valide la sélection et ouvre l'éditeur de segments"""
        selected_id = self.button_group.checkedId()
        if selected_id >= 0:
            suggestion = self.suggestions[selected_id]

            # IMPORTANT : Copier d'abord
            suggestion_copy = {
                'titre': suggestion['titre'],
                'commentaire': suggestion['commentaire'],
                'duree_estimee': suggestion['duree_estimee'],
                'segments': []
            }

            # Puis ajouter les segments avec le fichier
            for seg in suggestion['segments']:
                segment_copy = seg.copy()
                # Utiliser le fichier déjà présent OU ajouter mix_complet.wav par défaut
                if 'fichier' not in segment_copy:
                    segment_copy['fichier'] = 'mix_complet.wav'
                suggestion_copy['segments'].append(segment_copy)

            # Ouvrir l'éditeur
            from src.gui.dialogs.segment_editor_dialog import SegmentEditorDialog

            editor = SegmentEditorDialog(suggestion_copy, self)

            if editor.exec():
                segments_modifies = editor.get_segments()

                suggestion_finale = suggestion_copy.copy()
                suggestion_finale['segments'] = segments_modifies

                duree_totale = sum(s['fin'] - s['debut'] for s in segments_modifies)
                suggestion_finale['duree_estimee'] = round(duree_totale / 60, 1)

                self.suggestion_selectionnee = suggestion_finale
                self.accept()
            # Sinon, retour au dialogue de suggestions (ne ferme pas)

    def _affiner_suggestions(self):
        """Ouvre un dialogue pour affiner avec feedback"""
        from PyQt6.QtWidgets import QInputDialog, QProgressDialog
        from PyQt6.QtCore import Qt

        feedback, ok = QInputDialog.getMultiLineText(
            self,
            "Affiner les suggestions",
            "Décrivez vos attentes pour affiner les suggestions :\n"
            "(ex: 'Trop long, réduis à 3 minutes' ou 'Plus de moments drôles')"
        )

        if ok and feedback and self.ai_analyzer:
            # Dialogue de progression
            progress = QProgressDialog("Relance de Claude avec votre feedback...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setWindowTitle("Affinage en cours")
            progress.show()

            try:
                # Construire un prompt d'affinage
                import json
                prompt_affinage = f"""Voici les suggestions précédentes que tu as générées :

{json.dumps(self.suggestions, indent=2, ensure_ascii=False)}

L'utilisateur a donné ce feedback :
"{feedback}"

Génère 3 nouvelles suggestions en tenant compte de ce feedback.
Garde le même format JSON que précédemment."""

                # Appeler Claude
                response = self.ai_analyzer.client.messages.create(
                    model=self.ai_analyzer.config['modele'],
                    max_tokens=4096,
                    temperature=self.ai_analyzer.config['temperature'],
                    messages=[{
                        "role": "user",
                        "content": prompt_affinage
                    }]
                )

                # Parser la réponse
                nouvelles_suggestions = self.ai_analyzer._parser_reponse(
                    response.content[0].text
                )

                progress.close()

                # Remplacer les suggestions et rafraîchir
                self.suggestions = nouvelles_suggestions
                self._refresh_ui()

            except Exception as e:
                progress.close()
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'affinage : {e}")

    def _refresh_ui(self):
        """Rafraîchit l'interface avec les nouvelles suggestions"""
        # Supprimer l'ancien contenu
        layout = self.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Recréer l'interface
        self.button_group = QButtonGroup(self)
        self.init_ui()

    def _decoupage_perso(self):
        """Permet un découpage personnalisé"""
        from src.gui.dialogs.segment_editor_dialog import SegmentEditorDialog

        # Créer une suggestion vide comme template
        suggestion_template = {
            'titre': 'Découpage personnalisé',
            'commentaire': 'Créé manuellement par l\'utilisateur',
            'duree_estimee': 1,
            'segments': [
                {
                    'debut': 0.0,
                    'fin': 60.0,
                    'fichier': 'mix_complet.wav',  # ← IMPORTANT
                    'description': 'Segment exemple - à modifier'
                }
            ]
        }

        editor = SegmentEditorDialog(suggestion_template, self)

        if editor.exec():
            segments_modifies = editor.get_segments()

            # Créer la suggestion finale
            suggestion_finale = {
                'titre': 'Découpage personnalisé',
                'commentaire': 'Créé manuellement par l\'utilisateur',
                'duree_estimee': round(sum(s['fin'] - s['debut'] for s in segments_modifies) / 60, 1),
                'segments': segments_modifies
            }

            self.suggestion_selectionnee = suggestion_finale
            self.accept()

        editor = SegmentEditorDialog(suggestion_template, self)

        if editor.exec():
            segments_modifies = editor.get_segments()

            # Créer la suggestion finale
            suggestion_finale = {
                'titre': 'Découpage personnalisé',
                'commentaire': 'Créé manuellement par l\'utilisateur',
                'duree_estimee': round(sum(s['fin'] - s['debut'] for s in segments_modifies) / 60, 1),
                'segments': segments_modifies
            }

            self.suggestion_selectionnee = suggestion_finale
            self.accept()

    @staticmethod
    def _formater_temps(secondes: float) -> str:
        """Formate les secondes en MM:SS"""
        minutes = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_suggestion(self):
        """Retourne la suggestion sélectionnée"""
        return self.suggestion_selectionnee