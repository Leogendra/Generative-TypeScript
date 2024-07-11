import os, shutil
from utils import create_folder

RAW_FILES_DIR = "./typescript_repos"
CLEANED_FILES_DIR = "./typescript_files"


def get_typescript_files(srcDir, destDir):
    cptCopy = 0
    for root, _dirs, files in os.walk(srcDir):
        for file in files:
            if (file.endswith('.ts')) and (file.count('.') == 1):
                srcFilePath = os.path.join(root, file)
                destFilePath = os.path.join(destDir, file)
                shutil.copy2(srcFilePath, destFilePath)
                cptCopy += 1
                if cptCopy % 100 == 0:
                    print(f"{cptCopy} fichiers copiés", end="\r")
                
    print(f"{cptCopy} fichiers copiés")



if __name__ == "__main__":
    
    create_folder(CLEANED_FILES_DIR)
    get_typescript_files(RAW_FILES_DIR, CLEANED_FILES_DIR)