from bs4 import BeautifulSoup
import json
import requests
import re
import time


# JSON file management class
class IO:
    def __init__(self, name):
        self.name = name
        self.create()

    def store(self, obj, inputData):
        data = self.read()
        if obj.name not in data.keys():
            data[obj.name] = inputData
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


# Class defining each wiki page that is indexed
class WikiEntry:
    def __init__(self, name):
        self.name = name.replace("/Legends", "")
        self.underscoredName = self.name.replace(" ", "_")
        self.data = self.getAllFromWiki()

    def getAllFromWiki(self):
        url = f"https://starwars.fandom.com/wiki/{self.underscoredName}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # Lists all categories the page belongs to
        categoriesTags = soup.find("div",
                                   class_="page-header__categories"
                                   ).find_all("a")
        categories = [category.text for category in categoriesTags if not re.search(r"^\d.more$", category.text)]

        # Finds all the data-sources stored on the wiki (block content e.g. height, gender)
        dataSources = soup.find_all("div", class_="pi-item")

        # Appends additional data to the results dict
        results = {}
        results['name'] = self.name
        results['categories'] = categories
        results['image'] = self.getImage()

        # Appends all the dataSources to the results dictionary
        for dataSource in dataSources:
            sourceName = dataSource["data-source"]
            dataValue = dataSource.find("div", class_="pi-data-value")

            for sup in dataValue.find_all("sup"):
                sup.decompose()

            result = dataValue.text

            if dataValue.find("li"):
                result = []
            for li in dataValue.find_all("li"):
                for ul in li.find_all("ul"):
                    ul.decompose()
                if li.text != '':
                    result.append(li.text)

            results[sourceName] = result

        return results

    def getImage(self):
        url = f"https://starwars.fandom.com/wiki/{self.underscoredName}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        result = soup.find("img", class_="pi-image-thumbnail")

        if result is not None:
            link = result['src']
            link = link.split(".png")[0] + ".png"
            return link

        return None


class Node:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent


visited = set()


def traverseWiki(startingPoint, parentNode=None):
    if startingPoint in visited:
        return
    visited.add(startingPoint)

    if parentNode is None:
        nodeName = startingPoint.replace("/", "").split("Category:")[1]
        parentNode = Node(nodeName, None)

    page = requests.get(startingPoint)
    soup = BeautifulSoup(page.content, "html.parser")

    categories = soup.find_all("a",
                               class_="category-page__member-link",
                               string=re.compile("Category:"))
    links = soup.find_all("a",
                          class_="category-page__member-link",
                          string=re.compile("^(?!Category:).*$"))

    for link in links:
        legendsCheck = link['title'].replace("/Legends", "")
        entry = WikiEntry(legendsCheck)
        disallowedCategories = ["Legends articles", "Non-canon articles"]
        entryCategories = entry.data["categories"]
        if not set(disallowedCategories).intersection(set(entryCategories)):
            dataStore.store(entry, entry.data)

    for category in categories:
        if isinstance(parentNode, Node):
            removeCategoryPrefix = category.text.replace("Category:", "")
            newNode = Node(removeCategoryPrefix, parentNode.name)
            if parentNode.name not in categoryMap.read().keys():
                categoryMap.store(parentNode, parentNode.__dict__)
            categoryMap.store(newNode, newNode.__dict__)

        href = category["href"]
        traverseWiki(f"https://starwars.fandom.com{href}", newNode)


dataStore = IO("data.json")
categoryMap = IO("categories.json")
st = time.time()
traverseWiki("https://starwars.fandom.com/wiki/Category:Informants")
et = time.time()
print(f"{et-st}s")
