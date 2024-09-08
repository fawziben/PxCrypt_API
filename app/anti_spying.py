import os
import re

venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "Lib", "site-packages")

network_keywords = [
    "requests.get", "requests.post", "requests.put", "requests.delete", "requests.patch",
    "urllib.request.urlopen", "http.client.HTTPConnection", "http.client.HTTPSConnection",
    "socket.send", "socket.connect", "socket.create_connection", "socket.socket",
    "subprocess.Popen", "os.system", "shutil.copyfile"
]

libraries_to_check = [
    "fastapi", "sqlalchemy", "fastapi_mail", "pydantic", "starlette", 
    "cryptography", "psycopg2", "jose", "apscheduler", "passlib"
]

def check_file_for_network_calls(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
        for i, line in enumerate(lines, start=1):
            for keyword in network_keywords:
                if re.search(r'\b' + keyword + r'\b', line):
                    return (i, line.strip())
    return None

def scan_libraries_for_spying():
    for library in libraries_to_check:
        library_path = os.path.join(venv_path, library)
        if os.path.exists(library_path):
            print(f"Scanning library: {library}")
            for root, dirs, files in os.walk(library_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        result = check_file_for_network_calls(file_path)
                        if result:
                            line_number, code_snippet = result
                            print(f"Potential spying detected in: {file_path} (Line {line_number})")
                            print(f"Code: {code_snippet}\n")
        else:
            print(f"Library {library} not found in the virtual environment.")

scan_libraries_for_spying()
