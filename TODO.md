# podcasteur
- [x] Avoir banque de sons prédéfinis (exemple générique, virgule, etc..)
- [x] Choix suggestions: choix multiple possible et ajouter: soumettre 1 découpage perso, permettre la possibilité de relancer un prompt à pour qu'iel affine ses suggestions claude api
- [x] Si possible output audacity project (avec le track splitté selon le découpage de sortie) pour pouvoir éditer la sortie dans audacity directement
- [x] Sortie dans dossier sortie/ avec timestamp pour ne pas overwrite ?
- [x] Si c'est utile pour la précision de la réponse de claude api: Transcription avec identification speaker (https://scalastic.io/en/whisper-pyannote-ultimate-speech-transcription/) 
- [x] Fichier timestamp et durée en sortie avec les segments pour connaître où on en est écoutant la sortie : prendre le format de decoupage.json actuel et y ajouter attributs optionnels (début_output,fin_output,durée)
- [x] Workflow semi-automatique qui permet de skip la transcription en fournissant un fichier de transcription
- [x] Proposer fichier concaténé pour éviter l'étape de concaténation
- [ ] GUI
- [ ] Pouvoir ajouter une musique de fond sur des segments
- [ ] Timestamps au dixième de seconde
- [ ] Gérer valeurs de fondu nues dans la config

# GUI
- [x] progression bloquée à 0
- [x] import transcription ou du mix
- [x] rendre découpage séctionné (manuel ou auto) dynamique et pouvoir y inclure (ou enlever) des morceaux  
- [x] découpage personnalisé
- [x] ajouter nom du fichier à l'édition des séquences
- [ ] ton: picklist + 'Autre..'
- [ ] .exe + mac + linux
- [ ] étendre + intégrer onglet config
- [ ] thème clair
- [ ] affichage des suggestions
- [ ] ajouter la possibilité de soumettre le découpage en json
- [ ] workflow manuel