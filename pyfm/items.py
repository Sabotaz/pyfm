import json
from pprint import pprint
import re
import prix
from binascii import unhexlify

initialized = False        
reader = None

items = dict()
item_types = dict()
effects = dict()
jobs = dict()

class d2i_reader:
# @Torf : in Dofus 2.10 and before, there was 3 parts in those files :
# Utf-8 strings, offset table for integer indexed strings and
# offset + keys table for text - indexed strings. Now there is some non-text
# additionnal data at the end. This data at the end is highly redondant
# (like 4 bytes int with small increments each time).
    def __init__(self, file = 'i18n_fr.d2i'):
        self.names=open(file,'rb')
        self.ids = dict()
        self.table_address = int(self.read(4),16)
        self.read_table()
        
    def read(self,n):
        return ''.join('%02x' % ord(b) for b in self.names.read(n))
        
    def read_table(self):
        self.names.seek(self.table_address)
        t = 0
        table_length = int(self.read(4),16)
        t = t + 4
        while True:
            if t >= table_length:
                break
            id = int(self.read(4),16)
            nb = int(self.read(1),16)
            tuple = [int(self.read(4),16) for i in range(nb+1)]
            self.ids[id] = tuple
            t = t + 4+1+(nb+1)*4
                
    def get_name(self,id):
        try:
            self.names.seek(self.ids[id][0])
        except KeyError:
            return ''
        n = int(self.read(2),16)
        # name = unhexlify(self.read(n)).decode('latin-1')
        name = unhexlify(self.read(n)).decode('utf-8')
        # name = unicode(self.read(n)).decode('hex')
        return name        

class item:
    def __init__(self, data):
        self.data = data
        caracs = self.get("possibleEffects")
        self.caracteristics = dict()
        for carac in caracs:
            id = carac["effectId"]
            num = carac["diceNum"]
            side = carac["diceSide"]
            min = num
            max = side if side != 0 else min
            (name1,name2) = effects[id]
            self.caracteristics[name2] = (min,max)
    
    def get_price(self):
        if self.get_name() in prix.prix:
            return prix.prix[self.get_name()]
        elif hasattr(self, "recipe"):
            return self.recipe.get_fabrication_price()
        else:
            return 0
    
    def get_id(self):
        return self.get("id")
        
    def get_level(self):
        return self.get("level")
    
    def get_nameId(self):
        return self.get("nameId")
    
    def get_name(self):
        return reader.get_name(self.get_nameId())
    
    def get(self, id):
        return self.data[id]
        
    def get_type(self):
        return self.get("typeId")
        
    def get_caracs(self):
        return self.caracteristics
        
    def get_carac(self,carac):
        if carac not in self.caracteristics:
            return (0,0)
        return self.caracteristics[carac]
        
def load_caracs(file = 'Effects.json'):
    global effects
    json_data=open(file)
    data = json.load(json_data)
    regex = re.compile(r"\+?#1{.*}#2 (.*)")
    for node in data:
        id = node["id"]
        name = reader.get_name(node["descriptionId"])
        name2 = regex.sub(r"\1",name)
        if name == '':
            name = id
            name2 = id
        effects[id] = (name,name2)
    # out = open('caracs_init.csv','w')
    # for (k,(name,name2)) in effects.items():
        # out.write(str(k))
        # out.write(',')
        # out.write(str(name2))
        # out.write('\n')

def load_jobs(file = 'Jobs.json'):
    global jobs
    json_data=open(file)
    data = json.load(json_data)
    for node in data:
        id = node["id"]
        name = reader.get_name(node["nameId"])
        jobs[id] = name
                
def __init__():
    global reader
    reader = d2i_reader()
    load_caracs()
    load_types()
    load_items()
    
    load_jobs()
    
def load_items(file = 'Items.json'):
    global items
    json_data=open(file)
    data = json.load(json_data)
    x = len(data)/10
    n = 0
    for node in data:
        i = item(node)
        items[i.get_id()] = i
        n += 1
        if n % x == 0:
            print '*'

def load_types(file = 'ItemTypes.json'):
    global item_types
    json_data=open(file)
    data = json.load(json_data)
    for node in data:
        item_types[node["id"]] = reader.get_name(node["nameId"])
  
def get_job(id):
    if id in jobs:
        return jobs[id]
    else:
        return None
        
def get_item(id):
    if id in items:
        return items[id]
    else:
        return None

def get_items():
    return items
        
if not initialized:        
    __init__()