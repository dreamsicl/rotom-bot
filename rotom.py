import discord
from discord.ext import commands
import pprint
import logging
import sys
import traceback
import asyncio
from collections import Counter

with open("utils.py") as f:
    exec(f.read())

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

pokeapi = "http://pokeapi.co/api/v2/"

description = '''Your trusty RotomDex!'''
bot = commands.Bot(command_prefix='!', description=description, help_attrs=dict(hidden=True))

@bot.event
async def on_ready():
    print('Logged in as', bot.user.name)
    print(bot.user.id)
    print('------')


# @bot.event
# def on_command(message):
#     bot.type()
    
    

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)

        traceback.print_tb(error.original.__traceback__)

        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
    elif isinstance(error, commands.TooManyArguments):
        await bot.say("You sent too many arguments!")



@bot.command()
async def move(*, move_name: str):
    """ Move description. Includes type, power, pp, and more. """    
    await bot.say(fetching(move_name))
    mv = getJSONFromPokeapi(pokeapi + "move/" + move_name.strip().lower().replace(" ", "-"))

    if isinstance(mv,dict):
        mv['name'] = [name['name'] for name in mv['names'] if name['language']['name'] == "en"][0]

        flavor_text = [text['flavor_text'] for text in mv['flavor_text_entries'] if text['language']['name'] == "en"][0]

        say_move = "**MOVE: " + mv["name"].upper() + "** ```" + flavor_text + "```" + \
            "\n__Type:__ `" + mv["damage_class"]["name"].upper() + "`, `" + mv["type"]["name"].upper() + \
            "`\n__Power:__ `" + repr(mv["power"]) + "`\t__PP:__ `" + repr(mv["pp"]) + "`\t__Accuracy:__ `" + repr(mv["accuracy"]) + "`\t__Priority:__ `" + repr(mv['priority']) + "`"

    else: 
        say_move = say_error(mv, titlecaps(move_name))

    await bot.edit_message(say_move)


@bot.command()
async def type(type_name: str):
    """ Type effectiveness info. """
    ttype = getJSONFromPokeapi(pokeapi + "type/" + type_name.strip().lower())

    if isinstance(ttype, dict):
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

    await bot.edit_message(say_type)

@bot.command(aliases=["pkmn"])
async def pokemon(pokemon_name: str):
    """ Pokedex entry. Includes base stats, breeding info, abilities, etc."""
    pkmn = getJSONFromPokeapi(pokeapi + "pokemon/" + pokemon_name.strip().lower())
    if isinstance(pkmn,dict):
        species = getJSONFromPokeapi(pokeapi + "pokemon-species/" + pkmn['name'])
        
        genus = [item['genus'] for item in species['genera'] if item['language']['name'] == "en"][0]
        flavor_text = [item['flavor_text'] for item in species['flavor_text_entries'] if item['language']['name'] == "en"][0]

        say_pokemon = "**POKEMON: " + pkmn["name"].upper() + "**" + \
            "```markdown\n#" + repr(pkmn['id']) + " - The " + genus + " Pokemon\n" + flavor_text + "```\n"

        # TYPES / ABILITIES
        say_pokemon += "**Type:** `" + "`, `".join([item['type']['name'].upper() for item in pkmn['types']]) + "`   |   " + \
            "**Abilities:** `" + "`, `".join(list_abilities(pkmn['abilities'])) + "`\n\n"

        # BREEDING INFO
        say_pokemon += "**Gender:** " + gender_str(species['gender_rate']) + "   |   " + \
            "**Egg Groups:** `" + "`, `".join([item['name'].capitalize() for item in species['egg_groups']]) + "`   |   " + \
            "**Hatch Steps:** `" + repr(species['hatch_counter']*255) + "`\n\n"

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

        # BASE STATS
        say_pokemon += "**Base Stats:**  HP: `" + hp + "`   |   " + \
            "Atk: `" + attack + "`   |   " + \
            "Def: `" + defense + "`   |   " + \
            "SpAtk: `" + sp_attack + "`   |   " + \
            "SpDef: `" + sp_defense + "`   |   " + \
            "Spd: `" + speed + "`\n"

        # EVOLUTION TODO: evolution line, evolution method,
        # evolution = getJSONFromPokeapi(species['evolution_chain']['url'])
        # say_pokemon += "**Evolution:** " + evo_chain(evolution, evolution['chain']['species']['name'].capitalize())


        # TODO: height, weight, abilities,
    
    else: 
        say_pokemon = say_error(pkmn, pokemon_name)

    # await bot.upload(str(pkmn['sprites']['front_default']))
    await bot.say(say_pokemon)

# TODO: abilities, egg group command
@bot.command()
async def ability(*, ability_name: str):
    """ Ability description and Pokemon who have it."""
    abil = getJSONFromPokeapi(pokeapi + "ability/" + ability_name)

    if isinstance(abil, dict):
        say_abil = "**ABILITY: " + abil['name'].upper() + "**"

        effect_entry = [item['effect'] for item in abil['effect_entries'] if item['language']['name'] == "en"][0]
        say_abil += "```" + effect_entry + "```\n"

        say_abil += "**Pokemon with " + abil['name'].capitalize() + ":** `" + \
            "`, `".join(pkmnWithAbilStr(abil['pokemon'])) + "`"

    
    else:
        say_abil = say_error(abil, ability_name)
    
    await bot.say(say_abil)

# run bot
# if __name__ == '__main__':
with open("credentials.json") as f:
    token = json.load(f)['token']
bot.commands_used = Counter()
bot.run(token)
bot.logout()
bot.close()
# loop = asyncio.get_event_loop()
# try:
#     loop.run_until_complete()
# except Exception:
#     loop.run_until_complete(bot.logout())
# finally:
#     loop.close()