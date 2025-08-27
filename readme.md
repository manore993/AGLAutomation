# Étapes pour lancer agldiff.exe

1/ Ouvrir le dossier où se trouve agldiff.exe dans l’Explorateur Windows.

2/ Clic droit dans le dossier 

3/ Selectionner "Ouvrir dans le Terminal Windows" (ou "Ouvrir PowerShell ici").

4/ Dans la nouvelle fenetre, taper la commande suivante (adapter les chemins) :

> .\agldiff.exe --generated_folder 'C:\chemin\vers\gen-messages' --reference_folder 'C:\chemin\vers\ref-messages' --config 'D:\chemin\vers\config.json'

Astuce : vous pouvez glisser-déposer un dossier ou un fichier dans la fenêtre PowerShell, son chemin s’insère automatiquement.