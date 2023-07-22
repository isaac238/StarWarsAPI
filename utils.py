import json


# JSON file management class
class IO:
    def __init__(self, name):
        self.name = name
        self.create()

    def store(self, obj, inputData):
        data = self.read()
        if obj.name not in data.keys():
            data[obj.name.lower()] = inputData
        with open(self.name, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Stored: {obj.name}")

    def read(self):
        self.create()
        with open(self.name, "r") as f:
            data = json.load(f)
        return data

    def create(self):
        with open(self.name, "a+") as f:
            f.seek(0)
            content = f.read()
            if content == "":
                json.dump({}, f, indent=4)
