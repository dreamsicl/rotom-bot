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
    name = name.strip().lower().replace(" ", "-")
    move = getJSON(pokeapi + "move/" + name)

    # remove unnecessary keys for easier debugging
    # del move["flavor_text_entries"]
    # del move["names"]

    # pp.pprint(move['names'])
    move['name'] = [name['name'] for name in move['names'] if name['language']['name'] == "en"][0]

    flavor_text = [text['flavor_text'] for text in move['flavor_text_entries'] if text['language']['name'] == "en"][0]

    say_move = "**" + move["name"].upper() + "**" + \
        "\n\n__Type:__ `" + move["damage_class"]["name"].upper() + "`, `" + move["type"]["name"].upper() + \
        "`\n__Power:__ `" + repr(move["power"]) + "`\t__PP:__ `" + repr(move["pp"]) + "`\t__Accuracy:__ `" + repr(move["accuracy"]) + "`\t__Priority:__ `" + repr(move['priority']) + \
        "`\n\n__Description:__ `" + flavor_text + "`"

    await bot.say(say_move)

@bot.command()
async def ttype(ttype: str):
    ttype = ttype.strip().lower()
    ttype = getJSON(pokeapi + "type/" + ttype)

    delimiter = "`, `"
    super_on = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['double_damage_to']])
    weak = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['double_damage_from']])
    resist = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['half_damage_from']])
    not_on = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['half_damage_to']])
    no_dmg_to = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['no_damage_to']])
    no_dmg_from = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['no_damage_from']])

    say_type = "**" + ttype["name"].upper() + "**\n\n"
    if super_on:
        say_type += "**Super Effective On:** `" + super_on + "`\n"
    if not_on:
        say_type += "**Not Very Effective On:** `" + not_on + "`\n"
    if resist:
        say_type += "**Resists:** `" + resist + "`\n"
    if weak:
        say_type += "**Weak to:** `" + weak + "`\n"
    if no_dmg_from:
        say_type += "**No damage from:** `" + no_dmg_from + "`\n"
    if no_dmg_to:
        say_type += "**No damage to:** `" + no_dmg_to + "`\n"
    
    await bot.say(say_type)


bot.run('MjQ5MjUyNDkzMDg1NzY5NzI4.CxEnMA.5EJhgAM_yeHAmLDvI-676afmYLE')
