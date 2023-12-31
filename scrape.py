from bs4 import BeautifulSoup
from utils import IO
import requests
import re
import time


class Wiki:
    def __init__(self, url):
        self.url = self.validate_url(url)
        self.name = self.get_name(url)
        print(self.name)
        self.dataStore = IO(f"{self.name}/data.json")
        self.categoryMap = IO(f"{self.name}/categories.json")

    def get_name(self, url):
        name = url.replace("https://", "")
        name = name.replace("www.", "")
        print(name)
        name = name.split(".")[0]
        return name

    def validate_url(self, url):
        regexString = r"^(https:\/\/)(www\.)?.*.(fandom.com)(\/\w+)?(\/)?"
        if re.search(regexString, url):
            url = url[:-1] if url[-1] == "/" else url
            return url
        return None

    def create_new_node(self, category, parentNode):
        if isinstance(parentNode, Node):
            removeCategoryPrefix = category.text.replace("Category:", "")
            newNode = Node(removeCategoryPrefix, parentNode.name)
            if parentNode.name.lower() not in self.categoryMap.read().keys():
                self.categoryMap.store(parentNode, parentNode.__dict__)
            self.categoryMap.store(newNode, newNode.__dict__)
            return newNode

    def store_link(self, link):
        if '/Legends' in link['title']:
            return
        entry = WikiEntry(link['title'], self)
        disallowedCategories = ["Legends articles", "Non-canon articles"]
        entryCategories = entry.data["categories"]
        hasDisallowedCategory = set(disallowedCategories).intersection(set(entryCategories))
        if not hasDisallowedCategory:
            self.dataStore.store(entry, entry.data)

    def create_parent_node(self, rootNode):
        nodeName = rootNode.replace("/", "").split("Category:")[1]
        parentNode = Node(nodeName, None)
        return parentNode

    def dfs_from_category(self, rootNode, parentNode=None):
        if rootNode in visited:
            return
        visited.add(rootNode)

        if parentNode is None:
            parentNode = self.create_parent_node(rootNode)

        page = requests.get(rootNode)
        soup = BeautifulSoup(page.content, "html.parser")

        categories = soup.find_all("a",
                                   class_="category-page__member-link",
                                   string=re.compile("Category:"))
        links = soup.find_all("a",
                              class_="category-page__member-link",
                              string=re.compile("^(?!Category:).*$"))

        for link in links:
            linkName = link['title'].replace("/Legends", "").lower()
            if linkName in self.dataStore.read().keys():
                continue
            self.store_link(link)


        for category in categories:
            newNode = self.create_new_node(category, parentNode)
            href = category["href"]
            self.dfs_from_category(f"{self.url}{href}", newNode)

        if soup.find("a", class_="category-page__pagination-next"):
            print("NEXT FOUND")
            nextPage = soup.find("a", class_="category-page__pagination-next")["href"]
            self.dfs_from_category(f"{nextPage}", parentNode)


# Class defining each wiki page that is indexed
class WikiEntry:
    def __init__(self, name, wiki: Wiki):
        self.wiki = wiki
        self.name = name.replace("/Legends", "")
        self.underscoredName = self.name.replace(" ", "_")
        self.data = self.get_entry_contents()

    def get_entry_categories(self, soup):
        # Lists all categories the page belongs to
        entryCategories = soup.find("div",
                                    class_="page-header__categories"
                                    ).find_all("a")

        reString = r"^\d.more$"
        def not_more(category): return not re.search(reString, category.text)

        return [category.text for category in entryCategories if not_more(category)]

    def get_value_from_datasource(self, source):
        dataValue = source.find("div", class_="pi-data-value")

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

        return result

    def get_entry_contents(self):
        url = f"{self.wiki.url}/wiki/{self.underscoredName}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # Appends additional data to the results dict
        results = {}
        results['name'] = self.name
        results['categories'] = self.get_entry_categories(soup)
        results['image'] = self.get_image()

        # Finds all the data-sources stored on the wiki e.g. height, gender
        dataSources = soup.find_all("div", class_="pi-item")

        # Appends all the dataSources to the results dictionary
        for dataSource in dataSources:
            sourceName = dataSource["data-source"]
            result = self.get_value_from_datasource(dataSource)
            if sourceName == "affiliation" and type(result) is not list:
                result = [result]
            results[sourceName] = result

        return results

    def get_image(self):
        url = f"{self.wiki.url}/wiki/{self.underscoredName}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        result = soup.find("img", class_="pi-image-thumbnail")

        if result is not None:
            link = result['src']
            link = link.split(".png")[0] + ".png"
            link = link.split("/revision")[0]
            return link

        return None


class Node:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent


visited = set()

st = time.time()

starWarsWiki = Wiki("https://starwars.fandom.com")
starWarsWiki.dfs_from_category("https://starwars.fandom.com/wiki/Category:Droids_by_affiliation")
et = time.time()
print(f"{et-st}s")
