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
    # init request to pokeapi, set headers
    req = urllib.request.Request(url,
                                 data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                                          })
    try: response = urllib.request.urlopen(req)
    except urllib.request.HTTPError as e:
        if e.code() >= 500:
            return "щ(`Д´щ;) I can't reach the databazzze! Try again later..."
        if e.code() >= 400 and e.code() < 500:
            return "I couldn't find your request in the databazzze! (ू˃̣̣̣̣̣̣︿˂̣̣̣̣̣̣ ) Please try again... "
    else:
        data = response.read()
        data = "".join(map(chr, data))
        data = json.loads(data)
        return data


# begin bot commands
description = '''Your trusty RotemDex!'''
bot = commands.Bot(command_prefix='!', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def move(*, name: str):
    """ Pokemon move description """
    name = name.strip().lower().replace(" ", "-")
    move = getJSON(pokeapi + "move/" + name)

    if move is dict:
        move['name'] = [name['name'] for name in move['names'] if name['language']['name'] == "en"][0]

        flavor_text = [text['flavor_text'] for text in move['flavor_text_entries'] if text['language']['name'] == "en"][0]

        say_move = "**MOVE: " + move["name"].upper() + "**" + \
            "\n\n__Type:__ `" + move["damage_class"]["name"].upper() + "`, `" + move["type"]["name"].upper() + \
            "`\n__Power:__ `" + repr(move["power"]) + "`\t__PP:__ `" + repr(move["pp"]) + "`\t__Accuracy:__ `" + repr(move["accuracy"]) + "`\t__Priority:__ `" + repr(move['priority']) + \
            "`\n\n__Description:__ `" + flavor_text + "`"

    else:
        say_move = move

    await bot.say(say_move)


@bot.command()
async def type(ttype: str):

    ttype = getJSON(pokeapi + "type/" + ttype.strip().lower())

    if ttype is dict:
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
        say_type = ttype

    await bot.say(say_type)

# recursively get evo chain     
def evo_chain(chain, species):
    if chain['evolves_to']:
        species += " > " + " / ".join([evo[name].capitalize() for evo in chain['evolves_to']])
        return evo_chain(chain['evolves_to'])

    return species


@bot.command()
async def pokemon(name: str):
    pokemon = getJSON(pokeapi + "pokemon/" + name.strip().lower())
    if pokemon is dict:
        species = getJSON(pokeapi + "pokemon-species/" + name.strip().lower())

        genus = [item['genus']for item in species['genera'] if item['language']['name'] == "en"][0]
        flavor_text = [item['flavor_text'] for item in species['flavor_text_entries'] if item['version']['name'] == "alpha-sapphire" and item['language']['name'] == "en"][0]
        
        say_pokemon = "**POKEMON: " + pokemon["name"].upper() + "**\n" + \
            "``` markdown \n#" + str(pokemon["id"]) + " - The " + genus + " Pokémon\n" + flavor_text + "```\n"
        

        # TYPES
        say_pokemon += "**Type:**   `" + "`, ".join([item['type']['name'] for item in pokemon['types']]).upper() + "`\n"

        # EGG GROUPS / HATCH STEPS
        say_pokemon += "**Egg Group(s):**   `" + "`, ".join([item['name'] for item in species['egg_groups']]).upper() + \
            "**Steps to Hatch:**   `" + repr(species['hatch_counter']*255) + "`\n"

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

        say_pokemon += "**Base Stats:**  HP: `" + hp + "`   |   " + \
            "Atk: `" + attack + "`   |   " + \
            "Def: `" + defense + "`   |   " + \
            "SpAtk: `" + sp_attack + "`   |   " + \
            "SpDef: `" + sp_defense + "`   |   " + \
            "Spd: `" + speed + "`\n"

        # EVOLUTION TODO: evolution line, evolution method,
        evolution = getJSON(species['evolution_chain']['url'])
        say_pokemon += "**Evolution:** " + evo_chain(evolution, evolution['chain']['species']['name'].capitalize())


        # TODO: height, weight, abilities,
    
    else: 
        say_pokemon = pokemon

    # await bot.upload(str(pokemon['sprites']['front_default']))
    await bot.say(say_pokemon)

# TODO: abilities, egg group command
bot.run('MjQ5MjUyNDkzMDg1NzY5NzI4.CxEnMA.5EJhgAM_yeHAmLDvI-676afmYLE')
