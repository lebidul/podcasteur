"""
Interface en ligne de commande (CLI) pour Podcasteur
"""

import click
import yaml
from pathlib import Path
from typing import Optional, List
import os
from dotenv import load_dotenv

from .editor import PodcastEditor
from .decoupage import Decoupage


# Charger les variables d'environnement
load_dotenv()


def _collecter_fichiers_audio(entrees: tuple) -> List[Path]:
    """
    Collecte les fichiers audio depuis une liste de chemins (fichiers ou dossiers)

    Args:
        entrees: Tuple de chemins (fichiers ou dossiers)

    Returns:
        Liste de Path vers les fichiers audio
    """
    fichiers_audio = []
    extensions_audio = {'.wav', '.mp3', '.ogg', '.flac', '.m4a', '.aac', '.wma', '.opus'}

    for entree in entrees:
        chemin = Path(entree)

        if chemin.is_file():
            # C'est un fichier, vérifier si c'est un fichier audio
            if chemin.suffix.lower() in extensions_audio:
                fichiers_audio.append(chemin)
            else:
                click.echo(f"⚠️  Ignoré (pas un fichier audio) : {chemin.name}", err=True)

        elif chemin.is_dir():
            # C'est un dossier, récupérer tous les fichiers audio
            click.echo(f"📁 Analyse du dossier : {chemin}")
            trouves = []
            for ext in extensions_audio:
                trouves.extend(chemin.glob(f'*{ext}'))

            if trouves:
                click.echo(f"   Trouvé {len(trouves)} fichier(s) audio")
                fichiers_audio.extend(trouves)
            else:
                click.echo(f"   ⚠️  Aucun fichier audio trouvé dans ce dossier", err=True)

        else:
            click.echo(f"❌ Chemin invalide : {entree}", err=True)

    return fichiers_audio


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🎙️ Podcasteur - Éditeur de podcasts automatisé

    Deux workflows disponibles :
    - AUTO : Transcription + IA pour suggestions automatiques
    - MANUEL : Découpage prédéfini dans un fichier JSON
    """
    pass


@cli.command()
@click.argument('entrees', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '--sortie', '-o',
    type=click.Path(),
    default='sortie',
    help='Dossier de sortie'
)
@click.option(
    '--duree', '-d',
    type=int,
    help='Durée cible en minutes'
)
@click.option(
    '--ton', '-t',
    type=str,
    help='Ton souhaité (ex: "informatif et dynamique")'
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Fichier de configuration personnalisé'
)
def auto(entrees, sortie, duree, ton, config):
    """
    Workflow automatique : transcription + analyse IA

    ENTREES peut être :
    - Des fichiers audio : fichier1.wav fichier2.mp3
    - Un dossier contenant des fichiers audio : dossier_audio/
    - Un mélange des deux

    Exemples :

      podcasteur auto fichier1.wav fichier2.wav --duree 5

      podcasteur auto dossier_audio/ --duree 5 --ton "dynamique"

      podcasteur auto audio/*.wav --duree 3
    """
    click.echo("\n🎙️ Podcasteur - Workflow Automatique\n")

    # Collecter tous les fichiers audio
    fichiers_path = _collecter_fichiers_audio(entrees)

    if not fichiers_path:
        click.echo("❌ Erreur : Aucun fichier audio trouvé")
        click.echo("\nFormats supportés : WAV, MP3, OGG, FLAC, M4A, AAC, WMA, OPUS")
        return

    # Afficher les fichiers à traiter
    click.echo(f"\n📋 Fichiers à traiter ({len(fichiers_path)}) :")
    for i, f in enumerate(fichiers_path, 1):
        click.echo(f"   {i}. {f.name}")
    click.echo()

    # Charger la configuration
    config_dict = _charger_config(config)

    # Vérifier la clé API
    cle_api = os.getenv('ANTHROPIC_API_KEY')
    if not cle_api:
        click.echo("❌ Erreur : Clé API Anthropic manquante")
        click.echo("   Définissez ANTHROPIC_API_KEY dans votre fichier .env")
        click.echo("   ou comme variable d'environnement")
        click.echo("\n💡 Obtenez votre clé sur : https://console.anthropic.com")
        return

    dossier_sortie = Path(sortie)

    # Créer l'éditeur
    editor = PodcastEditor(config_dict, cle_api)

    try:
        # Lancer le workflow
        fichier_final = editor.workflow_automatique(
            fichiers_path,
            dossier_sortie,
            duree_cible=duree,
            ton=ton
        )

        click.echo(f"\n✅ Succès ! Podcast créé : {fichier_final}")

    except Exception as e:
        click.echo(f"\n❌ Erreur : {e}")
        if os.getenv('DEBUG'):
            raise


@cli.command()
@click.argument('decoupage', type=click.Path(exists=True))
@click.argument('source', type=click.Path(exists=True))
@click.option(
    '--sortie', '-o',
    type=click.Path(),
    default='sortie',
    help='Dossier de sortie'
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Fichier de configuration personnalisé'
)
def manuel(decoupage, source, sortie, config):
    """
    Workflow manuel : découpage prédéfini

    Exemple :
        podcasteur manuel decoupage.json dossier_audio/ --sortie sortie/
    """
    click.echo("\n🎙️ Podcasteur - Workflow Manuel\n")

    # Charger la configuration
    config_dict = _charger_config(config)

    # Convertir en Path
    fichier_decoupage = Path(decoupage)
    dossier_source = Path(source)
    dossier_sortie = Path(sortie)

    # Vérifier que source est un dossier
    if not dossier_source.is_dir():
        click.echo(f"❌ Erreur : {source} n'est pas un dossier")
        return

    # Créer l'éditeur (pas besoin de clé API)
    editor = PodcastEditor(config_dict)

    try:
        # Lancer le workflow
        fichier_final = editor.workflow_manuel(
            fichier_decoupage,
            dossier_source,
            dossier_sortie
        )

        if fichier_final:
            click.echo(f"\n✅ Succès ! Podcast créé : {fichier_final}")

    except Exception as e:
        click.echo(f"\n❌ Erreur : {e}")
        if os.getenv('DEBUG'):
            raise


@cli.command()
@click.argument('sortie', type=click.Path())
def exemple(sortie):
    """
    Crée un fichier de découpage d'exemple

    Exemple :
        podcasteur exemple mon_decoupage.json
    """
    chemin_sortie = Path(sortie)

    # Utiliser une config minimale pour le gestionnaire de découpage
    config_minimal = {'validation': {}}
    manager = Decoupage(config_minimal)

    manager.creer_exemple(chemin_sortie, avec_commentaires=True)

    click.echo(f"\n✅ Fichier d'exemple créé : {chemin_sortie}")
    click.echo("\nVous pouvez maintenant éditer ce fichier et utiliser :")
    click.echo(f"  podcasteur manuel {chemin_sortie} dossier_audio/")


@cli.command()
@click.option(
    '--sortie', '-o',
    type=click.Path(),
    default='config/ma_config.yaml',
    help='Chemin du fichier de configuration'
)
def init_config(sortie):
    """
    Crée un fichier de configuration par défaut

    Exemple :
        podcasteur init-config --sortie ma_config.yaml
    """
    chemin_sortie = Path(sortie)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    # Charger la config par défaut
    config_defaut = _charger_config(None)

    # Sauvegarder
    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        yaml.dump(config_defaut, f, allow_unicode=True, sort_keys=False)

    click.echo(f"\n✅ Configuration créée : {chemin_sortie}")
    click.echo("\nÉditez ce fichier pour personnaliser les paramètres.")


@cli.command()
def info():
    """
    Affiche les informations sur Podcasteur
    """
    click.echo("""
🎙️ Podcasteur v1.0.0

Un éditeur de podcasts automatisé qui utilise l'IA pour suggérer
les meilleurs découpages de vos enregistrements audio.

📦 Deux workflows :
  • AUTO   : Transcription + suggestions IA (nécessite clé API Anthropic)
  • MANUEL : Découpage prédéfini dans un fichier JSON

🔧 Commandes disponibles :
  • auto          : Workflow automatique
  • manuel        : Workflow manuel
  • exemple       : Créer un fichier de découpage d'exemple
  • init-config   : Créer un fichier de configuration
  • info          : Afficher ces informations

📚 Documentation complète :
  https://github.com/lebidul/podcasteur

💡 Exemples d'utilisation :
  
  Workflow automatique :
    podcasteur auto *.wav --duree 5 --ton "dynamique"
    podcasteur auto dossier_audio/ --duree 5
  
  Workflow manuel :
    podcasteur exemple decoupage.json
    podcasteur manuel decoupage.json audio/ --sortie sortie/
  
  Configuration personnalisée :
    podcasteur init-config --sortie ma_config.yaml
    podcasteur auto *.wav --config ma_config.yaml

🔑 Configuration de la clé API :
  
  Créez un fichier .env à la racine du projet :
    ANTHROPIC_API_KEY=votre_cle_api_ici
  
  Ou définissez la variable d'environnement :
    set ANTHROPIC_API_KEY=votre_cle_api_ici    (Windows CMD)
    $env:ANTHROPIC_API_KEY="votre_cle_api_ici" (PowerShell)
    export ANTHROPIC_API_KEY=votre_cle_api_ici (Linux/Mac)

🎨 Formats audio supportés :
  Entrée : WAV, MP3, OGG, FLAC, M4A, AAC, WMA, OPUS
  Sortie : MP3, WAV, OGG
""")


def _charger_config(chemin_config: Optional[str]) -> dict:
    """Charge la configuration depuis un fichier ou utilise la config par défaut"""
    if chemin_config:
        with open(chemin_config, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        # Charger la config par défaut
        config_defaut_path = Path(__file__).parent.parent / 'config' / 'default_config.yaml'
        if config_defaut_path.exists():
            with open(config_defaut_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Config minimale en fallback
            return {
                'audio': {
                    'format_export': 'mp3',
                    'debit': '192k',
                    'duree_fondu': 500,
                    'silence_entre_segments': 1000,
                    'normaliser': True
                },
                'transcription': {
                    'modele': 'base',
                    'langue': 'fr',
                    'dossier_sortie': 'transcriptions'
                },
                'analyse_ia': {
                    'modele': 'claude-sonnet-4-5-20250929',
                    'duree_cible': 5,
                    'ton': 'informatif et dynamique',
                    'nombre_suggestions': 3,
                    'temperature': 0.7
                },
                'tri_fichiers': {
                    'methode': 'nom',
                    'ordre': 'asc'
                },
                'validation': {
                    'verifier_timestamps': True,
                    'tolerance_timestamps': 0.5
                }
            }


if __name__ == '__main__':
    cli()