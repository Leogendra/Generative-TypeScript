import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel
from utils import *
import numpy as np
import os, json, re, subprocess, random

TRAINING_PATH = "entrainement/"
TSC_PATH = os.path.abspath("node_modules/.bin/tsc.cmd")


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

    # ajouter des } si le code n'est pas terminé
    if inFunction:
        currentFunction += "}" * accoladesCount
        functions.append(currentFunction.strip())

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
            distanceWithGenerated = distance_levenshtein(function[:len(generatedFunction)], generatedFunction) # On crop la fonction de base si jamais on a pas eu assez de tokens
            evaluation_results.append([distanceWithGenerated, len(function), len(generatedFunction)])

        if (treatedFunctions >= nbFiles):
                    break
        
    with open(TRAINING_PATH + "evaluation_greedy_results.json", "w") as file:
        json.dump(evaluation_results, file)

    return [distances/lenGenerated for distances, _, lenGenerated in evaluation_results]


def evaluate_model_syntaxic(model, tokenizer, inputPath, nbFiles, maxLength):

    evaluation_results = []
    create_folder(TRAINING_PATH + "tmp/")
    
    allEvaluateFiles = os.listdir(inputPath)
    random.shuffle(allEvaluateFiles)
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
            if (len(function) > 500):
                continue

            treatedFunctions += 1
            firstLine = "// only this function\n" + function.split("\n")[0].strip()
            print(f"{BLUE}Génération de la fonction {treatedFunctions}/{nbFiles}{RESET}", end="\r")
            generatedFunction = generate(model, tokenizer, firstLine, min(len(firstLine)//2, maxLength))
            cleanedGeneratedFunction = code_cleaner(generatedFunction)[0] # On récupère la première fonction générée
           
            tmpTsFile = os.path.join(TRAINING_PATH + f"tmp/temp_{treatedFunctions}.ts")
            with open(tmpTsFile, "w") as file:
                file.write(cleanedGeneratedFunction)
            
            # On utilise tsc pour vérifier la syntaxe et la sémantique du code
            result = subprocess.run([TSC_PATH, '--noEmit', tmpTsFile], capture_output=True, text=True)
            
            # On compte si y a une erreur ou plus
            errors = 0
            if result.returncode != 0: 
                all_errors = (" " + result.stdout).split("entrainement/temp.ts(")
                for error in all_errors:
                    if (len(error) < 5) or (error.startswith("1,")):
                        continue
                    else:
                        errors += 1

            evaluation_results.append([errors, len(function), len(cleanedGeneratedFunction)])

        if (treatedFunctions >= nbFiles):
                    break
        
    # On sauvagarde les résultats
    with open(TRAINING_PATH + "evaluation_syntaxic_results.json", "w") as file:
        json.dump(evaluation_results, file)

    return [errors for errors, _, _ in evaluation_results]

    




if __name__ == "__main__":

    # Variables
    pathToEvaluateFiles = "typescript_files/"
    nbFilesEvaluating = 50
    maxTokenNumber = 200 # Comprend l'entree
    # evaluation = "greedy"
    evaluation = "syntaxic"

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

    print(f"{BLUE}Évaluation des performances du modèle avec la fonction {evaluation}...{RESET}")

    if evaluation == "greedy":
        evaluate_results = evaluate_model_greedy(trained_model, tokenizer, pathToEvaluateFiles, nbFilesEvaluating, maxTokenNumber)
        moyenne = np.mean(evaluate_results)
        equartType = np.std(evaluate_results)

        print(f"\n{YELLOW}Test d'évaluation du modèle :{RESET}")
        print(f"  Nombre de fonctions évaluées : {nbFilesEvaluating}")
        print(f"  Nombre de tokens maximum : {maxTokenNumber}")
        print(f"  Distance moyenne : {moyenne}")
        print(f"  Ecart-type : {equartType}")
        print(f"  Distance minimale : {min(evaluate_results)}")
        print(f"  Distance maximale : {max(evaluate_results)}")

    elif (evaluation == "syntaxic"):
        evaluate_results = evaluate_model_syntaxic(trained_model, tokenizer, pathToEvaluateFiles, nbFilesEvaluating, maxTokenNumber)
        moyenne = np.mean(evaluate_results)
        equartType = np.std(evaluate_results)

        print(f"\n{YELLOW}Test d'évaluation du modèle :{RESET}")
        print(f"  Nombre de fonctions évaluées : {nbFilesEvaluating}")
        print(f"  Nombre maximum de tokens : {maxTokenNumber}")
        print(f"  Nombre moyen d'erreurs : {moyenne}")
        print(f"  Ecart-type : {equartType}")
        print(f"  Nombre minimal d'erreurs : {min(evaluate_results)}")
        print(f"  Nombre maximal d'erreurs : {max(evaluate_results)}")