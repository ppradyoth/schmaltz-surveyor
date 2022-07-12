from flask import Flask,render_template,url_for,request
import pickle
import numpy as np
import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
import tweepy
from tweepy import OAuthHandler 
# consumer_key="nKYTHw8FJ45dtxKbnURY7Nvuz"
# consumer_secret="GxOl2B8DdpNZHOHyuXC3t532bQxFCGQ21fCaBhPGYVfnctY8fF"
# access_token="1539172679416066048-wdwJRdNyA3f6rWwdZYfVaUv3R8U4PQ"
# access_token_secret="Me6aRljMhOSQUUcHQSQrIISbVIvxvQiOmLrUtmIblkLPR"
access_token="1539172679416066048-wdwJRdNyA3f6rWwdZYfVaUv3R8U4PQ"
access_token_secret="Me6aRljMhOSQUUcHQSQrIISbVIvxvQiOmLrUtmIblkLPR"
consumer_key="nKYTHw8FJ45dtxKbnURY7Nvuz"
consumer_secret="GxOl2B8DdpNZHOHyuXC3t532bQxFCGQ21fCaBhPGYVfnctY8fF"
app = Flask(__name__)
@app.route('/result')
@app.route('/home')
@app.route('/')
def home():
	return render_template('home.html')
@app.route('/predict',methods=['POST'])
def predict():
  class TwitterClient(object): 
    def __init__(self): 
        #Initialization method. 
        try: 
            # create OAuthHandler object 
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            # add hyper parameter 'proxy' if executing from behind proxy "proxy='http://172.22.218.218:8085'"
            self.api=tweepy.API(auth)
            # self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            
        except tweepy.errors.TweepError as e:
            print(f"Error: Tweeter Authentication Failed - \n{str(e)}")

    def get_tweets(self, query, maxTweets = 100):
        #Function to fetch tweets. 
        # empty list to store parsed tweets 
        tweets = [] 
        sinceId = None
        max_id = -1
        tweetCount = 0
        tweetsPerQry = 100

        while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    if (not sinceId):
                        new_tweets = self.api.search_tweets(q=query, count=tweetsPerQry,tweet_mode='extended',lang = "en")
                    else:
                        new_tweets = self.api.search_tweets(q=query, count=tweetsPerQry,
                                                since_id=sinceId,tweet_mode='extended',lang = "en")
                else:
                    if (not sinceId):
                        new_tweets = self.api.search_tweets(q=query, count=tweetsPerQry,
                                                max_id=str(max_id - 1),tweet_mode='extended',lang = "en")
                    else:
                        new_tweets = self.api.search_tweets(q=query, count=tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=sinceId,tweet_mode='extended',lang = "en")
                if not new_tweets:
                    print("No more tweets found")
                    break

                for tweet in new_tweets:
                    parsed_tweet = {} 
                    parsed_tweet['tweets'] = tweet.full_text 

                    # appending parsed tweet to tweets list 
                    if tweet.retweet_count > 0: 
                        # if tweet has retweets, ensure that it is appended only once 
                        if parsed_tweet not in tweets: 
                            tweets.append(parsed_tweet) 
                    else: 
                        tweets.append(parsed_tweet) 
                        
                tweetCount += len(new_tweets)
                print("Downloaded {0} tweets".format(tweetCount))
                max_id = new_tweets[-1].id

            except tweepy.errors.TweepError as e:
                # Just exit if any error
                print("Tweepy error : " + str(e))
                break
        
        return pd.DataFrame(tweets)
  def remove_pattern(input_txt, pattern):                                           #function to remove pattern 
      r = re.findall(pattern, input_txt)
      for i in r:
          input_txt = re.sub(i, '', input_txt)        
      return input_txt
  def clean_tweets(lst):
      lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")                         # removing RT @x from tweets:
      lst = np.vectorize(remove_pattern)(lst, "@[\w]*")                             # removing  @xxx from tweets 
      lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")            # reremoving URL links http://xxx
      print (lst)
      return lst
    
  def con1(sentence):
    emotion_list = []
    sentence = sentence.split(' ')
    with open('emotions.txt','r') as file:
      for line in file:
        clear_line = line.replace("\n", '').replace(",",'').replace("'",'').strip()
        word, emotion = clear_line.split(':')
        if word in sentence:
          emotion_list.append(emotion)
      return emotion_list
  d=pd.read_csv('App.csv')
  d.head()
  x = d.iloc[:,-2].values
  d.head()
  tv = TfidfVectorizer(max_df=0.90, min_df=2, stop_words='english',ngram_range=(1, 2),max_features=23252)
  print(tv)
  x = tv.fit_transform(x.astype('U'))
#   print(tv.transform([tweet]).toarray())
#   pickle_in = open("App.pickle","rb") 
  pickle_in= open("randomforest.pickle","rb")
  classifier1 = pickle.load(pickle_in)
#   classifier1.fit()
  print(classifier1)
  if request.method == 'POST':
    comment = request.form['Tweet']
    twitter_client = TwitterClient()
    tweets_df = twitter_client.get_tweets(comment, maxTweets=1000)                           
    tweets_df['len']=tweets_df["tweets"].str.len()                       
    df1= tweets_df[(tweets_df['len'] <=137)]
    df2=tweets_df[(tweets_df['len'] >=150)]
    data=pd.concat([df1,df2])                              
    data = data.sample(frac=1).reset_index(drop=True)      
    data['clean']=clean_tweets(data['tweets']) 
    data['clean']=data['clean'].str.replace("[^a-zA-Z ]", " ")
    tweets = []
    ops = []
    for i,tweet in enumerate(data['clean']):
      print(tv.transform([tweet]).toarray())
      X=tv.transform([tweet]).toarray()
      op=classifier1.predict(X)
      if op == [0]:
        tweets.append(data.tweets[i])
        ops.append('Negative') 
      if op == [1]:
        tweets.append(data.tweets[i])
        ops.append('Positive')
      if op == [2]:
        tweets.append(data.tweets[i])
        ops.append('Neutral')
    output=dict(zip(tweets,ops))
    Neucount = ops.count('Neutral')
    Negcount = ops.count('Negative')
    Poscount = ops.count('Positive')
    # emo=con1(data['clean'].sum())
    # h=emo.count(' happy')
    # s=emo.count(' sad')
    # a=emo.count(' angry')
    # l=emo.count(' loved')
    # pl=emo.count(' powerless')
    # su=emo.count(' surprise')
    # fl=emo.count(' fearless')
    # c=emo.count(' cheated')
    # at=emo.count(' attracted')
    # so=emo.count(' singled out')
    # ax=emo.count(' anxious')
    # return render_template('result.html',outputs = output,NU=Neucount,N=Negcount,P=Poscount,happy=h,sad=s,angry=a,loved=l,powerless=pl,surprise=su,fearless=fl,cheated=c,attracted=at,singledout=so,anxious=ax)
    return render_template('result.html',outputs = output,NU=Neucount,N=Negcount,P=Poscount)
if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)