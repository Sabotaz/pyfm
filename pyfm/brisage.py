# -*- coding: utf-8 -*-

import math
import items
from items import get_item, get_job
import json
import recipes

carac_to_rune = { # carac -> rune
    u"Force"                 : u"Fo",
    u"Intelligence"          : u"Ine",
    u"Chance"                : u"Cha",
    u"Agilité"               : u"Age",
    u"Vitalité"              : u"Vi",
    u"Sagesse"               : u"Sa",
    u"Initiative"            : u"Ini",
    u"Prospection"           : u"Prospe",
    u"Puissance"             : u"Pui",
    u"Résistance Terre"      : u"Ré Terre",
    u"Résistance Feu"        : u"Ré Feu",
    u"Résistance Neutre"     : u"Ré Neutre",
    u"Résistance Air"        : u"Ré Air",
    u"Résistance Eau"        : u"Ré Eau",
    u"% Résistance Terre"    : u"Ré Per Terre",
    u"% Résistance Feu"      : u"Ré Per Feu",
    u"% Résistance Neutre"   : u"Ré Per Neutre",
    u"% Résistance Air"      : u"Ré Per Air",
    u"% Résistance Eau"      : u"Ré Per Eau",
    u"Résistance Poussée"    : u"Ré Pou",
    u"Résistance Critiques"  : u"Ré Cri",
    u"Esquive PA"            : u"Ré Pa",
    u"Esquive PM"            : u"Ré Pme",
    u"Arme de chasse"        : u"Chasse",
    u"Pods"                  : u"Pod",
    u"Puissance (pièges)"    : u"Pi Per",
    u"Dommages Pièges"       : u"Pi",
    u"Tacle"                 : u"Tac",
    u"Fuite"                 : u"Fui",
    u"Retrait PA"            : u"Ret Pa",
    u"Retrait PM"            : u"Ret Pme",
    u"Soins"                 : u"So",
    u"Coups Critiques"       : u"Cri",
    u"Invocations"           : u"Invo",
    u"PO"                    : u"Po",
    u"PM"                    : u"Ga Pme",
    u"PA"                    : u"Ga Pa",
    u"Dommages"              : u"Do",
    u"Renvoie dommages"      : u"Do Ren",
    u"Dommages Terre"        : u"Do Terre",
    u"Dommages Neutre"       : u"Do Neutre",
    u"Dommages Feu"          : u"Do Feu",
    u"Dommages Air"          : u"Do Air",
    u"Dommages Eau"          : u"Do Eau",
    u"Dommages Poussée"      : u"Do Pou",
    u"Dommages Critiques"    : u"Do Cri",
}

