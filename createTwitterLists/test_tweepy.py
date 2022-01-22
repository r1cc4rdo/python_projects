"""
Keys obtained from https://developer.twitter.com/
after registering for a developer account.
"""
import json
import tweepy

api = None


def create_api_endpoint(secrets):
    global api
    auth = tweepy.OAuthHandler(secrets['api_key'], secrets['api_secret_key'])
    auth.set_access_token(secrets['access_token'], secrets['access_secret_token'])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def print_following():
    for index, friend in enumerate(tweepy.Cursor(api.friends).items()):
        print(f'{index:4d}: @{friend.screen_name} ({friend.name})')


def print_tweets():
    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)


def create_lists():
    with open('lists.json', 'r') as json_in:
        lists = json.load(json_in)

    total_count = 0
    for list_name, list_members in lists.items():
        print(f'Creating {list_name} ({len(list_members)} handles)')
        list_obj = api.create_list(list_name)
        for index, screen_name in enumerate(list_members):
            print(f'\t{index + 1:4d}: {screen_name}')
            api.add_list_member(screen_name=screen_name, list_id=list_obj.id)
            total_count += 1

    print(f'Added a total of {total_count} handles in {len(lists)} lists')


if __name__ == '__main__':
    with open('secrets.json', 'r') as json_in:
        create_api_endpoint(json.load(json_in))
        create_lists()
