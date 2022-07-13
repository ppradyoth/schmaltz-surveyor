from matplotlib.pyplot import twinx
from helpers.twitter import TwitterClient as tw
from helpers.googleNLPAPI import sentimentAnalyze
from flask import Flask, render_template, url_for, request
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
GOOGLE_APPLICATION_CREDENTIALS=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        twitter = tw()
        tweets = twitter.get_tweets(request.form['topic'], maxTweets=int(request.form['nResult']))
        print(f'{len(tweets)} tweets fetched')
        for i in tweets:
            i['sentiment'] = sentimentAnalyze(i['text'])
        return render_template('result.html', topic=request.form['topic'], tweets=tweets)

if __name__ == '__main__':
    app.run(debug=True)
