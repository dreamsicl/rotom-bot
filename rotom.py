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

# helpers
pokeapi = "http://pokeapi.co/api/v2/"
pp = pprint.PrettyPrinter(indent=4)

def getJSON(url):
    # init request to pokeapi, set headers
    req = urllib.request.Request(url,
                                 data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                                          })
    try: response = urllib.request.urlopen(req)
    except urllib.request.HTTPError as e:
        print(e.code, e.reason)
        return e.code
    except urllib.request.URLError as e:
        print(e.reason)
        return 0
    else:
        data = response.read()
        data = "".join(map(chr, data))
        data = json.loads(data)
        return data

# http error 
def say_error(code: int, name: str):
    if code > 400 and code < 500:
        return "I couldn't' find **" + name.capitalize() + "** in the database! (ू˃̣̣̣̣̣̣︿˂̣̣̣̣̣̣ ) Pleazzze try again..."
    elif code >= 500:
        return "I can't reach the databazzze right now. Try again later...'"

# parse error
def isnumber(thing):
    try: 
        float(thing)
        return True
    except Exception:
        return False

# capitalize all words in a string
def titlecaps(words: str):
    return " ".join([word.capitalize() for word in words.split()])

# all of an individual pkmn's abilities
def list_abilities(abilities: list):
    ablt = []
    ability_str = ""
    for ability in abilities:
        print(ability)
        ability_str = titlecaps(ability['ability']['name'].replace("-", " "))
        if ability['is_hidden']:
            ability_str += " (HA)"
        ablt.append(ability_str)
    return ablt

# begin bot commands
description = '''Your trusty RotemDex!'''
bot = commands.Bot(command_prefix='!', description=description, help_attrs=dict(hidden=True))

@bot.event
async def on_ready():
    print('Logged in as', bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def move(*, move_name: str):
    """ Move description. Includes type, power, pp, and more. """
    move_name = move_name.strip().lower().replace(" ", "-")
    mv = getJSON(pokeapi + "move/" + move_name)

    if not isnumber(mv):
        mv['name'] = [name['name'] for name in mv['names'] if name['language']['name'] == "en"][0]

        flavor_text = [text['flavor_text'] for text in mv['flavor_text_entries'] if text['language']['name'] == "en"][0]

        say_move = "**MOVE: " + mv["name"].upper() + "**" + \
            "\n\n__Type:__ `" + mv["damage_class"]["name"].upper() + "`, `" + mv["type"]["name"].upper() + \
            "`\n__Power:__ `" + repr(mv["power"]) + "`\t__PP:__ `" + repr(mv["pp"]) + "`\t__Accuracy:__ `" + repr(mv["accuracy"]) + "`\t__Priority:__ `" + repr(mv['priority']) + \
            "`\n\n__Description:__ `" + flavor_text + "`"

    else: 
        say_move = say_error(mv, titlecaps(move_name))

    await bot.say(say_move)


@bot.command()
async def type(type_name: str):
    """ Type effectiveness info. """
    ttype = getJSON(pokeapi + "type/" + type_name.strip().lower())

    if not isnumber(ttype):
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
        say_type = say_error(ttype, type_name)

    await bot.say(say_type)

@bot.command(aliases=["pkmn"])
async def pokemon(pokemon_name: str):
    """ Pokedex entry. Includes base stats, breeding info, abilities, and more."""
    pkmn = getJSON(pokeapi + "pokemon/" + pokemon_name.strip().lower())
    if not isnumber(pkmn):
        species = getJSON(pokeapi + "pokemon-species/" + pkmn['name'])

        genus = [item['genus'] for item in species['genera'] if item['language']['name'] == "en"][0]
        flavor_text = [item['flavor_text'] for item in species['flavor_text_entries'] if item['language']['name'] == "en"][0]

        say_pokemon = "**POKEMON: " + pkmn["name"].upper() + "**" + \
            "```markdown\n#" + repr(pkmn['id']) + " - The " + genus + " Pokemon\n" + flavor_text + "```\n"

        
        # TYPES / ABILITIES
        say_pokemon += "**Type:** `" + "`, `".join([item['type']['name'].capitalize() for item in pkmn['types']]) + "`   |   " + \
            "**Abilities:** `" + "`, `".join(list_abilities(pkmn['abilities'])) + "`\n\n"

        # TODO: BREEDING INFO: gender ratio, egg group, hatch steps

        # BASE STATS
        for item in pkmn["stats"]:
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
            "Spd: `" + speed + "`\n"

        # TODO: height, weight, nickname, abilities, evolution line, evolution method
    
    else: 
        say_pokemon = say_error(pkmn, pokemon_name)

    # await bot.upload(str(pkmn['sprites']['front_default']))
    await bot.say(say_pokemon)


bot.run('MjQ5MjUyNDkzMDg1NzY5NzI4.CxEnMA.5EJhgAM_yeHAmLDvI-676afmYLE')
bot.logout()
bot.close()