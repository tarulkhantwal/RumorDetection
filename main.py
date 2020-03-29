from bs4 import BeautifulSoup
import requests
import spacy
import tweepy
import rake

import os
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
key = os.getenv("key")
secret = os.getenv("secret")

consumer_key = key
consumer_secret = secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

urlstart = "http://www.thesaurus.com/browse/"
urlend = "?s=t"
#nlp = spacy.load("en")
nlp = spacy.load("en_core_web_lg")
def antonym_finder(word):
    print(word)
	
    url = urlstart + word + urlend
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    try:
        data = soup.find('ul', { "class" : "css-1lc0dpe et6tpn80" })
        data= data.find_all('li')
    except:
        data=""
    antonyms = []
    counter = 0
    for w in data:
        if counter == 0:
            counter += 1
            continue
        antonyms.append(w.text)
    return antonyms

def extract_nouns(sentence):
    nouns = []
    words = sentence.split(' ')
    for w in words:
        nouns.append(w)
    return nouns

def get_tweet(id):
    tweet_text = api.get_status(id)
    return tweet_text

def get_relatable_tweets(keywords):
    tweets = api.search(keywords[0])
    all_tweets_text = []
    for t in tweets:
        all_tweets_text.append(t.text)
    return all_tweets_text

def get_keywords(tweet):
    stop_path = "shop_txt.txt"
    rake_obj = rake.Rake(stop_path, 1, 1, 1)
    return rake_obj.run(tweet)

def issimilar(sentence1, sentence2):
    similarity = 0
    nouns1 = extract_nouns(sentence1)
    nouns2 = extract_nouns(sentence2)
    for x in nouns1:
        for y in nouns2:
            _x = nlp(u''+x)
            _y = nlp(u''+y)
            if _x.similarity(_y) > 0.3:
                similarity += 1;
    if(similarity > 0.3):
        return 1
    return 0

def isantonympair(word1, word2):
    antonym1 = antonym_finder(word1)
    for an1 in antonym1:
        if an1 == word2:
            return 1
    return 0

def iscontradicts(sentence1, sentence2):
    antonymcount = 0
    nouns1 = extract_nouns(sentence1)
    nouns2 = extract_nouns(sentence2)
    for x in nouns1:
        for y in nouns2:
            if isantonympair(x,y) == 1:
                antonymcount += 1;
    if antonymcount >= 1:
        return 1
    else:
        return 0

#................. Code Entry Here...............#
#get tweet id
id = input("Enter the tweet ID: ")

#variable for calculating amount of contradiction
contradict = 0

#getting tweet text using id
tweet_text = get_tweet(id).text

keywords = get_keywords(tweet_text)

tweets = get_relatable_tweets(keywords)
II=0
#check how many contradicts
print(len(tweets))
for t in tweets:
    if(II == 2):
        break
    II+=1
    if (issimilar(tweet_text, t) == 1) and iscontradicts(tweet_text, t) == 1:
        contradict += 1
#len(tweet)
if (contradict/2) >= 0.3:
    print ("Taruls AI says the tweet might be a rumor")
else:
    print ("Taruls AI says the Tweet is not a rumour..")

