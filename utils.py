# coding=utf-8
import urllib.request
import json
import pprint

# helpers
pp = pprint.PrettyPrinter(indent=4)

def fetching(name: str):
    return "Getting info on **" + name.capitalize() + "**."

def getJSONFromPokeapi(url):
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
        return str("I couldn't find **" + name.capitalize() + "** in the database! :( Pleazzze try again...")
    elif code >= 500:
        return "I can't reach the databazzze right now. Try again later...'"

# capitalize all words in a string
def titlecaps(words: str):
    return " ".join([word.capitalize() for word in words.split()])

# all of an individual pkmn's abilities
def list_abilities(abilities: list):
    ablt = []
    ability_str = ""
    for ability in abilities:
        ability_str = titlecaps(ability['ability']['name'].replace("-", " "))
        if ability['is_hidden']:
            ability_str += " (HA)"
        ablt.append(ability_str)
    return ablt

def gender_str(rate: int):
    if (rate < 0):
        return "**Genderless**"
    return "**\u2642`** "+ repr((1-rate/8)*100) + "%` :: **\u2640** `" + repr(rate/8*100) + "%`"

def pkmnWithAbilStr(pkmn: list):
    pkmn_strs = []
    for item in pkmn:
        pkmn_str = item['pokemon']['name'].capitalize()
        if item['is_hidden']:
            pkmn_str += " (HA)"
        pkmn_strs.append(pkmn_str)

    return pkmn_strs