runes = { # rune -> (power-rate/effet, effet-ba, effet-pa, effet-ra)
    u"Fo"            : (1,   1,  3,  10),
    u"Ine"           : (1,   1,  3,  10),
    u"Cha"           : (1,   1,  3,  10),
    u"Age"           : (1,   1,  3,  10),
    u"Vi"            : (0.25,3,  10, 30),
    u"Sa"            : (3,   1,  3,  10),
    u"Ini"           : (0.1, 10, 30, 100),
    u"Prospe"        : (3,   1,  3,  None),
    u"Pui"           : (2,   1,  3,  10),
    u"Ré Terre"      : (2,   1,  None,None),
    u"Ré Feu"        : (2,   1,  None,None),
    u"Ré Neutre"     : (2,   1,  None,None),
    u"Ré Air"        : (2,   1,  None,None),
    u"Ré Eau"        : (2,   1,  None,None),
    u"Ré Per Terre"  : (6,   1,  None,None),
    u"Ré Per Feu"    : (6,   1,  None,None),
    u"Ré Per Neutre" : (6,   1,  None,None),
    u"Ré Per Air"    : (6,   1,  None,None),
    u"Ré Per Eau"    : (6,   1,  None,None),
    u"Ré Pou"        : (2,   1,  3,  None),
    u"Ré Cri"        : (2,   1,  3,  None),
    u"Ré Pa"         : (7,   1,  3,  None),
    u"Ré Pme"        : (7,   1,  3,  None),
    u"Chasse"        : (5,   1,  None,None),
    u"Pod"           : (0.25,10, 30, 100),
    u"Pi Per"        : (2,   1,  3,  10),
    u"Pi"            : (15,  1,  3,  None),
    u"Tac"           : (4,   1,  3,  None),
    u"Fui"           : (4,   1,  3,  None),
    u"Ret Pa"        : (7,   1,  3,  None),
    u"Ret Pme"       : (7,   1,  3,  None),
    u"So"            : (20,  1,  None,None),
    u"Cri"           : (30,  1,  None,None),
    u"Invo"          : (30,  1,  None,None),
    u"Po"            : (51,  1,  None,None),
    u"Ga Pme"        : (90,  1,  None,None),
    u"Ga Pa"         : (100, 1,  None,None),
    u"Do"            : (20,  1,  None,None),
    u"Do Ren"        : (30,  1,  None,None),
    u"Do Terre"      : (5,   1,  3,  None),
    u"Do Neutre"     : (5,   1,  3,  None),
    u"Do Feu"        : (5,   1,  3,  None),
    u"Do Air"        : (5,   1,  3,  None),
    u"Do Eau"        : (5,   1,  3,  None),
    u"Do Pou"        : (5,   1,  3,  None),
    u"Do Cri"        : (5,   1,  3,  None),
}

def puissance_extractible(poids, niveau, jet):
    return max(0,min(1.5*(niveau*niveau)/math.pow(poids,5.0/4.0) + ((jet-1) / poids) * (100.0*2.0/3.0 - 1.5*(niveau*niveau)/math.pow(poids,5.0/4.0)), 100.0*2.0/3.0))/100.0

def puissance_reelle(jet):
    return jet * (2.0/3.0)
        
def power_rune(carac, force):
    (pwrt, ba, pa, ra) = runes[carac]
    if force == "ba":
        return pwrt*ba
    elif force == "pa":
        if pa == None:
            return None
        else:
            return pwrt*pa
    elif force == "ra":
        if ra == None:
            return None
        else:
            return pwrt*ra
    else:
        return None
    
def poids_rune(carac, force):
    (pwrt, ba, pa, ra) = runes[carac]
    if force == "ba":
        return ba
    elif force == "pa":
        if pa == None:
            return None
        else:
            return pa
    elif force == "ra":
        if ra == None:
            return None
        else:
            return ra
    else:
        return None
    
def taux_intermediaire(carac, force):
    (pwrt, ba, pa, ra) = runes[carac]
    if force == "ba":
        return ba
    elif force == "pa":
        if pa == None:
            return None
        else:
            return 2*taux_intermediaire(carac,"ba") + pa
    elif force == "ra":
        if ra == None:
            return None
        else:
            return 2*taux_intermediaire(carac,"pa") + ra
    else:
        return None

def brisage_jet(jet, carac, niveau):
    (ba, pa, ra) = (0,0,0)
    if jet == 1:
        ba = puissance_extractible(power_rune(carac, "ba"),niveau,jet)
    else:
        pui = puissance_reelle(jet)
        rands = [1+i*0.001+0.0005 for i in range(-100,100)]
        for rand in rands:
            (nba, npa, nra) = brisage_puissance(pui*rand, carac, niveau)
            (ba, pa, ra) = (ba+nba, pa+npa, ra+nra)
        div = float(len(rands))
        (ba, pa, ra) = (ba/div, pa/div, ra/div)
    return (ba, pa, ra)

