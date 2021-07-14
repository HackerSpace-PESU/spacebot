import os

with open(".env") as f:
    lines = f.read().strip().split('\n')
    for line in lines:
        os.system(f"heroku config:set {line}")