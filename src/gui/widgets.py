"""
Widgets personnalisés pour l'interface Podcasteur
Boutons, checkboxes, dropdowns et sliders stylisés
"""

from PyQt6.QtWidgets import QPushButton, QCheckBox, QComboBox, QSlider, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt


class PrimaryButton(QPushButton):
    """Bouton principal pour les actions importantes

    Utilisation : actions primaires comme "Lancer", "Valider", "Créer"
    Style : fond bleu, texte blanc, en gras
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du bouton principal"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2d5d8f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)


class SecondaryButton(QPushButton):
    """Bouton secondaire pour les actions moins prioritaires

    Utilisation : actions secondaires comme "Annuler", "Retour", "Modifier"
    Style : fond transparent, bordure bleue, texte bleu
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du bouton secondaire"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4a90e2;
                border: 2px solid #4a90e2;
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #4a90e2;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #357abd;
                color: #ffffff;
                border-color: #357abd;
            }
            QPushButton:disabled {
                border-color: #cccccc;
                color: #aaaaaa;
            }
        """)


class DangerButton(QPushButton):
    """Bouton pour les actions dangereuses ou destructives

    Utilisation : actions destructives comme "Supprimer", "Effacer", "Reset"
    Style : fond rouge, texte blanc
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du bouton danger"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41707;
            }
            QPushButton:disabled {
                background-color: #ffcccc;
                color: #cccccc;
            }
        """)


class SuccessButton(QPushButton):
    """Bouton pour les actions de succès ou de validation finale

    Utilisation : actions de validation finale comme "Créer le podcast", "Terminer"
    Style : fond vert, texte blanc, en gras
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du bouton succès"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)


class NeutralButton(QPushButton):
    """Bouton neutre pour les actions standard

    Utilisation : actions neutres comme "Parcourir", "Ajouter fichier", "Voir"
    Style : fond gris clair, texte foncé
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du bouton neutre"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #b0b0b0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f9f9f9;
                color: #aaaaaa;
                border-color: #e0e0e0;
            }
        """)




class StyledCheckBox(QCheckBox):
    """Checkbox stylisée avec meilleure visibilité

    Améliore la clarté visuelle par rapport au checkbox PyQt6 par défaut
    """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du checkbox"""
        self.setStyleSheet("""
            QCheckBox {
                color: #333333;
                spacing: 8px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4a90e2;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #357abd;
                background-color: #f0f8ff;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border-color: #4a90e2;
                image: none;
            }
            QCheckBox::indicator:checked:after {
                content: "✓";
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QCheckBox::indicator:disabled {
                border-color: #cccccc;
                background-color: #f5f5f5;
            }
        """)


class StyledComboBox(QComboBox):
    """ComboBox/Dropdown stylisé avec meilleure lisibilité

    Améliore la clarté et l'apparence des menus déroulants
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du combobox"""
        self.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 28px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #4a90e2;
            }
            QComboBox:focus {
                border-color: #4a90e2;
                background-color: #f0f8ff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #d0d0d0;
                background-color: #f8f8f8;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::drop-down:hover {
                background-color: #e8e8e8;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #4a90e2;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #357abd;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #4a90e2;
                selection-color: #ffffff;
                border: 2px solid #4a90e2;
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                min-height: 24px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
                color: #333333;
            }
            QComboBox:disabled {
                background-color: #f5f5f5;
                color: #aaaaaa;
                border-color: #e0e0e0;
            }
        """)


class StyledSlider(QSlider):
    """Slider stylisé avec meilleure visibilité

    Améliore l'apparence et la manipulation des sliders
    """

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du slider"""
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #d0d0d0;
                height: 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
            QSlider::groove:horizontal:hover {
                background-color: #e8e8e8;
            }
            QSlider::handle:horizontal {
                background-color: #4a90e2;
                border: 2px solid #357abd;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #357abd;
                border-color: #2d5d8f;
            }
            QSlider::handle:horizontal:pressed {
                background-color: #2d5d8f;
            }
            QSlider::sub-page:horizontal {
                background-color: #4a90e2;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background-color: #f5f5f5;
                border-radius: 4px;
            }
            QSlider:disabled {
                opacity: 0.5;
            }
            
            /* Vertical slider */
            QSlider::groove:vertical {
                border: 1px solid #d0d0d0;
                width: 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background-color: #4a90e2;
                border: 2px solid #357abd;
                width: 18px;
                height: 18px;
                margin: 0 -6px;
                border-radius: 9px;
            }
            QSlider::handle:vertical:hover {
                background-color: #357abd;
            }
            QSlider::sub-page:vertical {
                background-color: #4a90e2;
                border-radius: 4px;
            }
        """)




