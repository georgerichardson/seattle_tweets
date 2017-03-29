import json
import dataset
import tweepy
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

seatle_location = [-122.450238,47.434415,-122.213336,47.757275]

def store_tweet(tweet_dict):
    # set table
    table = db['tweets']
    table.insert(tweet_dict)

class SeattleStreamListener(tweepy.StreamListener, limit=None):
    def __init__(self, api=None):
        super(SeattleStreamListener, self).__init__()
        self.num_tweets = 0
        self.limit = limit
        
    def on_status(self, status):
        if self.limit:
            if self.num_tweets >= self.limit:
                print('\n \n Stored {} tweets {}'.format(limit, db))
                return False
        
        if hasattr(status, 'retweeted_status'):
            return

        else:
            self.num_tweets += 1
            #if print_to_notebook == 1:
            #    print(status.text)

            if hasattr(status, 'entities'):
                hashtags = []
                for tag in status.entities['hashtags']:
                    hashtags.append(tag['text'])
                hashtags = json.dumps(hashtags)

        tweet_dict = {
                    'description': status.user.description,
                    'loc': status.user.location,
                    'text': status.text,
                    'name': status.user.screen_name,
                    'user_created': status.user.created_at,
                    'followers': status.user.followers_count,
                    'id_str': status.id_str,
                    'retweet_count': status.retweet_count,
                    'friends_count': status.user.friends_count,
                    'favorite_count': status.favorite_count,
                    'hashtags': hashtags
                }

        store_tweet(tweet_dict)
            
    def on_error(self, status_code):
        '''Twitter is rate limiting, exit'''

        if status_code == 420:
            print('Twitter rate limit error_code {}, exiting...'.format(status_code))
            return False

def stream_location(location, db_name, limit=None):
    stream_listener = SeattleStreamListener(limit=limit)
    sapi = tweepy.Stream(auth=api.auth, listener=stream_listener)    
    db = dataset.connect('sqlite:///{}.sqlite'.format(db_name))
    sapi.filter(locations=location)