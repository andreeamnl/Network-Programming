import requests
from bs4 import BeautifulSoup
urls = ["https://999.md/ro/list/audio-video-photo/headphones"]
urls=["https://999.md/ro/list/animals-and-plants/cats"]
data = []


def fetch_and_parse(current, urls, data):
    current_link = urls[current]
    page = requests.get(current_link)
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a',class_='js-item-ad'):
        link = str(link.get('href'))
        if "booster" not in link:
            url = 'https://999.md' + link
            data.append(url)

    max_pages = soup.select('nav.paginator > ul > li > a')
    for page in max_pages:
        link = str('https://999.md' + page['href'])
        if link not in urls:
            urls.append(link)
    try:
                
        if  current >= len(urls)-1:
            return data
        else:
            
            fetch_and_parse(current+1, urls, data)
    except Exception as e:
        print(e)

init = fetch_and_parse(0, urls, data)


f = open("links.txt", "a")
for link in data:
    #f.write(link + "\n")
    print(link)
f.close()


print(len(data))
#print(data)