import os

def remove_rpyc(root_dir: str):
    for root, _, files in os.walk(root_dir):
        for name in files:
            if name.endswith(".rpyc"):
                path = os.path.join(root, name)
                try:
                    os.remove(path)
                    print(f"remove: {path}")
                except OSError:
                    print(f"error remove: {path}")

remove_rpyc(".")

