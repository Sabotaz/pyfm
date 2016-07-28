import BaseHTTPServer
from SocketServer import ThreadingMixIn

import time
import sys
import os
import urllib2
from urlparse import urlparse, parse_qs

HOST_NAME = '188.165.65.182'
PORT_NUMBER = 8080

import web

import brisage
from items import get_item, get_items, get_job
from brisage import carac_to_rune, runes
import prix

lettres = [
u"A", u"B", u"C", u"D", u"E",
u"F", u"G", u"H", u"I", u"J",
u"K", u"L", u"M", u"N", u"O",
u"P", u"Q", u"R", u"S", u"T",
u"U", u"V", u"W", u"X", u"Y",
u"Z"]

correspondances = {
    u"E": [u"É"],
    u"O": [u"Œ"],
    u"U": [u"Ú"],
    u"P": [u"p"],        
}

import socket,struct

def makeMask(n):
    "return a mask of n bits as a long integer"
    #return (2L<<n-1) - 1
    return (4294967295L<<n)

def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('>L',socket.inet_aton(ip))[0]

def networkMask(ip,bits):
    "Convert a network address to a long integer" 
    return dottedQuadToNum(ip) & makeMask(bits)

def addressInNetwork(ip,net):
   "Is an address in a network"
   return ip & net == net

