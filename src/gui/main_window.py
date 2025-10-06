"""
Fenêtre principale avec workflow automatique complet
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFileDialog,
    QListWidget, QSpinBox, QLineEdit, QTextEdit,
    QProgressBar, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
import yaml
import os
import sys


class MainWindow(QMainWindow):
    """Fenêtre principale de Podcasteur GUI"""

    def __init__(self):
        super().__init__()
        self.fichiers_audio = []
        self.config = self._charger_config()

        # Workers et données intermédiaires
        self.concat_worker = None
        self.transcription_worker = None
        self.ai_worker = None
        self.montage_worker = None

        self.fichier_mix = None
        self.transcription = None
        self.suggestions = None

        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Podcasteur v1.4.0 - Éditeur de podcasts IA")
        self.setMinimumSize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # En-tête
        header = QLabel("🎙️ Podcasteur - Éditeur de podcasts automatisé")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Onglets
        tabs = QTabWidget()
        tabs.addTab(self._create_auto_tab(), "Workflow Automatique")
        tabs.addTab(self._create_manual_tab(), "Workflow Manuel")
        tabs.addTab(self._create_config_tab(), "Configuration")
        layout.addWidget(tabs)

        self.statusBar().showMessage("Prêt")

    def _create_auto_tab(self):
        """Crée l'onglet workflow automatique"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Sélection des fichiers
        files_group = QGroupBox("1. Fichiers audio")
        files_layout = QVBoxLayout()

        files_buttons = QHBoxLayout()
        btn_add_files = QPushButton("Ajouter fichiers")
        btn_add_files.clicked.connect(self._add_files)
        btn_add_folder = QPushButton("Ajouter dossier")
        btn_add_folder.clicked.connect(self._add_folder)
        btn_clear = QPushButton("Effacer tout")
        btn_clear.clicked.connect(self._clear_files)

        files_buttons.addWidget(btn_add_files)
        files_buttons.addWidget(btn_add_folder)
        files_buttons.addWidget(btn_clear)
        files_buttons.addStretch()

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(150)

        files_layout.addLayout(files_buttons)
        files_layout.addWidget(self.files_list)
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)

        # Options
        options_group = QGroupBox("2. Options")
        options_layout = QVBoxLayout()

        # Durée cible
        duree_layout = QHBoxLayout()
        duree_layout.addWidget(QLabel("Durée cible (minutes) :"))
        self.duree_spin = QSpinBox()
        self.duree_spin.setMinimum(1)
        self.duree_spin.setMaximum(120)
        self.duree_spin.setValue(5)
        duree_layout.addWidget(self.duree_spin)
        duree_layout.addStretch()
        options_layout.addLayout(duree_layout)

        # Ton souhaité
        ton_layout = QHBoxLayout()
        ton_layout.addWidget(QLabel("Ton souhaité :"))
        self.ton_input = QLineEdit("informatif et dynamique")
        ton_layout.addWidget(self.ton_input)
        options_layout.addLayout(ton_layout)

        # Checkbox speakers
        self.detect_speakers_check = QCheckBox("Détecter les speakers (nécessite token HF)")
        options_layout.addWidget(self.detect_speakers_check)

        # Checkbox + champ mix
        mix_layout = QHBoxLayout()
        self.use_mix_check = QCheckBox("Utiliser fichier mix existant :")
        self.use_mix_check.stateChanged.connect(self._toggle_mix_mode)
        mix_layout.addWidget(self.use_mix_check)

        self.mix_file_input = QLineEdit()
        self.mix_file_input.setEnabled(False)
        self.mix_file_input.setPlaceholderText("Aucun fichier sélectionné")
        mix_layout.addWidget(self.mix_file_input)

        self.btn_browse_mix = QPushButton("Parcourir")
        self.btn_browse_mix.clicked.connect(self._browse_mix_file)
        self.btn_browse_mix.setEnabled(False)
        mix_layout.addWidget(self.btn_browse_mix)

        options_layout.addLayout(mix_layout)

        # Checkbox + champ transcription
        trans_layout = QHBoxLayout()
        self.use_transcription_check = QCheckBox("Utiliser transcription existante :")
        self.use_transcription_check.stateChanged.connect(self._toggle_transcription_mode)
        trans_layout.addWidget(self.use_transcription_check)

        self.transcription_file_input = QLineEdit()
        self.transcription_file_input.setEnabled(False)
        self.transcription_file_input.setPlaceholderText("Aucun fichier sélectionné")
        trans_layout.addWidget(self.transcription_file_input)

        self.btn_browse_trans = QPushButton("Parcourir")
        self.btn_browse_trans.clicked.connect(self._browse_transcription_file)
        self.btn_browse_trans.setEnabled(False)
        trans_layout.addWidget(self.btn_browse_trans)

        options_layout.addLayout(trans_layout)

        # Dossier de sortie
        sortie_layout = QHBoxLayout()
        sortie_layout.addWidget(QLabel("Dossier de sortie :"))
        self.sortie_input = QLineEdit()
        self.sortie_input.setPlaceholderText("Sélectionnez un dossier de sortie...")
        sortie_layout.addWidget(self.sortie_input, 1)
        btn_browse_sortie = QPushButton("Parcourir")
        btn_browse_sortie.clicked.connect(self._browse_sortie_folder)
        sortie_layout.addWidget(btn_browse_sortie)
        options_layout.addLayout(sortie_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Console de sortie
        console_group = QGroupBox("3. Progression")
        console_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(200)

        console_layout.addWidget(self.progress_bar)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)

        # Bouton lancer
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_start = QPushButton("🚀 Lancer le workflow automatique")
        self.btn_start.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold;")
        self.btn_start.clicked.connect(self._start_auto_workflow)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget

    def _create_manual_tab(self):
        """Crée l'onglet workflow manuel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Workflow manuel (à implémenter)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget

    def _create_config_tab(self):
        """Crée l'onglet configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        sound_group = QGroupBox("Éléments sonores")
        sound_layout = QVBoxLayout()

        self.enable_sounds_check = QCheckBox("Activer intro/outro")
        self.enable_sounds_check.setChecked(
            self.config.get('elements_sonores', {}).get('activer', False)
        )

        intro_layout = QHBoxLayout()
        intro_layout.addWidget(QLabel("Intro :"))
        self.intro_input = QLineEdit(
            self.config.get('elements_sonores', {}).get('generique_debut', {}).get('fichier', 'assets/intro.mp3')
        )
        btn_intro = QPushButton("Parcourir")
        btn_intro.clicked.connect(lambda: self._browse_file(self.intro_input))
        intro_layout.addWidget(self.intro_input)
        intro_layout.addWidget(btn_intro)

        outro_layout = QHBoxLayout()
        outro_layout.addWidget(QLabel("Outro :"))
        self.outro_input = QLineEdit(
            self.config.get('elements_sonores', {}).get('generique_fin', {}).get('fichier', 'assets/outro.mp3')
        )
        btn_outro = QPushButton("Parcourir")
        btn_outro.clicked.connect(lambda: self._browse_file(self.outro_input))
        outro_layout.addWidget(self.outro_input)
        outro_layout.addWidget(btn_outro)

        sound_layout.addWidget(self.enable_sounds_check)
        sound_layout.addLayout(intro_layout)
        sound_layout.addLayout(outro_layout)
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)

        btn_save = QPushButton("Sauvegarder la configuration")
        btn_save.clicked.connect(self._save_config)
        layout.addWidget(btn_save)
        layout.addStretch()

        return widget

    def _start_auto_workflow(self):
        """Lance le workflow automatique avec chaînage des workers"""
        # Déterminer le mode de fonctionnement
        mode_mix = self.use_mix_check.isChecked() and bool(self.mix_file_input.text())
        mode_trans = self.use_transcription_check.isChecked() and bool(self.transcription_file_input.text())

        # Validation
        if not mode_mix and not self.fichiers_audio:
            QMessageBox.warning(self, "Aucun fichier",
                                "Ajoutez des fichiers audio ou sélectionnez un fichier mix existant.")
            return

        if self.use_mix_check.isChecked() and not self.mix_file_input.text():
            QMessageBox.warning(self, "Fichier mix manquant",
                                "Sélectionnez un fichier mix ou décochez l'option.")
            return

        # Vérifier la clé API Anthropic
        cle_api = os.getenv('ANTHROPIC_API_KEY')
        if not cle_api:
            QMessageBox.critical(self, "Clé API manquante",
                                 "ANTHROPIC_API_KEY non définie dans .env")
            return

        # Vérifier le dossier de sortie
        if not self.sortie_input.text().strip():
            QMessageBox.warning(self, "Dossier de sortie manquant",
                                "Veuillez sélectionner un dossier de sortie.")
            return

        dossier_sortie = Path(self.sortie_input.text())
        try:
            dossier_sortie.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Erreur dossier de sortie",
                                 f"Impossible de créer le dossier : {e}")
            return

        self.btn_start.setEnabled(False)
        self._log("🚀 Démarrage du workflow automatique...")
        self._log(f"   Mode mix existant : {'OUI' if mode_mix else 'NON'}")
        self._log(f"   Mode transcription existante : {'OUI' if mode_trans else 'NON'}")

        # Décision du workflow
        if mode_mix:
            # Utiliser le fichier mix fourni
            self.fichier_mix = Path(self.mix_file_input.text())
            self._log(f"\n📍 ÉTAPE 1/4 : Utilisation du fichier mix fourni")
            self._log(f"📄 Fichier : {self.fichier_mix.name}")

            if mode_trans:
                # Skip aussi la transcription
                self._charger_transcription_existante()
            else:
                # Faire la transcription
                self._start_transcription()
        else:
            # Workflow classique avec concaténation
            self._log(f"\n📍 ÉTAPE 1/4 : Concaténation de {len(self.fichiers_audio)} fichiers")
            self._start_concatenation()

    def _start_concatenation(self):
        """Démarre la concaténation"""
        from src.gui.workers.concat_worker import ConcatWorker
        from ..audio_processor import AudioProcessor

        self._log("\n📍 ÉTAPE 1/4 : Concaténation")

        processor = AudioProcessor(self.config)
        dossier_sortie = Path(self.sortie_input.text())
        dossier_sortie.mkdir(parents=True, exist_ok=True)
        fichier_mix = dossier_sortie / "mix_complet.wav"

        self.concat_worker = ConcatWorker(
            processor,
            self.fichiers_audio,
            fichier_mix,
            methode_tri=self.config['tri_fichiers']['methode'],
            ordre_tri=self.config['tri_fichiers']['ordre']
        )

        self.concat_worker.progress.connect(self._update_progress)
        self.concat_worker.finished.connect(self._on_concat_finished)
        self.concat_worker.error.connect(self._on_error)
        self.concat_worker.start()

    def _on_concat_finished(self, fichier_mix):
        """Concaténation terminée → lancer transcription"""
        self.fichier_mix = fichier_mix
        self._start_transcription()

    def _charger_transcription_existante(self):
        """Charge une transcription depuis un fichier"""
        chemin_trans = Path(self.transcription_file_input.text())

        self._log("\n📍 ÉTAPE 2/4 : Chargement de la transcription existante")
        self._log(f"📄 Fichier : {chemin_trans.name}")

        try:
            with open(chemin_trans, 'r', encoding='utf-8') as f:
                if chemin_trans.suffix == '.json':
                    import json
                    self.transcription = json.load(f)
                else:
                    # Format texte simple
                    texte = f.read()
                    self.transcription = {
                        'texte': texte,
                        'langue': 'fr',
                        'segments': []
                    }

            self._log("✅ Transcription chargée")
            self._start_ai_analysis()

        except Exception as e:
            self._on_error(f"Erreur chargement transcription : {e}")

    def _start_transcription(self):
        """Démarre la transcription"""

        # Dans main_window.py, méthode _start_transcription
        def _start_transcription(self):
            """Démarre la transcription"""

            # Vérifier si on est dans un exe
            if getattr(sys, 'frozen', False):
                QMessageBox.warning(
                    self,
                    "Fonctionnalité non disponible",
                    "La transcription n'est pas disponible dans la version exécutable.\n\n"
                    "Veuillez :\n"
                    "1. Utiliser un fichier transcription existant\n"
                    "2. OU installer Python et lancer : python podcasteur_gui.py"
                )
                self.btn_start.setEnabled(True)
                return

        from src.gui.workers.transcription_worker import TranscriptionWorker
        from ..transcriber import Transcriber

        self._log("\n📍 ÉTAPE 2/4 : Transcription")

        transcriber = Transcriber(self.config)

        # Token HF si diarisation
        token_hf = None
        if self.detect_speakers_check.isChecked():
            token_hf = os.getenv('HUGGINGFACE_TOKEN')
            if not token_hf:
                self._log("⚠️ HUGGINGFACE_TOKEN manquant, diarisation ignorée")

        self.transcription_worker = TranscriptionWorker(
            transcriber,
            self.fichier_mix,
            detecter_speakers=self.detect_speakers_check.isChecked(),
            token_hf=token_hf
        )

        self.transcription_worker.progress.connect(self._update_progress)
        self.transcription_worker.finished.connect(self._on_transcription_finished)
        self.transcription_worker.error.connect(self._on_error)
        self.transcription_worker.start()

    def _on_transcription_finished(self, transcription):
        """Transcription terminée → lancer analyse IA"""
        self.transcription = transcription
        self._start_ai_analysis()

    def _start_ai_analysis(self):
        """Démarre l'analyse IA"""
        from src.gui.workers.ai_worker import AIWorker
        from ..ai_analyzer import AIAnalyzer

        self._log("\n📍 ÉTAPE 3/4 : Analyse IA")

        cle_api = os.getenv('ANTHROPIC_API_KEY')
        analyzer = AIAnalyzer(self.config, cle_api)

        self.ai_worker = AIWorker(
            analyzer,
            self.transcription,
            duree_cible=self.duree_spin.value(),
            ton=self.ton_input.text()
        )

        self.ai_worker.progress.connect(self._update_progress)
        self.ai_worker.finished.connect(self._on_ai_finished)
        self.ai_worker.error.connect(self._on_error)
        self.ai_worker.start()

    def _on_ai_finished(self, suggestions):
        """Analyse IA terminée → afficher suggestions"""
        self.suggestions = suggestions

        # CORRECTION : Ajouter le fichier source à TOUS les segments
        fichier_source = str(self.fichier_mix) if self.fichier_mix else 'mix_complet.wav'
        print(f"📎 Ajout fichier source aux suggestions : {fichier_source}")

        for suggestion in self.suggestions:
            for segment in suggestion['segments']:
                if 'fichier' not in segment:
                    segment['fichier'] = fichier_source

        self._show_suggestions_dialog()

    def _show_suggestions_dialog(self):
        """Affiche le dialogue de sélection"""
        from src.gui.dialogs.suggestion_dialog import SuggestionsDialog

        dialog = SuggestionsDialog(self.suggestions, self)

        if dialog.exec():
            suggestion = dialog.get_suggestion()
            if suggestion:
                self._start_montage(suggestion)
        else:
            self._log("\n❌ Sélection annulée")
            self.btn_start.setEnabled(True)

    def _start_montage(self, suggestion):
        """Démarre le montage"""
        from src.gui.workers.montage_worker import MontageWorker
        from ..audio_processor import AudioProcessor

        self._log(f"\n📍 ÉTAPE 4/4 : Montage - {suggestion['titre']}")

        processor = AudioProcessor(self.config)
        dossier_sortie = Path(self.sortie_input.text())

        self.montage_worker = MontageWorker(
            processor,
            self.fichier_mix,
            suggestion,
            dossier_sortie
        )

        self.montage_worker.progress.connect(self._update_progress)
        self.montage_worker.finished.connect(self._on_montage_finished)
        self.montage_worker.error.connect(self._on_error)
        self.montage_worker.start()

    def _on_montage_finished(self, fichier_final):
        """Montage terminé"""
        self._log(f"\n✅ WORKFLOW TERMINÉ !")
        self._log(f"📁 Fichier final : {fichier_final}")

        QMessageBox.information(self, "Succès",
                              f"Podcast créé avec succès !\n\n{fichier_final}")

        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(100)

    def _update_progress(self, value, message):
        """Met à jour la progression"""
        self.progress_bar.setValue(value)
        self._log(message)

    def _on_error(self, error_msg):
        """Gère les erreurs"""
        self._log(f"\n❌ ERREUR : {error_msg}")
        QMessageBox.critical(self, "Erreur", error_msg)
        self.btn_start.setEnabled(True)

    def _add_files(self):
        """Ajoute des fichiers audio"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Sélectionner des fichiers audio", "",
            "Fichiers audio (*.wav *.mp3 *.ogg *.flac *.m4a)"
        )
        for file in files:
            if file not in self.fichiers_audio:
                self.fichiers_audio.append(file)
                self.files_list.addItem(Path(file).name)
        self._update_status()

    def _add_folder(self):
        """Ajoute tous les fichiers audio d'un dossier"""
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if folder:
            extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
            for ext in extensions:
                for file in Path(folder).glob(f'*{ext}'):
                    file_str = str(file)
                    if file_str not in self.fichiers_audio:
                        self.fichiers_audio.append(file_str)
                        self.files_list.addItem(file.name)
        self._update_status()

    def _clear_files(self):
        """Efface tous les fichiers"""
        self.fichiers_audio.clear()
        self.files_list.clear()
        self._update_status()

    def _toggle_mix_mode(self, state):
        """Active/désactive le mode mix"""
        is_mix = state == Qt.CheckState.Checked.value
        self.mix_file_input.setEnabled(is_mix)
        self.btn_browse_mix.setEnabled(is_mix)

        # Désactiver sélection fichiers si mix activé
        if is_mix:
            self.files_list.setEnabled(False)
        else:
            self.files_list.setEnabled(True)

    def _toggle_transcription_mode(self, state):
        """Active/désactive le mode transcription existante"""
        is_trans = state == Qt.CheckState.Checked.value
        self.transcription_file_input.setEnabled(is_trans)
        self.btn_browse_trans.setEnabled(is_trans)

    def _browse_mix_file(self):
        """Parcourir un fichier mix"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier mix", "",
            "Fichiers audio (*.wav *.mp3 *.flac)"
        )
        if file:
            self.mix_file_input.setText(file)

    def _browse_transcription_file(self):
        """Parcourir un fichier de transcription"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner la transcription", "",
            "Fichiers texte (*.txt *.json)"
        )
        if file:
            self.transcription_file_input.setText(file)

    def _browse_sortie_folder(self):
        """Parcourir le dossier de sortie"""
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionner le dossier de sortie",
            self.sortie_input.text()
        )
        if folder:
            self.sortie_input.setText(folder)

    def _browse_file(self, line_edit):
        """Parcourir un fichier"""
        file, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "",
                                              "Tous les fichiers (*.*)")
        if file:
            line_edit.setText(file)

    def _save_config(self):
        """Sauvegarde la configuration"""
        self.config['elements_sonores']['activer'] = self.enable_sounds_check.isChecked()
        self.config['elements_sonores']['generique_debut']['fichier'] = self.intro_input.text()
        self.config['elements_sonores']['generique_fin']['fichier'] = self.outro_input.text()
        self._log("Configuration sauvegardée")
        self.statusBar().showMessage("Configuration sauvegardée", 3000)

    def _charger_config(self):
        """Charge la configuration"""
        # Gérer le mode PyInstaller
        if getattr(sys, 'frozen', False):
            # Mode exécutable
            base_path = Path(sys._MEIPASS)
        else:
            # Mode développement
            base_path = Path(__file__).parent.parent.parent

        config_path = base_path / 'config' / 'default_config.yaml'

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        # Configuration par défaut si fichier absent
        return {
            'elements_sonores': {
                'activer': False,
                'generique_debut': {'fichier': 'assets/intro.wav'},
                'generique_fin': {'fichier': 'assets/outro.wav'}
            },
            'tri_fichiers': {
                'methode': 'alphabetique',
                'ordre': 'croissant'
            }
        }

    def _log(self, message):
        """Affiche un message dans la console"""
        self.console.append(message)

    def _update_status(self):
        """Met à jour la barre de statut"""
        count = len(self.fichiers_audio)
        if count == 0:
            self.statusBar().showMessage("Aucun fichier sélectionné")
        else:
            self.statusBar().showMessage(f"{count} fichier(s) sélectionné(s)")