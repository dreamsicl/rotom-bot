import discord
from discord.ext import commands
import random
import urllib.request
import json
import pprint
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# grab info from pokeapi
pokeapi = "http://pokeapi.co/api/v2/"


def getJSON(url):
    logging.info("getJSON(): currURL=%s" % url)

    # init request to pokeapi, set headers
    req = urllib.request.Request(url,
                                 data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                                          })
    response = urllib.request.urlopen(req)

    data = response.read()
    data = "".join(map(chr, data))
    data = json.loads(data)
    return data


# begin bot commands
description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='!', description=description)


# @bot.event
# async def on_ready():
#     print('Logged in as')
#     print(bot.user.name)
#     print(bot.user.id)
#     print('------')


# @bot.command()
# async def add(left: int, right: int):
#     """Adds two numbers together."""
#     await bot.say(left + right)


# @bot.command()
# async def roll(dice: str):
#     """Rolls a dice in NdN format."""
#     try:
#         rolls, limit = map(int, dice.split('d'))
#     except Exception:
#         await bot.say('Format has to be in NdN!')
#         return

#     result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
#     await bot.say(result)


# @bot.command(description='For when you wanna settle the score some other way')
# async def choose(*choices: str):
#     """Chooses between multiple choices."""
#     await bot.say(random.choice(choices))


# @bot.command()
# async def repeat(times: int, content='repeating...'):
#     """Repeats a message multiple times."""
#     for i in range(times):
#         await bot.say(content)


# @bot.command()
# async def joined(member: discord.Member):
#     """Says when a member joined."""
#     await bot.say('{0.name} joined in {0.joined_at}'.format(member))


# @bot.group(pass_context=True)
# async def cool(ctx):
#     """Says if a user is cool.
#     In reality this just checks if a subcommand is being invoked.
#     """
#     if ctx.invoked_subcommand is None:
#         await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))


# @cool.command(name='bot')
# async def _bot():
#     """Is the bot cool?"""
#     await bot.say('Yes, the bot is cool.')


@bot.command()
async def move(*, name: str):
    """ Pokemon move description """
    name = name.strip().replace(" ", "-")
    move = getJSON(pokeapi + "move/" + name)

    # remove unnecessary keys for easier debugging
    # del move["flavor_text_entries"]
    # del move["names"]

    # pp.pprint(move)
    for name in move['names']:
        if name['language']['name'] = "en":
             move_name = name['language']['name']
    
    move['name'] = move_name
    
    sayMove = "''''" + move["name"].upper() + "'''" +
        "Damage Class: " + move["damage_class"]["name"] + "Type: " + move["type"]["name"] +
        "\nPower '" + repr(move["power"]) + "' PP '" + repr(move["pp"]) + "' Accuracy '" + repr(move["accuracy"]) + "'"

    # TODO: support multi-word move names

    await bot.say(name)


bot.run('MjQ5MjUyNDkzMDg1NzY5NzI4.CxEnMA.5EJhgAM_yeHAmLDvI-676afmYLE')