# address = dottedQuadToNum("192.168.1.1")
# networka = networkMask("10.0.0.0",24)
# networkb = networkMask("192.168.0.0",24)
# print (address,networka,networkb)
# print addressInNetwork(address,networka)
# print addressInNetwork(address,networkb)

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def write(self, s):
        self.wfile.write(s.encode('utf-8'))

    def display_metiers(self):
        self.write(u'<div>')
        self.write(u'<a href="/jobs?job_id=15">Cordonnier</a> - ')
        self.write(u'<a href="/jobs?job_id=27">Tailleur</a> - ')
        self.write(u'<a href="/jobs?job_id=16">Bijoutier</a><br/>')
        self.write(u'<a href="/jobs?job_id=13">Sculpteur d\'arcs</a> - ')
        self.write(u'<a href="/jobs?job_id=18">Sculpteur de batons</a> - ')
        self.write(u'<a href="/jobs?job_id=19">Sculpteur de baguettes</a><br/>')
        self.write(u'<a href="/jobs?job_id=11">Forgeur d\'épées</a> - ')
        self.write(u'<a href="/jobs?job_id=14">Forgeur de marteaux</a> - ')
        self.write(u'<a href="/jobs?job_id=17">Forgeur de dagues</a><br/>')
        self.write(u'<a href="/jobs?job_id=20">Forgeur de pelles</a> - ')
        self.write(u'<a href="/jobs?job_id=31">Forgeur de haches</a><br/>')
        self.write(u'Prix : ')
        for l in lettres:
            self.write(u'<a href="/prices?l=' + l + u'">[' + l + u']</a> ')
        self.write(u'<br/>')
        self.write(u'<a href="/search">Rechercher</a><br/>')
        self.write(u'</div>')
        
    def get_search_params(self, params):
        runes_choice = []
        jobs_choice = []
        flags = dict()
        if "rune" in params:
            runes_choice = params[u"rune"]
            runes_choice = [i.decode("utf8") for i in runes_choice]
        if "job" in params:
            jobs_choice = params[u"job"]
            jobs_choice = [int(i) for i in jobs_choice]
        flags[u"jobs"] = jobs_choice
        flags[u"runes"] = runes_choice
        return flags
        
    def afficher_search_menu(self, flags):
        self.write(u"""<div><form action="/search" method="get">""")
                    
        self.write(u"""<table><tr><td>""")
                
        self.write(u"""<table>""")
        for rune in runes:
            (pwd, ba, pa, ra) = runes[rune]
            types = [ba, pa, ra]
            add = [u"Ba ", u"Pa ", u"Ra "]
            self.write(u"<tr>")
            for i in range(3):
                if types[i] is not None:
                    name = add[i] + rune
                    if name in flags[u"runes"]:
                        self.write(u"""<td><input type="checkbox" name="rune" value=\"""" + name + u"""" checked>""" + name + u"""</td>""")
                    else:
                        self.write(u"""<td><input type="checkbox" name="rune" value=\"""" + name + u"""">""" + name + u"""</td>""")
                else:
                        self.write(u"<td></td>")
            self.write(u"</tr>")
        self.write(u"""</table><br/>""")
        
        self.write(u"""</td><td>""")
                    
        jobs_names = [u"Cordonnier", u"Tailleur", u"Bijoutier",
         u"Sculpteur d\'arcs", u"Sculpteur de batons",
         u"Sculpteur de baguettes", u"Forgeur d\'épées",
         u"Forgeur de marteaux", u"Forgeur de dagues",
         u"Forgeur de pelles", u"Forgeur de haches"]
        jobs_ids = [15, 27, 16, 13, 18, 19, 11, 14, 17, 20, 31]
        for (name, id) in zip(jobs_names, jobs_ids):
            if id in flags[u"jobs"]:
                self.write(u"""<input type="checkbox" name="job" value=\"""" + unicode(id) + u"""" checked>""" + name + u"""<br>""")
            else:
                self.write(u"""<input type="checkbox" name="job" value=\"""" + unicode(id) + u"""">""" + name + u"""<br>""")
                
        self.write(u"""</td></tr></table>""")
                
        self.write(u"""<input type="submit" name="submit" value="Rechercher"/>""")
            
        self.write(u"""</form></div>""")

    def display_prices_search(self, flags):
        items = []
        for job_id in flags[u"jobs"]:
            for item in brisage.all_items[job_id]:
                display = False
                for rune in flags[u"runes"]:
                    type = rune[3:]
                    if type in item.runes:
                        powers = item.runes[type]
                        if rune[:2] == u"Ba" and powers[0] != 0:
                            display = True
                        if rune[:2] == u"Pa" and powers[1] != 0:
                            display = True
                        if rune[:2] == u"Ra" and powers[2] != 0:
                            display = True
                if display:
                    items.append(item)
        items.sort(key = lambda item: item.recipe.get_fabrication_price() - item.recipe.get_runes_result_price())
        self.display_items(items)
        
    def display_prices_list(self, lettre):
        self.display_metiers()
        self.write(u"""
        <table>
        <tr>
            <th>Nom</th>
            <th>Prix</th>
            <th></th>
        </tr>""")
        
        items = []
        for id in get_items():
            item = get_item(id)
            if item.get_name()[0] == lettre or (lettre in correspondances and item.get_name()[0] in correspondances[lettre]):
                items.append(item)
                
        items.sort(key = lambda item: item.get_name())
                
        for item in items:
            self.write(u"""
            <tr>
                <form action="/prices" method="get">
                    <td>
                        <input class="object_name" type="text" name="nom" disabled="disabled" value=\"""" + item.get_name() + u""""/>
                    </td>
                    <td>
                        <input class="object_price" type="number" name="prix" value=\"""" + unicode(item.get_price()) + """"/>
                    </td>
                    <td>
                        <input type="hidden" name="id" value=\"""" + unicode(id) + u""""/>
                        <input type="submit" name="submit" value="Modifier"/>
                    </td>
                </form>
            </tr>""")
        
        self.write(u"</table>")
        

    def item_list(self, job_id):
        if job_id not in brisage.all_items:
            self.write(u'job ' + unicode(job_id)+ u' unknow...<br>')
            self.write(u'job list : ' + unicode(brisage.all_items.keys()))
            return
        items = brisage.all_items[job_id]
            
        self.display_metiers()
        self.display_items(items)
            
    def display_items(self, items):
        for item in items:
            args = dict()
            args["name"] = item.get_name()
            price_in = item.recipe.get_fabrication_price()
            price_out = item.recipe.get_runes_result_price()
            args["price in"] = unicode(int(price_in))
            args["price out"] = unicode(int(price_out))
            args["profit"] = unicode(int(price_out - price_in))
            
            if (int(price_out - price_in)) > 0:
                args["profit tag"] = u"positif"
            else:
                args["profit tag"] = u"negatif"
                
            args["ingredients"] = []
            args["craft tag"] = u"complet"
            
            for ingredient, nb in item.recipe.ingredients.items():
                obj = get_item(ingredient)
                name = obj.get_name()
                if name in prix.prix:
                    price = unicode(prix.prix[name])
                    tag = u"price_ok"
                elif hasattr(obj, "recipe"):
                    price = unicode(obj.recipe.get_fabrication_price())
                    tag = u"price_ok"
                else:
                    price = u"?"
                    tag = u"no_price"
                    args["craft tag"] = u"incomplet"
                args["ingredients"].append((unicode(nb), name, price, tag))
                
            args["runes"] = dict()
            args["brisage tag"] = u"complet"
            for (carac, (min, max)) in item.get_caracs().items():
                if carac in carac_to_rune:
                    args["runes"][carac] = []
                    
                    rune = carac_to_rune[carac]
                    powers = item.runes[rune]
                    names = (u"Rune ", u"Rune Pa ", u"Rune Ra ")
                    prix_ba = prix_pa = prix_ra = u"?"
                    for q, name in zip(powers, names):
                        if q != 0:
                            qt = u"%0.2f"%(q,)
                            rune_name = name + rune
                            if rune_name in prix.prix:
                                price = unicode(prix.prix[rune_name])
                                tag = u"price_ok"
                            else:
                                price = u"?"
                                tag = u"no_price"
                                args["brisage tag"] = u"incomplet"
                            args["runes"][carac].append((qt, rune_name, price, tag))
            
            display = web.display_item(args)
            self.write(display)
            
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
    def begin(self, page_name):
        self.do_HEAD()
        self.write(u"""<html> <head><title> %s </title>
            <script type="text/javascript" src="http://code.jquery.com/jquery-1.7.min.js"></script>
            <script src="script.js" type="text/javascript"></script>
            <link rel="stylesheet" type="text/css" href="style.css">
        </head> <body>\n""" % page_name)
    
    def end(self):
        self.write(u"</body> </html>\n")
    
    def do_GET(self):

        address = dottedQuadToNum(self.client_address[0])
        ens = networkMask("138.231.0.0",16)
        
        #if not addressInNetwork(address,ens):
        #    self.send_response(403)
        #    self.end_headers()
        #    return
            
        params = parse_qs(urlparse(self.path).query)
        if self.path.endswith('.js') or self.path.endswith('.css'):
            try:
                filename = os.path.dirname(os.path.realpath(__file__)) + os.sep + "res" + urllib2.url2pathname(self.path)
                f = open(filename, 'rb') #open requested file
                #send code 200 response
                self.send_response(200)
                #send header first
                if  self.path.endswith('.js'):
                    self.send_header('Content-type','text/javascript')
                elif  self.path.endswith('.css'):
                    self.send_header('Content-type','text/css')
                self.end_headers()
                #send file content to client
                self.wfile.write(f.read())
                f.close()
            except IOError:
                self.send_error(404, 'File Not Found')
        elif self.path.startswith("/jobs"):
            if "job_id" in params:
                if hasattr(self, "invalidate") and self.invalidate:
                    for job in brisage.all_items:
                        brisage.all_items[job].sort(key = lambda item: item.recipe.get_fabrication_price() - item.recipe.get_runes_result_price())
                    self.invalidate = False
                self.begin(u"runes")
                self.item_list(int(params["job_id"][0]))
                self.end()
            else:
                self.begin(u"zendikar")
                self.display_metiers()
                self.end()
                
        elif self.path.startswith("/prices"):
            id = None
            price = None
            if "id" in params:
                id = int(params[u"id"][0])
            if "prix" in params:
                price = int(params[u"prix"][0])
            if id is not None and price is not None:
                prix.set_price(get_item(id).get_name(), price)
                self.invalidate = True
                self.send_response(304)
                self.end_headers()
            else:
                if "l" in params:
                    lettre = params[u"l"][0].decode("utf8")
                    if lettre not in lettres:
                        lettre = u'A'
                else:
                    lettre = u'A'
                self.begin(u"prix")
                self.display_prices_list(lettre)
                self.end()
                
        elif self.path.startswith("/search"):
            flags = self.get_search_params(params)
            
            self.begin(u"search")
            self.display_metiers()
            self.afficher_search_menu(flags)
            self.display_prices_search(flags)
            self.end()
                
        else:
            self.begin(u"zendikar")
            self.display_metiers()
            self.end()

class Server(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass
    
if __name__ == "__main__":
    server_class = Server
    httpd = server_class((HOST_NAME, PORT_NUMBER), Handler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

    
