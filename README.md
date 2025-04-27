# SC Entity Extractor

⚠️ Cet outil a été testé avec Star Citizen 4.1. Il peut cesser de fonctionner avec les versions futures.

Cet outil dépend de [scdatatools](https://gitlab.com/scmodding/frameworks/scdatatools) et d'une version bêta de [cgf-converter](https://github.com/Markemp/Cryengine-Converter/tree/192/new-ivo-format).

# Installation & Utilisation

1. Téléchargez SCEntityExtractor.exe
2. Téléchargez les outils [texconv](https://github.com/microsoft/DirectXTex/releases) et [cgf-converter]() dans un dossier de votre choix
3. Ajoutez ce dossier à votre variable d'environnement PATH
4. Lancez SCEntityExtractor.exe
5. Le premier lancement prendra un peu de temps, mais les lancements suivants seront plus rapides grâce à un système de cache (située dans le dossier .sccache)
6. Sélectionnez l'entité que vous souhaitez extraire
7. Cliquez sur "Exporter", cela enregistrera les fichiers exportés dans un dossier nommé `extract`
8. Vous pouvez cliquer sur le bouton **Installer l'Addon Blender** pour ajouter l'addon d'importation à votre installation de Blender (par défaut Blender 3.5)
9. Une fois l'addon ajouté vous pouvez l'utiliser pour importer le modèle que vous avez extrait. [Video d'exemple](https://youtu.be/0YUl951DTQE?t=197)

Par défaut, l'outil utilisera le chemin `C:/Program Files/Roberts Space Industries/StarCitizen/LIVE` pour le chemin d'installation de Star Citizen, mais vous pouvez le modifier dans le fichier settings.json.

La version par défaut de Blender peut également être configurée dans le fichier settings.json.

Seule la version 3.5 de Blender est actuellement supportée.

# Compilation

Pour compiler l'application à partir des sources, exécutez :
```bash
uv run pyinstaller -F main.py -n SCEntityExtractor
```