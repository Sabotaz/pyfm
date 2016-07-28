import json
from pprint import pprint
from items import get_item, get_job
from ordered_set import OrderedSet
import prix

initialized = False
recipes_by_job = dict()
ingredient_prices = dict()
runes_prices = dict()
colonnes_effects = dict()
all_recipes = []

class recipe:
    def __init__(self, result,job):
        self.result = result
        self.ingredients = dict()
        self.caracs = dict()
        self.job = job
        item = get_item(self.result)
        if item != None:
            string = item.get_name()
            for (carac, (min,max)) in item.get_caracs().items():
                self.caracs[carac] = (min,max)
            
    def add_ingredient(self,id,quantity):
        self.ingredients[id] = quantity
        ingredient_prices[id] = 0
        
    def get_fabrication_price(self):
        return sum(nb*get_item(id).get_price() for (id,nb) in self.ingredients.iteritems())
        
    def get_result_price(self):
        return get_item(self.result).get_price()
        
    def get_runes_result_price(self):
        total = 0
        for (type, (ba, pa, ra)) in get_item(self.result).runes.iteritems():
            baname = "Rune " + type
            paname = "Rune Pa " + type
            raname = "Rune Ra " + type
            if baname in prix.prix:
                total += ba * prix.prix[baname]
            if paname in prix.prix:
                total += pa * prix.prix[paname]
            if raname in prix.prix:
                total += ra * prix.prix[raname]
        return total
        
def __init__():
    load_items()
    
def load_items(file = 'Recipes.json'):
    global items
    global all_recipes
    json_data=open(file)
    data = json.load(json_data)
    for node in data:
        item = get_item(node["resultId"])
        if item:
            recette = recipe(node["resultId"], node["jobId"])
            for (ingredient,quantity) in zip(node["ingredientIds"], node["quantities"]):
                recette.add_ingredient(ingredient,quantity)
            if recette.job not in recipes_by_job:
                recipes_by_job[recette.job] = dict()
            recipes_by_job[recette.job][recette.result] = recette
            all_recipes += [recette]
            
def add_price(id,prix):
    ingredient_prices[id] = prix

def get_all_recipes():
    return all_recipes
    
if not initialized:        
    __init__()