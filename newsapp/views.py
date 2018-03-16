from django.shortcuts import render

import json
import urllib.request
from newsapi import NewsApiClient
from nltk.corpus import stopwords
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from functools import partial

from dateutil.parser import parse

# from preprocessing import perform_preprocessing,normalize_text
from . import preprocessing

API_KEY = "87e663cbe74e4c0c9a8cb4725bce4b42"

# Create your views here.

garbage = set(stopwords.words('english'))
vectorizer = pickle.load(open("pickle-data/vectorizer.p", "rb"))
encoder = pickle.load(open("pickle-data/encoder.p", "rb"))
keywords = pickle.load(open("pickle-data/keywords.p", "rb"))
classifier = pickle.load(open("pickle-data/classifier.p", "rb"))

'''
def normalize_text(s, keywords):
    s = s.lower()

    s = re.sub('\s\W', ' ', s)
    s = re.sub('\W\s', ' ', s)

    s = re.sub('\s+', ' ', s)
    s = s.split()
    s = list(filter((lambda x: x not in garbage), s))
    for word in s:
        keywords.append(word)
    s = " ".join(s)
    return s
'''

def format_live_news_title(title, keywords):
    return [" ".join(list(word for word in title.split() if word in keywords))]


def find_category(title, vectorizer, encoder, keywords, classifier):
    sample = preprocessing.normalize_text(title, [])
    sample = format_live_news_title(sample, keywords)
    sample = vectorizer.transform(sample)
    output = classifier.predict(sample)
    return encoder.inverse_transform(output)[0]

def get_news_articles(category):
    api = NewsApiClient(api_key=API_KEY)
    articles_dict = api.get_everything(sources='google-news,techcrunch,msnbc,bbc-sport,business-insider,cnn,entertainment-weekly,financial-times,financial-post,mtv-news,the-economist,the-guardian-uk')

    articles = articles_dict['articles']
    # print(articles)
    for article in articles:
        article["category"] = find_category(article["title"], vectorizer, encoder, keywords, classifier)

    relevant_articles = list(filter((lambda x : category == x["category"]), articles))
    return relevant_articles


def newsfeed(request):
    # print("REMOVE THIS ONCE DEBUGGING IS DONE!!!\n")
    category = 't'
    if(request.GET.get('techbtn')):
        category = 't'
    elif(request.GET.get('medicalbtn')):
        category = 'm'
    elif(request.GET.get('businessbtn')):
        category = 'b'
    elif(request.GET.get('enterbtn')):
        category = 'e'

    articles = get_news_articles(category)
    # print('articles :: ',articles)

    # args['articles'] = articles
    article_dict = {}
    for article in articles:
        dt = parse(str(article['publishedAt']))
        dt = dt.strftime('%h %d, %Y')
        article_dict[str(article['title'])] = (str(article['url']), str(dt),
        str(article['source']['name']))

    return render(request, 'newsapp/newsfeed.html', {'article_list': article_dict})




'''
newsapi sources

abc-news
abc-news-au
aftenposten
al-jazeera-english
ansa
argaam
ars-technica
ary-news
associated-press
australian-financial-review
axios
bbc-news
bbc-sport
bild
blasting-news-br
bleacher-report
bloomberg
breitbart-news
business-insider
business-insider-uk
buzzfeed
cbc-news
cbs-news
cnbc
cnn
cnn-es
crypto-coins-news
daily-mail
der-tagesspiegel
die-zeit
el-mundo
engadget
entertainment-weekly
espn
espn-cric-info
financial-post
financial-times
focus
football-italia
fortune
four-four-two
fox-news
fox-sports
globo
google-news
google-news-ar
google-news-au
google-news-br
google-news-ca
google-news-fr
google-news-in
google-news-is
google-news-it
google-news-ru
google-news-sa
google-news-uk
goteborgs-posten
gruenderszene
hacker-news
handelsblatt
ign
il-sole-24-ore
independent
infobae
info-money
la-gaceta
la-nacion
la-repubblica
le-monde
lenta
lequipe
les-echos
liberation
marca
mashable
medical-news-today
metro
mirror
msnbc
mtv-news
mtv-news-uk
national-geographic
nbc-news
news24
new-scientist
news-com-au
newsweek
new-york-magazine
next-big-future
nfl-news
nhl-news
nrk
politico
polygon
rbc
recode
reddit-r-all
reuters
rt
rte
rtl-nieuws
sabq
spiegel-online
svenska-dagbladet
t3n
talksport
techcrunch
techcrunch-cn
techradar
the-economist
the-globe-and-mail
the-guardian-au
the-guardian-uk
the-hill
the-hindu
the-huffington-post
the-irish-times
the-lad-bible
the-new-york-times
the-next-web
the-sport-bible
the-telegraph
the-times-of-india
the-verge
the-wall-street-journal
the-washington-post
time
usa-today
vice-news
wired
wired-de
wirtschafts-woche
xinhua-net
ynet

'''
