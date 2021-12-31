
from PIL import Image, ImageDraw, ImageFont
from argparse import ArgumentParser
import random, textwrap

def go(arg):

    # load the strategies
    with open('strategies.txt', 'r') as file:
        lines = file.readlines()

    # pick a random one
    if arg.id is None:
        strategy = random.choice(lines)
    else:
        strategy = lines[arg.id]

    strategy = strategy.replace('\\n', '\n')
    strategy = '\n'.join(textwrap.wrap(strategy, width=30, replace_whitespace=False))
    print(strategy)

    img = Image.new('RGB', (1280, 720), color=(255, 255, 255))

    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("Roboto-Medium.ttf", 80)
    d.multiline_text((100, 83), strategy, font=fnt, spacing=30, fill=(0, 0, 10))

    img.save('final.png')

    print('done')

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

