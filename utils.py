import os 

RED = "\033[91m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
GRAS = "\033[1m"
RESET = "\033[0m"

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)



if __name__ == "__main__":
    from tensorflow.python.client import device_lib 
    print(device_lib.list_local_devices())