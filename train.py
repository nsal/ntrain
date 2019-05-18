import requests
from bs4 import BeautifulSoup

link = 'http://ojp.nationalrail.co.uk/service/timesandfares/BFD/BTN/130619/0930/dep'

r = requests.get(link)
html = BeautifulSoup(r.text, 'html.parser')

print(html)
