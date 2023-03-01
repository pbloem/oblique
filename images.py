
from PIL import Image, ImageDraw, ImageFont
from argparse import ArgumentParser
import random, textwrap

import requests, sys, os, time, yaml
from requests_oauthlib import OAuth1

import mastodon
from mastodon import Mastodon

def go(arg, twitter=True, mastodon=True):

    # load the strategies
    with open('strategies.txt', 'r') as file:
        lines = file.readlines()

    # pick a random one
    if arg.id is None:
        strategy = random.choice(lines)
    else:
        strategy = lines[arg.id]

    strategy_orig = strategy

    strategy = strategy.replace('\\n', '\n')
    strategy = '\n'.join(textwrap.wrap(strategy, width=30, replace_whitespace=False))
    print(strategy)

    img = Image.new('RGB', (1280, 720), color=(255, 255, 255))

    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("Roboto-Medium.ttf", 80)
    d.multiline_text((100, 83), strategy, font=fnt, spacing=30, fill=(0, 0, 10))

    img.save('final.png')

    print('Image created')

    """
    Post the image final.png to the obliquademia twitter account.
    
    """

    if twitter:


        def check(r):
            if r.status_code < 200 or r.status_code > 299:
                print(r.status_code, r.reason)
                print(r.text)
                sys.exit()


        # Creds for @obliquademia
        if os.path.exists('auth.twitter.yaml'):
            creds = yaml.safe_load(open('auth.twitter.yaml', 'r'))
        else:
            creds = {
                'app_key' : os.environ['APPKEY'],
                'app_secret' : os.environ['APPSECRET'],
                'user_key' : os.environ['USERKEY'],
                'user_secret' : os.environ['USERSECRET']
            }

        auth = OAuth1(
            creds['app_key'], # app key
            creds['app_secret'], # app secret
            creds['user_key'], # user key
            creds['user_secret'] # user secret
        )

        # Upload the image (chunked upload)

        URL = 'https://upload.twitter.com/1.1/media/upload.json'

        filename = 'final.png'
        mime = 'image/png'

        file = open(filename, 'rb')
        total_bytes = os.path.getsize(filename)

        ## INIT

        data = {
              'command': 'INIT',
              'media_type': mime,
              'total_bytes': total_bytes,
              'media_category': 'tweet_image'
            }

        r = requests.post(URL, data=data, auth=auth)

        check(r)

        if 'media_id' in r.json():
            media_id = r.json()['media_id']
        else:
            raise Exception('Media id not found. Response ', r.json())

        # APPEND

        bytes_sent = 0
        segment_id = 0
        while bytes_sent < total_bytes:
            print('appending')

            data = {
                'command': 'APPEND',
                'media_id': media_id,
                'segment_index': segment_id
            }

            files = {
                'media': file.read(4 * 1024 * 1024)
            }

            r = requests.post(url=URL, data=data, files=files, auth=auth)
            check(r)

            segment_id += 1
            bytes_sent = file.tell()

            print(f'{bytes_sent/1024:.5} of {total_bytes/1024:.5} kbytes uploaded')

        # FNALIZE

        data = {
          'command': 'FINALIZE',
          'media_id': media_id
        }

        print('finalizing')
        r = requests.post(url=URL, data=data, auth=auth)
        check(r)
        print('FINALIZE', r.json())

        # Add alt text to image

        URL = 'https://upload.twitter.com/1.1/media/metadata/create.json'
        data = {
            'media_id': media_id,
            'alt_text': {
                'text': strategy_orig
            }
        }

        r = requests.post(URL, json=data, auth=auth)
        check(r)

        # Post the tweet
        URL = 'https://api.twitter.com/1.1/statuses/update.json'
        data = {'status' : f'', 'media_ids' : media_id}

        r = requests.post(URL, data=data, auth=auth)
        print(r.status_code, r.reason)
        print(r.json())

    """
    Post the image final.png to the obliquademia mastodon account.

    """

    if mastodon:

        # Creds for @obliquademia
        if os.path.exists('auth.mastodon.yaml'):
            creds = yaml.safe_load(open('auth.mastodon.yaml', 'r'))
        else:
            creds = {
                'maccess_token': os.environ['MACCESS_TOKEN']
            }

        m = Mastodon(access_token=creds["maccess_token"], api_base_url="https://botsin.space")

        metadata = m.media_post('final.png', mime_type='image/png', description=strategy)
        # -- response format: https://mastodonpy.readthedocs.io/en/stable/#media-dicts

        m.status_post("", media_ids=metadata['id'])

if __name__ == "__main__":

    ## Parse the command line options
    parser = ArgumentParser()

    parser.add_argument("--id",
                        dest="id",
                        help="ID (line number) of the card. If none, a random one is chosen.",
                        default=None, type=int)

    # parser.add_argument("--time",
    #                     dest="time",
    #                     help="Runtime in minutes.",
    #                     default=60, type=int)

    options = parser.parse_args()

    print('OPTIONS ', options)

    go(options)

