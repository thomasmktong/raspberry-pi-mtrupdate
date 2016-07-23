from TwitterAPI import TwitterAPI
import threading
import re

class Twitter:

    # Get keys and secrets from https://apps.twitter.com/
    CONSUMER_KEY = 'xxx'
    CONSUMER_SECRET = 'xxx'
    ACCESS_TOKEN_KEY = 'xxx'
    ACCESS_TOKEN_SECRET = 'xxx'

    # Get twitter ID from https://tweeterid.com/
    THOMASMKTONG_TWITTER_ID = '238939375'
    MTRUPDATE_TWITTER_ID = '233829774'
    
    def __init__(self):
        self.max_messages = 10;
        self.messages = [];
        self.api = TwitterAPI(Twitter.CONSUMER_KEY,
                              Twitter.CONSUMER_SECRET,
                              Twitter.ACCESS_TOKEN_KEY,
                              Twitter.ACCESS_TOKEN_SECRET)


    def refresh(self):
        messages = [];
        tweets = self.api.request(
            'statuses/user_timeline',
            {'user_id': Twitter.MTRUPDATE_TWITTER_ID})
        
        for tweet in tweets:
            if('text' in tweet):
                text = tweet['text']
                if(text):
                    # not to process tweets which are in chinese
                    match_chinese = re.findall(u'[\u4e00-\u9fff]+', text)
                    if(len(match_chinese) == 0):
                        # remove links in tweets
                        text = re.sub(r'https?:\/\/.*', '', text)
                        messages.append(text)

        # store messages in ascending chronological order
        self.messages = list(reversed(messages))


    def stream(self, callback = None):
        while True:
            try:
                iterator = self.api.request(
                    'statuses/filter',
                    {'follow': Twitter.MTRUPDATE_TWITTER_ID})
                
                for item in iterator:
                    if 'text' in item:
                        text = item['text']
                        if(text):
                            # not to process tweets which are in chinese
                            match_chinese = re.findall(u'[\u4e00-\u9fff]+', text)
                            if(len(match_chinese) == 0):
                                # remove links in tweets
                                text = re.sub(r'https?:\/\/.*', '', text)

                                # add to the end, remove front if too many
                                self.messages.append(text)
                                
                                while len(self.messages) > self.max_messages:
                                    self.messages.pop(0)

                                # invoke callback
                                if(callback):
                                    callback(self.messages)
                                else:
                                    print(self.messages)
                                    
                    elif 'disconnect' in item:
                        event = item['disconnect']
                        if event['code'] in [2,5,6,7]:
                            # something needs to be fixed before re-connecting
                            raise Exception(event['reason'])
                        else:
                            # temporary interruption, re-try request
                            break
            except TwitterRequestError as e:
                if e.status_code < 500:
                    # something needs to be fixed before re-connecting
                    raise
                else:
                    # temporary interruption, re-try request
                    pass
            except TwitterConnectionError:
                # temporary interruption, re-try request
                pass


    def stream_async(self, callback = None):
        self.thread = threading.Thread(target=self.stream, args=[callback])
        self.thread.start()


# when this file executed individually, run test
if(__name__ == "__main__"):

    twitter = Twitter()
    twitter.refresh()
    twitter.stream_async()

    print('first set of message get using refresh:')
    print(twitter.messages)

    print('after stream:')
