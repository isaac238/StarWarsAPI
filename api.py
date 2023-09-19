from fastapi import FastAPI
from utils import IO

app = FastAPI()


dataStore = IO("starwars/data.json")
categoryMap = IO("starwars/categories.json")


@app.get("/individuals/{name}")
def getIndividual(name: str):
    data = dataStore.read()
    print(name)
    return data[name.lower()] if name.lower() in data.keys() else None


@app.get("/individuals/category/{category}")
def getIndividualCategory(category: str):
    data = dataStore.read()
    visited = set()
    resultSet = []
    returnArr = []
    resultSet = loadCategoryTree(category, visited)
    for key, value in data.items():
        if set(resultSet).intersection(set(value["categories"])):
            returnArr.append(value)
    return returnArr


def loadCategoryTree(rootCategory, visited, results=[]):
    categories = categoryMap.read()
    rootCategory = rootCategory.lower()

    categoryVisited = rootCategory in visited
    categoryInMap = rootCategory in categories.keys()
    categoryReturned = rootCategory in results
    if categoryVisited or not categoryInMap:
        return

    if not categoryReturned:
        category = categories[rootCategory]
        results.append(category["name"])

    visited.add(rootCategory)
    for key, value in categories.items():
        if value["parent"] is not None:
            if value["parent"].lower() == rootCategory.lower():
                results.append(value["name"])
                loadCategoryTree(key, visited, results)
                return results
