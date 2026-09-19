import tweepy
import datetime

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

while True:
    now = datetime.datetime.now()
    pi_time = datetime.time(15, 14)
    if now.time() == pi_time:
        api.update_status("It is PI time")

time.sleep(86400) # sleep for 24 hours