import argparse
import os
import pickle
import re
import json
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", default='encodings.pickle',
                    help="path to serialized db of facial encodings")
ap.add_argument("-o","--output",default="profile_detail.json",help="path to write output")
args = vars(ap.parse_args())
url = "https://www.google.com/search?q="


data = pickle.loads(open(args["encodings"], "rb").read())
dataset = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR =os .path.join(BASE_DIR,args['output'])

results = {}
for name ,id in zip(data['names'],data['id']):
    dataset[id] =name
for id,name in dataset.items():
    detail ={
        "id":id,
        "name":name
    }
    try:
        import urllib
        from bs4 import BeautifulSoup
        import requests
        print("id :{} ,name:{}".format(id,name))
        text = 'Central London'
        text = urllib.parse.quote_plus(text)
        url = 'https://google.com/search?q=' + name
        response = requests.get(url,timeout=10)
        print("google response",response.status_code,url)
        soup = BeautifulSoup(response.text, 'html.parser')
        name= "_".join(name.split(' '))
        wikki_link = None
        for g in soup.find_all('a', href=re.compile('https://en.wikipedia.org/wiki/')):
            link =  g['href'].split('&')[0].split('=')[1]
            if name in link.split("/"):
                wikki_link =link
                break
        if not wikki_link:
            continue
        print("wikki link:{}".format(wikki_link))
        detail['wikki_url'] = wikki_link
        response = requests.get(wikki_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup.prettify())
        title = soup.find(class_='firstHeading').get_text() if soup.find(class_='firstHeading') else ''
        detail[title]=title
        description =soup.find(class_="mw-parser-output")
        img =soup.find(class_='image') if soup.find(class_='image') else None
        img=img.find('img') if img else None
        img_url = None
        if img:
            img_url = "https:"+img['src']
        profile = ''
        if description :
            desc = description.find_all('p')
            for p in desc:
                profile += p.get_text()
        detail['image_url']= img_url
        import re
        profile =re.sub(r" ?\[[^)]+\]", '', profile)
        detail['profile_description'] = profile
        results[id]=detail
    except Exception as e:
        print(e)
    finally:
        file = open(BASE_DIR,'w')
        file.flush()
        json.dump(results,file,indent=4)