class StyledSpinBox(QSpinBox):
    """SpinBox stylisé avec boutons +/- visibles

    Améliore la visibilité des boutons d'incrémentation
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du spinbox"""
        self.setStyleSheet("""
            QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                padding: 4px 8px;
                min-height: 28px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #4a90e2;
            }
            QSpinBox:focus {
                border-color: #4a90e2;
                background-color: #f0f8ff;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #d0d0d0;
                border-top-right-radius: 4px;
                background-color: #f8f8f8;
            }
            QSpinBox::up-button:hover {
                background-color: #4a90e2;
            }
            QSpinBox::up-button:pressed {
                background-color: #357abd;
            }
            QSpinBox::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid #333333;
            }
            QSpinBox::up-button:hover .up-arrow,
            QSpinBox::up-arrow:hover {
                border-bottom-color: #ffffff;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                border-left: 1px solid #d0d0d0;
                border-bottom-right-radius: 4px;
                background-color: #f8f8f8;
            }
            QSpinBox::down-button:hover {
                background-color: #4a90e2;
            }
            QSpinBox::down-button:pressed {
                background-color: #357abd;
            }
            QSpinBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
            }
            QSpinBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QSpinBox:disabled {
                background-color: #f5f5f5;
                color: #aaaaaa;
                border-color: #e0e0e0;
            }
        """)


class StyledDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox stylisé avec boutons +/- visibles

    Version pour nombres décimaux
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """Configure le style du double spinbox"""
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                padding: 4px 8px;
                min-height: 28px;
                font-size: 13px;
            }
            QDoubleSpinBox:hover {
                border-color: #4a90e2;
            }
            QDoubleSpinBox:focus {
                border-color: #4a90e2;
                background-color: #f0f8ff;
            }
            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #d0d0d0;
                border-top-right-radius: 4px;
                background-color: #f8f8f8;
            }
            QDoubleSpinBox::up-button:hover {
                background-color: #4a90e2;
            }
            QDoubleSpinBox::up-button:pressed {
                background-color: #357abd;
            }
            QDoubleSpinBox::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid #333333;
            }
            QDoubleSpinBox::up-arrow:hover {
                border-bottom-color: #ffffff;
            }
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                border-left: 1px solid #d0d0d0;
                border-bottom-right-radius: 4px;
                background-color: #f8f8f8;
            }
            QDoubleSpinBox::down-button:hover {
                background-color: #4a90e2;
            }
            QDoubleSpinBox::down-button:pressed {
                background-color: #357abd;
            }
            QDoubleSpinBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
            }
            QDoubleSpinBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QDoubleSpinBox:disabled {
                background-color: #f5f5f5;
                color: #aaaaaa;
                border-color: #e0e0e0;
            }
        """)


# ============== EXEMPLE D'UTILISATION ==============

if __name__ == '__main__':
    """Exemple de démonstration des widgets"""
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
    import sys

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Démonstration des widgets Podcasteur")
    window.setMinimumWidth(500)

    layout = QVBoxLayout(window)

    # === BOUTONS ===
    layout.addWidget(QLabel("Boutons :"))
    btn_primary = PrimaryButton("🚀 Lancer le workflow")
    layout.addWidget(btn_primary)

    btn_secondary = SecondaryButton("⚙️ Paramètres")
    layout.addWidget(btn_secondary)

    btn_danger = DangerButton("🗑️ Supprimer tout")
    layout.addWidget(btn_danger)

    btn_success = SuccessButton("✅ Créer le podcast")
    layout.addWidget(btn_success)

    btn_neutral = NeutralButton("📁 Parcourir")
    layout.addWidget(btn_neutral)

    # === CHECKBOXES ===
    layout.addWidget(QLabel("\nCheckboxes :"))
    check1 = StyledCheckBox("Détecter les speakers")
    check1.setChecked(True)
    layout.addWidget(check1)

    check2 = StyledCheckBox("Normaliser l'audio")
    layout.addWidget(check2)

    # === COMBOBOX ===
    layout.addWidget(QLabel("\nDropdown :"))
    combo = StyledComboBox()
    combo.addItems(["informatif et dynamique", "détendu et conversationnel", "professionnel et concis"])
    layout.addWidget(combo)

    # === SPINBOX ===
    layout.addWidget(QLabel("\nSpinBox (nombre entier) :"))
    spinbox = StyledSpinBox()
    spinbox.setRange(1, 10)
    spinbox.setValue(5)
    layout.addWidget(spinbox)

    layout.addWidget(QLabel("\nDoubleSpinBox (nombre décimal) :"))
    double_spinbox = StyledDoubleSpinBox()
    double_spinbox.setRange(0.0, 10.0)
    double_spinbox.setValue(2.5)
    double_spinbox.setSingleStep(0.5)
    layout.addWidget(double_spinbox)

    # === SLIDER ===
    layout.addWidget(QLabel("\nSlider :"))
    slider_layout = QHBoxLayout()
    slider = StyledSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(70)
    slider.setMinimumWidth(300)
    slider_label = QLabel("70%")
    slider.valueChanged.connect(lambda v: slider_label.setText(f"{v}%"))
    slider_layout.addWidget(slider)
    slider_layout.addWidget(slider_label)
    slider_layout.addStretch()
    layout.addLayout(slider_layout)

    layout.addStretch()

    window.show()
    sys.exit(app.exec())