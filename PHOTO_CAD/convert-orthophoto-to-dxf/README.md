# Convert Orthophoto to DXF

Ce projet permet de convertir des orthophotos en fichiers DXF en utilisant des techniques de traitement d'image et de vectorisation. Il gère la lecture des images, la détection des lignes, le snapping des lignes aux angles dominants, et l'écriture des résultats en formats DXF et GeoJSON.

## Structure du projet

```
convert-orthophoto-to-dxf
├── src
│   ├── convert_orthophoto_to_dxf_snapping.py  # Script principal pour la conversion
│   ├── cli.py                                   # Interface en ligne de commande
│   ├── config.py                                # Configuration du projet
│   ├── types.py                                 # Types et interfaces
│   └── core
│       ├── __init__.py                          # Initialisation du module core
│       ├── raster.py                            # Manipulation des images raster
│       ├── vectorize.py                         # Vectorisation des lignes
│       ├── snapping.py                          # Snapping des lignes
│       └── dxf_export.py                        # Exportation au format DXF
├── tests
│   ├── test_raster.py                           # Tests unitaires pour le traitement des images raster
│   ├── test_snapping.py                         # Tests unitaires pour le snapping
│   └── test_dxf_export.py                       # Tests unitaires pour l'exportation DXF
├── examples
│   └── sample_config.yaml                       # Exemple de configuration YAML
├── pyproject.toml                               # Métadonnées du projet
├── requirements.txt                             # Dépendances requises
├── .gitignore                                   # Fichiers à ignorer par Git
├── LICENSE                                      # Informations de licence
└── README.md                                    # Documentation du projet
```

## Installation

Pour installer les dépendances du projet, exécutez la commande suivante :

```
pip install -r requirements.txt
```

## Utilisation

Pour utiliser le script principal, vous pouvez exécuter la commande suivante :

```
python src/convert_orthophoto_to_dxf_snapping.py --input <chemin_vers_image> --output <chemin_vers_fichier_dxf>
```

## Exemples

Un exemple de configuration est fourni dans le fichier `examples/sample_config.yaml`. Vous pouvez l'utiliser comme point de départ pour personnaliser vos paramètres.

## Tests

Des tests unitaires sont fournis dans le répertoire `tests`. Pour exécuter les tests, utilisez :

```
pytest tests/
```

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une demande de tirage pour toute amélioration ou correction de bogue.

## Licence

Ce projet est sous licence MIT. Veuillez consulter le fichier LICENSE pour plus de détails.