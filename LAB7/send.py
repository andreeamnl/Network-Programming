#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

list  = ["het", "salu", "ok"]
channel.exchange_declare(exchange='logs', exchange_type='fanout')

for i in list:
    message = i
    channel.basic_publish(exchange='logs', routing_key='', body=message)
    print(f" [x] Sent {message}")
#message = ' '.join(sys.argv[1:]) or "info: Hello World!"

connection.close()