from helper_functions.helper_functions import *

print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}--- Payload Decoder ---{bcolors.ENDC}")
print(f"{bcolors.HEADER}{bcolors.BOLD}-----------------------{bcolors.ENDC}")
print()

path = input(f"{bcolors.OKGREEN}{bcolors.BOLD}Enter the path to the payload: {bcolors.ENDC}")

result = []

with open(path, 'r') as payload_file:
    # Reading from json file
    payload_data = json.load(payload_file)

for txn in payload_data['transactions']:
    result.append(decode_data(txn['to'], txn['data'], ETHEREUM))

print()

if result != []:
    json_file_download(result)