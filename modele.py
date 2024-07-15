import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel
from utils import *
import numpy as np
import os, json

TYPESCRIPT_FOLDER = "typescript_files/"
TRAINING_PATH = "entrainement/"




def get_model():
    return TFGPT2LMHeadModel.from_pretrained("gpt2")


def get_tokenizer():
    return GPT2Tokenizer.from_pretrained("gpt2")


def check_model():
    return os.path.exists(TRAINING_PATH + "tf_model.h5")


def load_data(directory, nbMaxFiles):
    files_content = [] # On veut garder les fichiers séparés et pas concat
    all_files = os.listdir(directory)
    nbFiles = min(len(all_files), nbMaxFiles)
    nbFile = 1
    for filename in all_files[:nbMaxFiles]:
        if filename.endswith(".ts"):
            if nbFile % 100 == 0:
                print(f"Chargement du fichier {nbFile}/{nbFiles} ({100*nbFile/nbFiles}%)   ", end="\r")
            nbFile += 1
            with open(os.path.join(directory, filename), "r", encoding="utf-8", errors="ignore") as f:
                files_content.append(f.read())
    return files_content


def tokenize_data(tokenizer, dataFolder, nbFiles):
    savePath = f"{TRAINING_PATH}tokenized_data_{nbFiles}.json"
    if os.path.exists(savePath):
        # On récup directement les données tokenisées
        with open(savePath, "r", encoding="utf-8") as f:
            tokenized_data = json.load(f)
        print(f"{GREEN}Données tokenisées chargées depuis : {savePath}{RESET}")
    else:
        # On charge les données, on les tokenise et on les save
        data = load_data(dataFolder, nbFiles)
        tokenized_data = [tokenizer.encode(doc) for doc in data]
        with open(savePath, "w", encoding="utf-8") as f:
            json.dump(tokenized_data, f)
        print(f"{GREEN}Données tokenisées sauvegardées dans : {savePath}{RESET}")

    return tokenized_data


def prepare_training_data(sequences_list, maxlen):
    input_ids = []
    labels = []
    for sequences in sequences_list:
        for i in range(0, len(sequences) - maxlen, maxlen):
            input_ids.append(sequences[i : i + maxlen - 1])
            labels.append(sequences[i + 1 : i + maxlen])
    input_ids = pad_sequences(input_ids, maxlen=maxlen - 1, padding="post")
    labels = pad_sequences(labels, maxlen=maxlen - 1, padding="post")
    return input_ids, labels


def train_model(input_ids, labels, epochs, batch_size):

    model = get_model()

    # On convertit en tenseurs pour que ça marche avec tf
    input_ids = tf.constant(input_ids)
    labels = tf.constant(labels)

    optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)  # par défaut, à tester
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer=optimizer, loss=loss)
    model.fit(input_ids, 
              labels, 
              epochs=epochs, 
              batch_size=batch_size)  # batch_zize=4 pour pas exploser la mémoire
    model.save_pretrained(TRAINING_PATH)

    return model


def evaluate_model(model, tokenizer, inputText, maxLength):
    input_ids = tokenizer.encode(inputText, return_tensors="tf")
    attention_mask = tf.ones_like(input_ids)

    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_length=maxLength,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)




if __name__ == "__main__":

    # Variables
    epochs=1
    batch_size=4
    maxFilesTraining = 1000

    textToGenerate = "function test() {"
    maxTokenNumber = 100 # Comprend l'entree

    # Main
    create_folder(TRAINING_PATH)

    trained_model = get_model()
    tokenizer = get_tokenizer()

    if check_model():
        print(f"{GREEN}Chargement du modèle entraîné.{RESET}")
        trained_model.load_weights(TRAINING_PATH + "tf_model.h5")

    else:
        sequences = tokenize_data(tokenizer, TYPESCRIPT_FOLDER, maxFilesTraining)
        input_ids, labels = prepare_training_data(sequences, maxlen=512)

        print(f"{GREEN}Entraînement du modèle.{RESET}")
        trained_model = train_model(input_ids, labels, epochs, batch_size)

    print(f"{BLUE}Évaluation du modèle...{RESET}")
    generatedText = evaluate_model(trained_model, tokenizer, textToGenerate, maxTokenNumber)

    print(f"\n{YELLOW}Test de génération du modèle :{RESET}")
    print(f"{textToGenerate}{GRAS}{generatedText[len(textToGenerate):]}{RESET}") # gras : texte généré