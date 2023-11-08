
#!/usr/bin/env python
import pika
import threading
import requests
from bs4 import BeautifulSoup
import json  
from tinydb import TinyDB, Query

db = TinyDB('small.json', ensure_ascii=False)

 


def tojson(lnk):
    reqs = requests.get(lnk)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    def getname():
        try:
            str = soup.find('header',class_="adPage__header").get_text()
        except Exception as e:
            str = ''
        return str
    def getdescription():
        try:
            str = soup.find('div',class_="adPage__content__description grid_18").get_text()
        except Exception as e:
            str = ''
        return str
    def getprice():
        try:
            str = soup.find('span',class_="adPage__content__price-feature__prices__price__value").get_text() + soup.find('span',class_="adPage__content__price-feature__prices__price__currency").get_text()
        except Exception as e:
            str = ''
        return str
    def getcountry():
        try:
            str = soup.find('dd',itemprop="address").get_text()
        except Exception as e:
            str = ''
        return str


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
        
        "Name" : getname(),
        "Description" : getdescription(),
        "Price" : getprice(), 
        "Country" : getcountry(),
        "Phone" : tel,
    }
    default.update(properties) ## adds up both dictionaries
    #y = json.dumps(default, ensure_ascii=False)
    return default   ##this no longer returns json, but a dict, since tinydb needs dicts on insert



def consume(i):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=False)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs', queue=queue_name)
    def callback(ch, method, properties, body):
        print(f"Thread nr:[{i}], {body}")
        json_data = tojson(body)
        try:
            db.insert(json_data)  # Insert the valid dictionary into the database
        except json.decoder.JSONDecodeError as e:
            pass



    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()




# Number of consumer threads
num_threads = 2  ##i only ran the code for a few seconds 

# Create and start consumer threads
threads = []
for i in range(num_threads):
    thread = threading.Thread(target=consume, args=(i,))
    threads.append(thread)
    thread.start()

print(' [*] Waiting for logs. To exit, press CTRL+C')

# Wait for all consumer threads to finish
for thread in threads:
    thread.join()

db.close()