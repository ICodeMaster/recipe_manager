import recipe_handler
import json

def write_ingredients_to_json(ingredient_list:list):
    print("Generating Ingrd JSON:")
    json_object = json.dumps(ingredient_list, indent=4, sort_keys=True)
    with open("ingredient_data.json", "w", encoding="utf-8") as outfile:
        outfile.write(json_object)

def parse_json_ingredient(dct):
    ingrd = recipe_handler.Ingredient(dct["name"], dct["desc"])
    ingrd.id = dct["id"]
    try: ingrd.set_cost(dct["cost"][0], 1, dct["cost"][1])
    except IndexError:
        print("reading undefined cost")
    return ingrd
def read_ingredients_from_json(filename:str, filepath:str=None):
    if filepath:
        file = open(filepath + filename, "r", encoding="utf-8")
    else:
        file = open(filename, "r", encoding="utf-8")
    loaded_ingrds = json.loads(file.read(), object_hook=parse_json_ingredient)
    return loaded_ingrds
def write_recipes_to_json(recipe_list: recipe_handler.Recipe):
    print("Generating Ingrd JSON:")
    json_object = json.dumps(recipe_list, indent=4, sort_keys=True)
    with open("recipe_data.json", "w", encoding="utf-8") as outfile:
        outfile.write(json_object)