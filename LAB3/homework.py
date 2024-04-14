import requests
from bs4 import BeautifulSoup
import json  
lnk = "https://999.md/ro/84159408"  #this is a real scrapped link
#lnk = "https://999.md/ro/84349867"   #this other link simply has more data to be scrapped
 
 
def tojson(lnk):
    reqs = requests.get(lnk)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    prop_list = soup.find_all('li',class_="m-value")
    properties = {}
    for elem in prop_list:   #iterates throuhgh all properties and adds them to a dictionary
        elem = elem.get_text().split()
        properties[elem[0]] = elem[1]

    for link in soup.find_all('a'):   #finds first phone number
        href = link.get('href')
        if href is not None and ("+373" in href):
            tel = (link.get('href')[5:16])
            break

    default = {
        "Name" : soup.find('header',class_="adPage__header").get_text(),
        "Description" : soup.find('div',class_="adPage__content__description grid_18").get_text(),
        "Price" : soup.find('span',class_="adPage__content__price-feature__prices__price__value").get_text() + soup.find('span',class_="adPage__content__price-feature__prices__price__currency").get_text(), 
        "Country" : soup.find('dd',itemprop="address").get_text(),
        "Phone" : tel,
    }
    default.update(properties) ## adds up both dictionaries
    y = json.dumps(default, ensure_ascii=False)
    return y



print(tojson(lnk))

                