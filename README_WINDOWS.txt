================================================
Podcasteur GUI v1.5.0 - Windows
================================================

INSTALLATION:

1. Extrayez le dossier complet
2. Créez un fichier .env (copiez .env.example)
3. Éditez .env avec votre clé API:
   ANTHROPIC_API_KEY=sk-ant-xxxxx
4. Double-cliquez sur Podcasteur.exe

================================================
PRÉREQUIS:
================================================

✓ Windows 10/11
✓ FFmpeg dans le PATH
✓ Clé API Anthropic (workflow IA)

================================================
LIMITATION VERSION EXÉCUTABLE:
================================================

⚠️  La TRANSCRIPTION n'est pas disponible dans l'exe

Solutions:
- Utilisez "Utiliser transcription existante"
- Générez la transcription via CLI Python:
  1. Installez Python 3.8+
  2. pip install podcasteur
  3. podcasteur auto fichiers/ --duree 5
  4. Utilisez le fichier transcription_timestamps.txt
     généré dans output/

Pour transcription + GUI:
→ Utilisez: python podcasteur_gui.py

================================================
WORKFLOW RECOMMANDÉ (sans transcription):
================================================

1. GÉNÉRATION INITIALE (une fois):
   • Ajoutez vos fichiers audio
   • Cochez "Utiliser fichier mix existant"
   • Lancez → La transcription échouera
   • Utilisez le CLI Python pour transcrire

2. ÉDITIONS SUIVANTES (rapide):
   • Cochez "Utiliser fichier mix existant"
   • Sélectionnez output/mix_complet.wav
   • Cochez "Utiliser transcription existante"
   • Sélectionnez output/transcription_timestamps.txt
   • Lancez → Analyse IA directe

================================================
SUPPORT:
================================================

GitHub: https://github.com/lebidul/podcasteur
Issues: https://github.com/lebidul/podcasteur/issues