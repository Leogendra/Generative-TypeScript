# Modèle de Génération de Code TypeScript

Ce projet utilise un modèle GPT-2 pré-entraîné pour générer du code TypeScript à partir de fichiers TypeScript disponibles sur des projets publics de Github.

## Installation

### Prérequis

- Python 3.9+
- Bibliothèques Python nécessaires : TensorFlow, Transformers, numpy

```bash
pip install -r requirements.txt
```
- Github : Vous devez être connecté à Github sur votre machine pour pouvoir récupérer les fichiers TypeScript.

## Utilisation

### Entraînement du Modèle

1. **Récupération des Données :**
   - Pour récupérer des repositories, lancez `python scraper.py`
   - Vous pouvez définir MAX_REPOS pour le nombre maximum de repos à récupérer, ces derniers se retrouveront dans `typescript_repos/`.
   - Pour filtrer les repos et ne récupérer que les fichiers TypeScript, lancez `python cleaner.py`, les fichiers se retrouveront dans `typescript_files/`.

2. **Entraînement :**
   - Exécutez `python modele.py` pour entraîner le modèle. Assurez-vous de spécifier le nombre maximum de fichiers à utiliser (`MAX_FILES`).
   - ATTENTION : En raison d'un entraînement sur le CPU, l'entraînement peut prendre beaucoup de temps en fonction de la taille du dataset.
   - Le modèle sera entraîné et sauvegardé dans `entrainement/`.

### Génération de code

Une fois le modèle entraîné, vous pouvez générer du code TypeScript en exécutant simplement `python modele.py`. Modifiez la variable textToGenerate pour générer du code à partir de cette chaîne de caractères.

### Évaluation du modèle

Pour évaluer les capacités du modèle entraîné, exécutez `python evaluation.py`. Le modèle générera du code TypeScript à partir de fichiers TypeScript réels et les comparera. Vous pouvez choisir quel type d'évaluation effectuer en modifiant la variable `evaluation` à la ligne 206/207 :
- `evaluation = "greedy"` : Comparaison de la sortie du modèle avec le code réel en fonction de leur distance de Levenshtein.
- `evaluation = "syntaxic"` : Exécution d'une analyse syntaxique sur le code généré pour vérifier sa validité. Veuillez à bien installer TypeScript sur votre machine pour cette évaluation à l'aide de `npm install typescript` (ou `npm install -g typescript` selon si un environnement virtuel est utilisé ou non).

Vous povuez modifier le nombre de fonctions à évaluer en modifiant la variable `nbFilesEvaluating` à la ligne 204, ainsi que le nombre maximal de tokens à générer en modifiant la variable `maxTokenNumber` à la ligne 205.