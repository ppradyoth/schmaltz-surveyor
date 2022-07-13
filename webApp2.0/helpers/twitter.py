import tweepy
from tweepy import OAuthHandler
import os
from dotenv import load_dotenv
load_dotenv()


ACCESS_TOKEN=os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=os.getenv('ACCESS_TOKEN_SECRET')
CONSUMER_KEY=os.getenv('CONSUMER_KEY')
CONSUMER_SECRET=os.getenv('CONSUMER_SECRET')
class TwitterClient(object):
    def __init__(self):
        #Initialization method.
        try:
            # create OAuthHandler object
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            # set access token and secret
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            # create tweepy API object to fetch tweets
            # add hyper parameter 'proxy' if executing from behind proxy "proxy='http://172.22.218.218:8085'"
            self.api=tweepy.API(auth)
            # self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
           
        except Exception as err:
            print(f"Error: Tweeter Authentication Failed - \n{str(err)}")

    def get_tweets(self, query, maxTweets = 1000):
        #Function to fetch tweets.
        # empty list to store parsed tweets
        tweets = []
        sinceId = None
        max_id = -1
        tweetCount = 0
        tweetsPerQry = 100 if maxTweets > 100 else maxTweets

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
                    parsed_tweet['text'] = tweet.full_text
                    parsed_tweet['user'] = {
                        'name': tweet.user.screen_name,
                        'description': tweet.user.description
                    }
                    if len(tweet.entities['urls']) > 0:
                        parsed_tweet['url'] = tweet.entities['urls'][0]['url']

                    # appending parsed tweet to tweets list
                    if tweet.retweet_count > 0:
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)
                tweetCount = len(tweets)
            except Exception as err:
                # Just exit if any error
                print("Tweepy error : " + str(err))
                break
        return tweets