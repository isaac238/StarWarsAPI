import json
import os


# JSON file management class
class IO:
    def __init__(self, name):
        self.name = name
        self.create()

    def store(self, obj, inputData):
        data = self.read()
        if obj.name.lower() not in data.keys():
            data[obj.name.lower()] = inputData
            print(f"Stored: {obj.name}")
        else:
            print(f"Exists: {obj.name}")
        with open(self.name, "w") as f:
            json.dump(data, f, indent=4)

    def read(self):
        self.create()
        with open(self.name, "r") as f:
            data = json.load(f)
        return data

    def create(self):
        dir = self.name.split("/")[0]
        if not os.path.exists(dir):
            os.mkdir(dir)
        with open(self.name, "a+") as f:
            f.seek(0)
            content = f.read()
            if content == "":
                json.dump({}, f, indent=4)
