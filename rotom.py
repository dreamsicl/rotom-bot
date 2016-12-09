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

client = discord.Client()

# grab info from pokeapi
pokeapi = "http://pokeapi.co/api/v2/"


def getJSON(url):
    logging.info("getJSON(): currURL=%s" % url)

    # init request to pokeapi, set headers
    req = urllib.request.Request(url,
                                 data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                                          })
    try: response = urllib.request.urlopen(req)
    except urllib.request.HTTPerror as e:
        print(e.code)
        print(e.read())
        return False
    else:
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

    if move:
        move['name'] = [name['name'] for name in move['names'] if name['language']['name'] == "en"][0]

        flavor_text = [text['flavor_text'] for text in move['flavor_text_entries'] if text['language']['name'] == "en"][0]

        say_move = "**MOVE: " + move["name"].upper() + "**" + \
            "\n\n__Type:__ `" + move["damage_class"]["name"].upper() + "`, `" + move["type"]["name"].upper() + \
            "`\n__Power:__ `" + repr(move["power"]) + "`\t__PP:__ `" + repr(move["pp"]) + "`\t__Accuracy:__ `" + repr(move["accuracy"]) + "`\t__Priority:__ `" + repr(move['priority']) + \
            "`\n\n__Description:__ `" + flavor_text + "`"

    else: 
        say_move = "Couldn't' find " + move + " in the database! (ू˃̣̣̣̣̣̣︿˂̣̣̣̣̣̣ ) Please try again... "

    await bot.say(say_move)

@bot.command()
async def ttype(ttype: str):

    ttype = getJSON(pokeapi + "type/" + ttype.strip().lower())

    if ttype:
        delimiter = "`, `"
        super_on = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['double_damage_to']])
        weak = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['double_damage_from']])
        resist = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['half_damage_from']])
        not_on = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['half_damage_to']])
        no_dmg_to = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['no_damage_to']])
        no_dmg_from = delimiter.join([item['name'].upper() for item in ttype['damage_relations']['no_damage_from']])

        say_type = "**TYPE: " + ttype["name"].upper() + "**\n\n"
        if super_on:
            say_type += "Super Effective on: `" + super_on + "`\n"
        if not_on:
            say_type += "Not Very Effective on: `" + not_on + "`\n"
        if resist:
            say_type += "Resists: `" + resist + "`\n"
        if weak:
            say_type += "Weak to: `" + weak + "`\n"
        if no_dmg_from:
            say_type += "No damage from: `" + no_dmg_from + "`\n"
        if no_dmg_to:
            say_type += "No damage to: `" + no_dmg_to + "`\n"
    
    else:
        say_type = "Couldn't' find " + ttype + " in the database! (ू˃̣̣̣̣̣̣︿˂̣̣̣̣̣̣ ) Please try again... "

    await bot.say(say_type)

@bot.command()
async def pokemon(pokemon: str):
    pokemon = getJSON(pokeapi + "pokemon/" + pokemon.strip().lower())
    if pokemon:
        say_pokemon = "**POKEMON: " + pokemon["name"].upper() + "**\n"
        
        # TYPES
        say_pokemon += "Type: `" + "`, ".join([item['type']['name'] for item in pokemon['types']]) + "`\n"

        # BASE STATS
        for item in pokemon["stats"]:
            if item['stat']['name'] == 'hp':
                hp = repr(item["base_stat"])
            if item['stat']['name'] == 'attack':
                attack = repr(item["base_stat"])
            if item['stat']['name'] == 'defense':
                defense = repr(item["base_stat"])
            if item['stat']['name'] == 'special-attack':
                sp_attack = repr(item["base_stat"])
            if item['stat']['name'] == 'special-defense':
                sp_defense = repr(item["base_stat"])
            if item['stat']['name'] == 'speed':
                speed = repr(item["base_stat"])

        say_pokemon += "**BASE STATS:**  HP: `" + hp + "`   |   " + \
            "Atk: `" + attack + "`   |   " + \
            "Def: `" + defense + "`   |   " + \
            "SpAtk: `" + sp_attack + "`   |   " + \
            "SpDef: `" + sp_defense + "`   |   " + \
            "Spd: `" + speed + "`"

        # TODO: height, weight, nickname, abilities, evolution line, evolution method
    
    else: 
        say_pokemon = "Couldn't' find " + pokemon + " in the database! (ू˃̣̣̣̣̣̣︿˂̣̣̣̣̣̣ ) Please try again... "

    await bot.send_file(channel, pokemon['sprites']['front_default'])
    await bot.say(say_pokemon)


bot.run('MjQ5MjUyNDkzMDg1NzY5NzI4.CxEnMA.5EJhgAM_yeHAmLDvI-676afmYLE')