def brisage_puissance(pui, carac, niveau):
    taux_ba = taux_intermediaire(carac, "ba")
    taux_pa = taux_intermediaire(carac, "pa")
    taux_ra = taux_intermediaire(carac, "ra")
    poids_ba = poids_rune(carac, "ba")
    poids_pa = poids_rune(carac, "pa")
    poids_ra = poids_rune(carac, "ra")
    (ba, pa, ra) = (0,0,0)
    if taux_ra:
        ra = (pui - pui % taux_ra) / taux_ra
        pui = pui - ra * poids_ra
    if taux_pa:
        pa = (pui - pui % taux_pa) / taux_pa
        pui = pui - pa * poids_pa
    
    ba = pui / taux_ba
    return (ba, pa, ra)

def brisage_jet_minmax(min, max, carac, niveau):
    (ba, pa, ra) = (0,0,0)
    for jet in range(min, max+1):
        (nba, npa, nra) = brisage_jet(jet, carac, niveau)
        (ba, pa, ra) = (ba+nba, pa+npa, ra+nra)
    (ba, pa, ra) = (ba/(max+1-min), pa/(max+1-min), ra/(max+1-min))
    return (ba, pa, ra)
    
def brisage_jets(jets, niveau):
    runes = dict()
    for (carac, (min, max)) in jets.items():
        if carac in carac_to_rune:
            rune = carac_to_rune[carac]
            runes[rune] = brisage_jet_minmax(min, max, rune, niveau)
        else:
            pass
            #print "carac non trouvée", carac
    return runes
    
def brisage_objet(item):
    return brisage_jets(item.get_caracs(), item.get_level())
    
def write_item(file, item, recipe):
    f.write(item.get_name() + '\t')
    #recipe
    n = 0
    for ingredient, nb in recipe.ingredients.items():
        f.write(str(nb) + "\t")
        obj = get_item(ingredient)
        if obj != None:
            f.write(obj.get_name() + "\t")
        else:
            f.write(str(ingredient) + "\t")
        n += 1
    for i in range(n, 8):
        f.write('\t\t')
            
    for (carac, (min, max)) in item.get_caracs().items():
        if carac in carac_to_rune:
            rune = carac_to_rune[carac]
            (ba, pa, ra) = item.runes[rune]
            f.write(str(ba) + '\t' + str(pa) + '\t' + str(ra) + '\t' + rune + '\t')
        else:
            pass
    f.write('\n')

all_items = dict()
    
if __name__ == "__main__":
    allowed = [11,13,14,15,16,17,18,19,20,27,31]
    remove_jobs = [0,1,2,24,25,26,28,36,41,56,58,60,65]
    # recipes=open('Recipes.json')
    # recipes = json.load(recipes)
    # print len(recipes)
    # f = open('runes', 'w')
    # for n, recipe in enumerate(recipes):
        # if recipe["jobId"] not in remove_jobs:
            # if recipe["jobId"] not in allowed:
                # print items.get_job(recipe["jobId"]), recipe["jobId"]
            # item = items.get_item(recipe["resultId"])
            # item.runes = brisage_objet(item)
            # write_item(f, item, recipe)
        # if n % 1000 == 0:
            # print n
    f = open('runes', 'w')
    for n, recipe in enumerate(recipes.all_recipes):
        if recipe.job not in remove_jobs:
            if recipe.job not in allowed:
                print items.get_job(recipe.job), recipe.job
            item = items.get_item(recipe.result)
            item.runes = brisage_objet(item)
            write_item(f, item, recipe)
        if n % 1000 == 0:
            print n
    f.close()
    
else:
    allowed = [11,13,14,15,16,17,18,19,20,27,31]
    # remove_jobs = [0,1,2,24,25,26,28,36,41,56,58,60,65]
    for n, recipe in enumerate(recipes.all_recipes):
        if recipe.job in allowed:
            item = items.get_item(recipe.result)
            item.runes = brisage_objet(item)
            item.recipe = recipe
            if recipe.job not in all_items:
                all_items[recipe.job] = []
            all_items[recipe.job] += [item]
    for job in all_items:
        items = all_items[job]
        items = sorted(items)
        items.sort(key = lambda item: item.recipe.get_fabrication_price() - item.recipe.get_runes_result_price())
        all_items[job] = items