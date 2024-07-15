import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel
from utils import *
import numpy as np
import os, json, re

TRAINING_PATH = "entrainement/"


def get_model():
    return TFGPT2LMHeadModel.from_pretrained("gpt2")


def get_tokenizer():
    return GPT2Tokenizer.from_pretrained("gpt2")


def check_model():
    return os.path.exists(TRAINING_PATH + "tf_model.h5")


def code_cleaner(code):
    code = re.sub(r"//.*", "", code) # commentaires inligne
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL) # commentaires multi
    code = re.sub(r"\n\n", "\n", code) # double retours chariots

    # récupérer les fonctions
    lines = code.split("\n")
    functions = []
    currentFunction = ""
    inFunction = False
    accoladesCount = 0
    
    for line in lines:
        
        strippedLine = line.strip()

        # Début d'une fonction
        if strippedLine.startswith("function") or strippedLine.startswith("async function"):
            inFunction = True
            line = strippedLine
        
        # Si on est dans une fonction on ajoute la ligne actuelle
        if inFunction:
            currentFunction += line + '\n'
            accoladesCount += line.count('{')
            accoladesCount -= line.count('}')
            
            # Fin de la fonction
            if accoladesCount == 0:
                functions.append(currentFunction.strip())
                inFunction = False
                currentFunction = ""

    return functions


# GPT
def distance_levenshtein(s1, s2):
    n, m = len(s1), len(s2)
    if n > m:
        s1, s2 = s2, s1
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (s1[j - 1] != s2[i - 1])
            current_row[j] = min(insertions, deletions, substitutions)
    return current_row[n]


def generate(model, tokenizer, inputText, maxLength):
    input_ids = tokenizer.encode(inputText, return_tensors="tf")
    attention_mask = tf.ones_like(input_ids)

    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_length=maxLength,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
        # do_sample=True, # à faire varier pour améliorer l'évaluation
        # temperature=0.7,
        # top_k=50,
        # top_p=0.95,
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)


def evaluate_model_greedy(model, tokenizer, inputPath, nbFiles, maxLength):

    evaluation_results = []
    
    allEvaluateFiles = os.listdir(inputPath)
    treatedFunctions = 0
    for file in allEvaluateFiles:
        with open(inputPath + file, "r") as file:
            fileText = file.read()
            cleanedCode = code_cleaner(fileText)

        # on récupère toutes les fonctions du fichier et on les génère avec notre modèle
        for function in cleanedCode:
            if (treatedFunctions >= nbFiles):
                break
            if ("foo" in function):
                continue
            if (len(function) < 10):
                continue

            treatedFunctions += 1
            firstLine = function.split("\n")[0]
            print(f"{BLUE}Génération de la fonction {treatedFunctions}/{nbFiles}{RESET}", end="\r")
            generatedFunction = generate(model, tokenizer, firstLine, maxLength)
            distanceWithGenerated = distance_levenshtein(function[:len(generatedFunction)], generatedFunction) #On crop la fonction de base si jamais on a pas eu assez de tokens
            evaluation_results.append([distanceWithGenerated, len(function), len(generatedFunction)])

        if (treatedFunctions >= nbFiles):
                    break
        
    with open(TRAINING_PATH + "evaluation_results.json", "w") as file:
        json.dump(evaluation_results, file)

    return [distances/lenGenerated for distances, _, lenGenerated in evaluation_results]




if __name__ == "__main__":

    # Variables
    pathToEvaluateFiles = "typescript_files/"
    nbFilesEvaluating = 10
    maxTokenNumber = 100 # Comprend l'entree

    # Main
    create_folder(TRAINING_PATH)
    create_folder(pathToEvaluateFiles)

    trained_model = get_model()
    tokenizer = get_tokenizer()

    if check_model():
        print(f"{GREEN}Chargement du modèle entraîné.{RESET}")
        trained_model.load_weights(TRAINING_PATH + "tf_model.h5")

    else:
        print(f"{RED}Le modèle n'est pas présent dans entrainement/{RESET}")

    print(f"{BLUE}Évaluation des performances du modèle...{RESET}")
    evaluate_results = evaluate_model_greedy(trained_model, tokenizer, pathToEvaluateFiles, nbFilesEvaluating, maxTokenNumber)
    moyenne = np.mean(evaluate_results)
    equartType = np.std(evaluate_results)

    print(f"\n{YELLOW}Test d'évaluation du modèle :{RESET}")
    print(f"  Nombre de fichiers évalués : {nbFilesEvaluating}")
    print(f"  Nombre de tokens maximum : {maxTokenNumber}")
    print(f"  Distance moyenne : {moyenne}")
    print(f"  Ecart-type : {equartType}")
    print(f"  Distance minimale : {min(evaluate_results)}")
    print(f"  Distance maximale : {max(evaluate_results)}")