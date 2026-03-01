import tweepy
import os

def post_tweet(text):
    client = tweepy.Client(
        bearer_token=os.getenv("BEARER_TOKEN"),
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_SECRET")
    )
    client.create_tweet(text=text)

def main():
    post_tweet("F1 bot test successful 🏎️🔥")

if __name__ == "__main__":
    main()
