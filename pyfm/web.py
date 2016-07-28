
def text_container(part1, part2):
    text = """
    <div>
<div class=\"text_container\">
    """ + part1 + """
    <div><!--div that we want to hide-->
    """ + part2 + """
    </div>
</div><!--end div_text_container-->
</div>
"""
    return text
    
    
def sep_milliers(s, sep='.'):
    if len(s) <= 3:
        return s
    else:
        return sep_milliers(s[:-3], sep) + sep + s[-3:]
    
def make_ingredients_list(args):
    text = "<ul>"
    for (quantity, name, price, tag) in args:
        text += "<li><span class=\"" + tag + "\">" + quantity + " x " + name + " (" + sep_milliers(price, ' ') + " k/u)</span></li>"
    text += "</ul>"
    return text
    
def make_runes_list(args):
    text = "<ul>"
    for carac in args:
        text += "<li>"
        for (quantity, name, price, tag) in args[carac]:
            text += "<span class=\"" + tag + "\">" + quantity + " x " + name + " (" + sep_milliers(price, ' ') + " k/u)</span><br/>"
        text += "</li>"
    text += "</ul>"
    return text
    
def display_item(args):
    part1 = """
        <table class="item_bar">
        <tr>
        <td class="item_name">""" + args["name"] + """</td>
        <td class=\"""" + args["craft tag"] + """">Craft : """ + sep_milliers(args["price in"], ' ') + """ kamas</td>
        <td class=\"""" + args["brisage tag"] + """">Brisage : """ + sep_milliers(args["price out"], ' ') + """ kamas</td>
        <td class=\"""" + args["profit tag"] + """">Profit : """ + sep_milliers(args["profit"], ' ') + """ kamas</td>
        </tr>
        </table>
        """
    part2 = """
        <table class="item_detail">
        <tr>
        <td>""" + make_ingredients_list(args["ingredients"]) + """</td>
        <td>""" + make_runes_list(args["runes"]) + """</td>
        </tr>
        </table>
        """
        
    return text_container(part1, part2)
    