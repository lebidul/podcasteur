"""
Fenêtre principale avec workflow automatique complet
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFileDialog,
    QListWidget, QSpinBox, QLineEdit, QTextEdit,
    QProgressBar, QCheckBox, QGroupBox, QMessageBox,
    QComboBox, QDoubleSpinBox
)
from PyQt6.QtGui import QPalette, QColor
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

        # Ajouter l'icône
        icon_path = self._get_icon_path()
        if icon_path and icon_path.exists():
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(icon_path)))

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
        self.ton_combo = QComboBox()
        self.ton_combo.addItems([
            "informatif et dynamique",  # ← Défaut
            "détendu et conversationnel",
            "professionnel et concis",
            "créatif et narratif"
        ])

        ton_layout.addWidget(self.ton_combo)
        options_layout.addLayout(ton_layout)

        # Nombre de suggestions
        suggestions_layout = QHBoxLayout()
        suggestions_layout.addWidget(QLabel("Nombre de suggestions :"))
        self.suggestions_spin = QSpinBox()
        self.suggestions_spin.setMinimum(1)
        self.suggestions_spin.setMaximum(5)
        self.suggestions_spin.setValue(self.config.get('analyse_ia', {}).get('nombre_suggestions', 3))
        suggestions_layout.addWidget(self.suggestions_spin)
        suggestions_layout.addStretch()
        options_layout.addLayout(suggestions_layout)

        # Format d'export
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format d'export :"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['mp3', 'wav', 'flac'])
        format_actuel = self.config.get('audio', {}).get('format_export', 'mp3')
        self.format_combo.setCurrentText(format_actuel)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)

        # Qualité audio (seulement pour MP3)
        qualite_layout = QHBoxLayout()
        qualite_layout.addWidget(QLabel("Qualité audio (MP3) :"))
        self.qualite_combo = QComboBox()
        self.qualite_combo.addItems(['128k', '192k', '256k', '320k'])
        debit_actuel = self.config.get('audio', {}).get('debit', '192k')
        self.qualite_combo.setCurrentText(debit_actuel)
        qualite_layout.addWidget(self.qualite_combo)
        qualite_layout.addStretch()
        options_layout.addLayout(qualite_layout)

        # Connecter le changement de format pour activer/désactiver qualité
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        self._on_format_changed(self.format_combo.currentText())  # Init

        # Normalisation audio
        self.normalize_check = QCheckBox("Normaliser l'audio")
        self.normalize_check.setChecked(self.config.get('audio', {}).get('normaliser', True))
        options_layout.addWidget(self.normalize_check)

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

        # === SECTION AUDIO ===
        audio_group = QGroupBox("Paramètres audio")
        audio_layout = QVBoxLayout()

        # Durée des fondus
        fondu_layout = QHBoxLayout()
        fondu_layout.addWidget(QLabel("Durée des fondus (ms) :"))
        self.fondu_spin = QSpinBox()
        self.fondu_spin.setMinimum(0)
        self.fondu_spin.setMaximum(5000)
        self.fondu_spin.setSingleStep(100)
        self.fondu_spin.setValue(self.config.get('audio', {}).get('duree_fondu', 1000))
        fondu_layout.addWidget(self.fondu_spin)
        fondu_layout.addStretch()
        audio_layout.addLayout(fondu_layout)

        # Silence entre segments
        silence_layout = QHBoxLayout()
        silence_layout.addWidget(QLabel("Silence entre segments (ms) :"))
        self.silence_spin = QSpinBox()
        self.silence_spin.setMinimum(0)
        self.silence_spin.setMaximum(5000)
        self.silence_spin.setSingleStep(100)
        self.silence_spin.setValue(self.config.get('audio', {}).get('silence_entre_segments', 1000))
        silence_layout.addWidget(self.silence_spin)
        silence_layout.addStretch()
        audio_layout.addLayout(silence_layout)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # === SECTION ÉLÉMENTS SONORES ===
        sound_group = QGroupBox("Éléments sonores")
        sound_layout = QVBoxLayout()

        self.enable_sounds_check = QCheckBox("Activer intro/outro")
        self.enable_sounds_check.setChecked(
            self.config.get('elements_sonores', {}).get('activer', False)
        )
        sound_layout.addWidget(self.enable_sounds_check)

        # Intro
        intro_layout = QHBoxLayout()
        intro_layout.addWidget(QLabel("Intro :"))
        self.intro_input = QLineEdit(
            self.config.get('elements_sonores', {}).get('generique_debut', {}).get('fichier', 'assets/intro.wav')
        )
        btn_intro = QPushButton("Parcourir")
        btn_intro.clicked.connect(lambda: self._browse_file(self.intro_input))
        intro_layout.addWidget(self.intro_input)
        intro_layout.addWidget(btn_intro)
        sound_layout.addLayout(intro_layout)

        # Volume intro
        intro_vol_layout = QHBoxLayout()
        intro_vol_layout.addWidget(QLabel("Volume intro (0.0 - 1.0) :"))
        self.intro_volume_spin = QDoubleSpinBox()
        self.intro_volume_spin.setMinimum(0.0)
        self.intro_volume_spin.setMaximum(1.0)
        self.intro_volume_spin.setSingleStep(0.1)
        self.intro_volume_spin.setValue(
            self.config.get('elements_sonores', {}).get('generique_debut', {}).get('volume', 0.8)
        )
        intro_vol_layout.addWidget(self.intro_volume_spin)
        intro_vol_layout.addStretch()
        sound_layout.addLayout(intro_vol_layout)

        # Outro
        outro_layout = QHBoxLayout()
        outro_layout.addWidget(QLabel("Outro :"))
        self.outro_input = QLineEdit(
            self.config.get('elements_sonores', {}).get('generique_fin', {}).get('fichier', 'assets/outro.wav')
        )
        btn_outro = QPushButton("Parcourir")
        btn_outro.clicked.connect(lambda: self._browse_file(self.outro_input))
        outro_layout.addWidget(self.outro_input)
        outro_layout.addWidget(btn_outro)
        sound_layout.addLayout(outro_layout)

        # Volume outro
        outro_vol_layout = QHBoxLayout()
        outro_vol_layout.addWidget(QLabel("Volume outro (0.0 - 1.0) :"))
        self.outro_volume_spin = QDoubleSpinBox()
        self.outro_volume_spin.setMinimum(0.0)
        self.outro_volume_spin.setMaximum(1.0)
        self.outro_volume_spin.setSingleStep(0.1)
        self.outro_volume_spin.setValue(
            self.config.get('elements_sonores', {}).get('generique_fin', {}).get('volume', 0.8)
        )
        outro_vol_layout.addWidget(self.outro_volume_spin)
        outro_vol_layout.addStretch()
        sound_layout.addLayout(outro_vol_layout)

        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)

        # === SECTION TRI FICHIERS ===
        tri_group = QGroupBox("Tri des fichiers audio")
        tri_layout = QVBoxLayout()

        # Méthode de tri
        methode_layout = QHBoxLayout()
        methode_layout.addWidget(QLabel("Méthode de tri :"))
        self.tri_methode_combo = QComboBox()
        self.tri_methode_combo.addItems(['alphabetique', 'date'])
        methode_actuelle = self.config.get('tri_fichiers', {}).get('methode', 'alphabetique')
        # Mapper "nom" -> "alphabetique" pour compatibilité
        if methode_actuelle == 'nom':
            methode_actuelle = 'alphabetique'
        self.tri_methode_combo.setCurrentText(methode_actuelle)
        methode_layout.addWidget(self.tri_methode_combo)
        methode_layout.addStretch()
        tri_layout.addLayout(methode_layout)

        # Ordre de tri
        ordre_layout = QHBoxLayout()
        ordre_layout.addWidget(QLabel("Ordre de tri :"))
        self.tri_ordre_combo = QComboBox()
        self.tri_ordre_combo.addItems(['croissant', 'decroissant'])
        ordre_actuel = self.config.get('tri_fichiers', {}).get('ordre', 'croissant')
        # Mapper "asc"/"desc" pour compatibilité
        if ordre_actuel == 'asc':
            ordre_actuel = 'croissant'
        elif ordre_actuel == 'desc':
            ordre_actuel = 'decroissant'
        self.tri_ordre_combo.setCurrentText(ordre_actuel)
        ordre_layout.addWidget(self.tri_ordre_combo)
        ordre_layout.addStretch()
        tri_layout.addLayout(ordre_layout)

        tri_group.setLayout(tri_layout)
        layout.addWidget(tri_group)

        # === SECTION IA ===
        ia_group = QGroupBox("Paramètres d'analyse IA")
        ia_layout = QVBoxLayout()

        # Modèle Claude
        modele_layout = QHBoxLayout()
        modele_layout.addWidget(QLabel("Modèle Claude :"))
        self.modele_input = QLineEdit(
            self.config.get('analyse_ia', {}).get('modele', 'claude-sonnet-4-5-20250929')
        )
        self.modele_input.setPlaceholderText("claude-sonnet-4-5-20250929")
        modele_layout.addWidget(self.modele_input)
        ia_layout.addLayout(modele_layout)

        # Température
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Température (0.0 - 1.0) :"))
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setMinimum(0.0)
        self.temperature_spin.setMaximum(1.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(
            self.config.get('analyse_ia', {}).get('temperature', 0.7)
        )
        temp_layout.addWidget(self.temperature_spin)
        temp_layout.addStretch()
        ia_layout.addLayout(temp_layout)

        ia_group.setLayout(ia_layout)
        layout.addWidget(ia_group)

        # Bouton sauvegarder
        btn_save = QPushButton("💾 Sauvegarder la configuration")
        btn_save.setStyleSheet("padding: 8px; font-weight: bold;")
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

        self._update_config_from_ui()

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

        # Mapper les valeurs GUI vers les valeurs attendues par audio_processor
        methode_map = {'alphabetique': 'nom', 'date': 'date'}
        ordre_map = {'croissant': 'asc', 'decroissant': 'desc'}

        methode = methode_map.get(self.config['tri_fichiers']['methode'], 'nom')
        ordre = ordre_map.get(self.config['tri_fichiers']['ordre'], 'asc')

        self.concat_worker = ConcatWorker(
            processor,
            self.fichiers_audio,
            fichier_mix,
            methode_tri=methode,
            ordre_tri=ordre
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
            import re

            with open(chemin_trans, 'r', encoding='utf-8') as f:
                if chemin_trans.suffix == '.json':
                    import json
                    self.transcription = json.load(f)
                else:
                    # Format texte avec timestamps : [MM:SS - MM:SS] texte
                    contenu = f.read()

                    # Parser le format timestamps
                    segments = []
                    texte_complet = []

                    # Regex pour capturer [MM:SS - MM:SS] [SPEAKER] texte
                    pattern = r'\[(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\]\s*(?:\[([^\]]+)\]\s*)?(.*)'

                    for ligne in contenu.strip().split('\n'):
                        match = re.match(pattern, ligne)
                        if match:
                            debut_min, debut_sec, fin_min, fin_sec, speaker, texte = match.groups()

                            debut = int(debut_min) * 60 + int(debut_sec)
                            fin = int(fin_min) * 60 + int(fin_sec)
                            texte = texte.strip()

                            segment = {
                                'debut': float(debut),
                                'fin': float(fin),
                                'texte': texte
                            }

                            # Ajouter speaker si présent
                            if speaker:
                                segment['speaker'] = speaker

                            segments.append(segment)
                            texte_complet.append(texte)

                    self.transcription = {
                        'texte': ' '.join(texte_complet),
                        'langue': 'fr',
                        'segments': segments
                    }

            # Vérification
            nb_segments = len(self.transcription.get('segments', []))
            nb_chars = len(self.transcription.get('texte', ''))

            self._log(f"✅ Transcription chargée")
            self._log(f"   📊 {nb_segments} segments")
            self._log(f"   📝 {nb_chars} caractères")

            if nb_segments == 0:
                raise ValueError("Aucun segment trouvé dans la transcription")

            self._start_ai_analysis()

        except Exception as e:
            self._on_error(f"Erreur chargement transcription : {e}")

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

        self._log("\n📝 ÉTAPE 2/4 : Transcription")

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

        print(f"🔍 DEBUG transcription reçue:")
        print(f"   - Clés: {transcription.keys()}")
        print(f"   - Texte: {len(transcription.get('texte', ''))} caractères")
        print(f"   - Segments: {len(transcription.get('segments', []))} segments")

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
            ton=self.ton_combo.currentText(),
            nombre_suggestions=self.suggestions_spin.value()  # ← AJOUTER
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

    def _on_format_changed(self, format_str):
        """Active/désactive les options de qualité selon le format"""
        self.qualite_combo.setEnabled(format_str == 'mp3')

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

    # Ajouter cette méthode helper dans la classe MainWindow
    def _get_icon_path(self):
        """Retourne le chemin de l'icône selon le contexte"""
        if getattr(sys, 'frozen', False):
            # Mode exécutable PyInstaller
            base_path = Path(sys._MEIPASS)
        else:
            # Mode développement
            base_path = Path(__file__).parent.parent.parent

        return base_path / 'assets' / 'icon.ico'

    def _save_config(self):
        """Sauvegarde la configuration"""
        # Audio
        self.config['audio']['duree_fondu'] = self.fondu_spin.value()
        self.config['audio']['silence_entre_segments'] = self.silence_spin.value()

        # Éléments sonores
        self.config['elements_sonores']['activer'] = self.enable_sounds_check.isChecked()
        self.config['elements_sonores']['generique_debut']['fichier'] = self.intro_input.text()
        self.config['elements_sonores']['generique_debut']['volume'] = self.intro_volume_spin.value()
        self.config['elements_sonores']['generique_fin']['fichier'] = self.outro_input.text()
        self.config['elements_sonores']['generique_fin']['volume'] = self.outro_volume_spin.value()

        # Tri fichiers
        self.config['tri_fichiers']['methode'] = self.tri_methode_combo.currentText()
        self.config['tri_fichiers']['ordre'] = self.tri_ordre_combo.currentText()

        # IA
        self.config['analyse_ia']['modele'] = self.modele_input.text()
        self.config['analyse_ia']['temperature'] = self.temperature_spin.value()

        self._log("✅ Configuration sauvegardée")
        self.statusBar().showMessage("Configuration sauvegardée", 3000)

        QMessageBox.information(
            self,
            "Configuration sauvegardée",
            "Les modifications seront appliquées au prochain lancement du workflow.\n\n"
            "Note : Pour persister ces changements, modifiez config/default_config.yaml"
        )

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
                config = yaml.safe_load(f)
        else:
            # Configuration par défaut
            config = {
                'elements_sonores': {
                    'activer': False,
                    'generique_debut': {'fichier': 'assets/intro.wav', 'volume': 0.8},
                    'generique_fin': {'fichier': 'assets/outro.wav', 'volume': 0.8}
                },
                'tri_fichiers': {
                    'methode': 'alphabetique',
                    'ordre': 'croissant'
                },
                'audio': {
                    'duree_fondu': 1000,
                    'silence_entre_segments': 1000,
                    'normaliser': True,
                    'format_export': 'mp3',
                    'debit': '192k'
                }
            }

        # Résoudre et vérifier TOUS les chemins relatifs dans elements_sonores
        if 'elements_sonores' in config:
            elements_ok = True

            for key in ['generique_debut', 'generique_fin']:
                if key in config['elements_sonores']:
                    fichier = config['elements_sonores'][key].get('fichier', '')

                    if fichier:
                        chemin_fichier = Path(fichier)

                        # Si chemin relatif, le résoudre depuis base_path
                        if not chemin_fichier.is_absolute():
                            chemin_absolu = base_path / fichier
                            config['elements_sonores'][key]['fichier'] = str(chemin_absolu)

                            # Vérifier l'existence
                            if not chemin_absolu.exists():
                                elements_ok = False

            # Si un fichier manque, désactiver automatiquement les éléments sonores
            if not elements_ok:
                config['elements_sonores']['activer'] = False

        return config

    def _update_config_from_ui(self):
        """Met à jour la config avec les valeurs de l'interface avant le workflow"""
        # Format d'export et qualité
        self.config['audio']['format_export'] = self.format_combo.currentText()
        self.config['audio']['debit'] = self.qualite_combo.currentText()
        self.config['audio']['normaliser'] = self.normalize_check.isChecked()

        # Nombre de suggestions IA
        if hasattr(self, 'suggestions_spin'):
            self.config['analyse_ia']['nombre_suggestions'] = self.suggestions_spin.value()

        # Ton (si modifié dans l'onglet config)
        self.config['analyse_ia']['ton'] = self.ton_combo.currentText()

        self._log(f"⚙️  Configuration appliquée : {self.format_combo.currentText().upper()}")
        if self.format_combo.currentText() == 'mp3':
            self._log(f"   Qualité : {self.qualite_combo.currentText()}")
        self._log(f"   Normalisation : {'OUI' if self.normalize_check.isChecked() else 'NON'}")

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