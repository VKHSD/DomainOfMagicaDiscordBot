#                    )      )   (      (      
#                 ( /(   ( /(   )\ )   )\ )   
#       (   (     )\())  )\()) (()/(  (()/(   
#       )\  )\  |((_)\  ((_)\   /(_))  /(_))  
#      ((_)((_) |_ ((_)  _((_) (_))   (_))_   
#      \ \ / /  | |/ /  | || | / __|   |   \  
#       \ V /     ' <   | __ | \__ \   | |) | 
#        \_/     _|\_\  |_||_| |___/   |___/  



import os
import random
import discord
from math import ceil
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import asyncio
import DPSCalc as dpsc
from collections import namedtuple, defaultdict
from sympy import *

TOKEN = 'TOKEN' # Input token here

intents = discord.Intents.all()

AUTHORIZED_USER_ID = 0 # Replace with your discord user ID to become the sole admin 

client = commands.Bot(command_prefix='.', intents=intents)

last_event_time = '2023-07-25 17:52:00'
last_occurrence = '2023-07-25 17:52:00'


@client.event
async def on_ready():
    print('bot ready')


@client.event
async def on_message(message):
    print(message.author, message.content, message.channel.id)
    await client.process_commands(message)


@client.command()
async def commands(ctx):
    await ctx.send('Available commands:\n'
                   '".dc boost" Gives an estimation for dc drops\n'
                   '".lg boost" Gives an estimation for lg drops\n'
                   '".simhell boost amount" Does a simulation for hell raid drops\n'
                   '".simcruins boost amount" Does a simulation for corrupted ruins drops\n'
                   '".th players" Shows the thresholds for lgs & dcs\n'
                   '".dps min max fire-rate shots att dex" Gives dps at 0 defense\n'
                   '".dpc type atk dex" Gives damage chart of a weapon type with user stats (does not account for abilities)\n'
                   '".dpsa min max shots mpcost" Gives damage per use of an ability\n'
                   '".random" Gives a random class to play\n'
                   '".c boost chance amount" Gives the approximate chance of a single drop\n'
                   '".cal phrase" Calculates an expression\n')


@client.command()
async def cal(ctx, *, expr: str):
    try:
        expr = simplify(expr)

        result = expr.evalf()
        await ctx.send(f'The result is: {result}')
    except Exception as e:
        await ctx.send(
            f'Sorry, I was unable to evaluate the expression. Please make sure it is a valid mathematical expression.')


@client.command()
async def c(ctx, boost, chance, amount: int = 1):
    await ctx.send(f"The chance is 1/{ceil(float(chance) / (int(amount) * (1 + (float(boost) / 100))))}")


@client.command()
async def dc(ctx, boost: float = 0):
    individual_chance_hell = ceil(((1 + (boost / 100)) / 600) ** (-1))
    average_chance_hell = individual_chance_hell / 14

    individual_chance_cruins_magus = ceil(((1 + (boost / 100)) / 600) ** (-1))
    individual_chance_cruins_eternal = ceil(((1 + (boost / 100)) / 666) ** (-1))
    individual_chance_cruins_madness = ceil(((1 + (boost / 100)) / 600) ** (-1))

    average_chance_cruins = (individual_chance_cruins_magus + individual_chance_cruins_eternal + individual_chance_cruins_madness) / 6

    await ctx.send(
        f'Your average chances of getting a demonic drop are:\n'
        f'- In Hell Raid: one in {ceil(average_chance_hell)}\n'
        f'- In Corrupted Ruins: one in {ceil(average_chance_cruins)}\n'
        f'Boost your chances by increasing the boost value!'
    )


@client.command()
async def lg(ctx, boost: int = 0):
    chance1 = ceil(((1 + (boost / 100)) / 400) ** (-1))
    chance2 = ceil(((1 + (boost / 100)) / 666) ** (-1))
    relic_chance1 = ceil(((1 + (boost / 400)) / 250) ** (-1))
    relic_chance2 = ceil(((1 + (boost / 700)) / 250) ** (-1))
    await ctx.send(f'Your chances of getting a generic legendary is roughly one in {chance1}-{chance2}\n'
                   f'Your chances of getting a generic relic is roughly one in {relic_chance1}-{relic_chance2}')


@client.command()
async def th(ctx, players: int = 0):
    if players <= 10:
        await ctx.send(f'The legendary threshold is {5}%'
                       f'\nThe demonic threshold is {7.5}%')
    else:
        legendary_threshold = 50 / players
        demonic_threshold = legendary_threshold * 1.8
        await ctx.send(f'The legendary threshold is {round(legendary_threshold, 2)}%'
                       f'\nThe demonic threshold is {round(demonic_threshold, 2)}%')


Stage = namedtuple('Stage', ['name', 'drops', 'chance', 'relic_chance', 'relic_drops'])

STAGES = [
    Stage('Limbo', ["Tablet of Doom", "Nightmare Gem"], "chance", "chance_relic1", 1),
    Stage('Lust', ["Vest of Doomed Souls", "Unstable Jewel"], "chance", "chance_relic1", 1),
    Stage('Gluttony', ["Face of Gluttony", "Soul Warden"], "chance", "chance_relic1", 1),
    Stage('Greed', ["Favor of Fortune", "Essence of Death"], "chance", "chance_relic1", 1),
    Stage('Wrath', ["Bloodlord's Cranium", "Rigormortis"], "chance", "chance_relic1", 1),
    Stage('Heresy', ["Blazing Machete", "Flame of Misery", "Harbinger", "Death's Gem", "Death's Mantle"],
          "chance2", "chance_relic2", 4)
]


@client.command()
async def simhell(ctx, boost: int = 0, amount: int = 1):
    if amount > 1000000:
        await ctx.send("The amount cannot exceed 1 million.")
        return

    chance = ceil(((1 + (boost / 100)) / 1200) ** (-1))
    chance2 = ceil(((1 + (boost / 100)) / 600) ** (-1))
    chance_relic1 = ceil(((1 + (boost / 100)) / 400) ** (-1))
    chance_relic2 = ceil(((1 + (boost / 100)) / 700) ** (-1))

    chances = {
        "chance": chance,
        "chance2": chance2,
        "chance_relic1": chance_relic1,
        "chance_relic2": chance_relic2,
    }

    loot = defaultdict(int)

    for _ in range(amount):
        for stage in STAGES:
            for drop in stage.drops:
                if random.randint(1, chances[stage.chance]) == 1:
                    loot[drop] += 1

            for _ in range(stage.relic_drops):
                if random.randint(1, chances[stage.relic_chance]) == 1:
                    loot["Relic of Awakening"] += 1

            if stage.name == 'Gluttony':
                for drop in stage.drops:
                    if random.randint(1, chances[stage.chance]) == 1:
                        loot[drop] += 1

            if stage.name == 'Greed':
                if random.randint(1, 8) == 1:
                    for drop in stage.drops:
                        if random.randint(1, chances[stage.chance]) == 1:
                            loot[drop] += 1

                for drop in stage.drops:
                    if random.randint(1, chances[stage.chance]) == 1:
                        loot[drop] += 1

            elif stage.name == 'Wrath':
                if random.randint(1, 4) == 1:
                    for drop in stage.drops:
                        if random.randint(1, chances[stage.chance]) == 1:
                            loot[drop] += 1

    if not loot:
        await ctx.send('You got nothing!')
    else:
        loot_string = "\n".join([f"{amount if amount > 1 else ''} {name}"
                                 for name, amount in loot.items()])
        total_items = sum(loot.values())
        header = f'From {amount} raids: ' if amount > 1 else ''
        await ctx.send(f'{header}You just got {total_items} items!\n{loot_string}')


Stage = namedtuple('Stage', ['name', 'drops', 'chance', 'relic_chance', 'relic_drops'])

STAGES_CRUINS = [
    Stage('Acheron', ["Ballistic Star", "Titanfeller Toxin", "General's Knife"], [500, 500, 500], 400, 1),
    Stage('Dragonborn Magus', ["Dragonkin's Shroud", "Executioner's Guillotine", "Primal Flame", "Drakenguard"],
          [285.7, 285.7, 600, 600], 250, 1),
    Stage('The Eternal One', ["Overgrown Skull", "Petrified Dragonroot", "Pyrus Draconia", "The Eternal Kinstone"],
          [333.3, 333.3, 666, 666], 400, 1),
    Stage('King of Madness', ["Mad King's Crook", "Mad King's Ramblings", "Rhongomyniad", "Crest of Ruin"],
          [285.7, 285.7, 600, 600], 25, 1),
]


@client.command()
async def simcruins(ctx, boost: int, amount: int = 1):
    if amount > 1000:
        await ctx.send("The amount cannot exceed a thousand.")
        return

    chances = [
        {"items": {"Relic of Awakening": 400, "Ballistic Star": 500, "Titanfeller Toxin": 500, "General's Knife": 500}},
        {"items": {"Relic of Awakening": 250, "Dragonkin's Shroud": 285.7, "Executioner's Guillotine": 285.7,
                   "Primal Flame": 600, "Drakenguard": 600}},
        {"items": {"Overgrown Skull": 333.3, "Petrified Dragonroot": 333.3, "Relic of Awakening": 400,
                   "Pyrus Draconia": 666, "The Eternal Kinstone": 666}},
        {"items": {"Relic of Awakening": 25, "Mad King's Crook": 285.7, "Mad King's Ramblings": 285.7,
                   "Rhongomyniad": 600, "Crest of Ruin": 600}},
    ]

    loot = defaultdict(int)

    for _ in range(amount):
        for stage in chances:
            for item, drop_rate in stage["items"].items():
                if random.randint(1, ceil(((1 + (boost / 100)) / drop_rate) ** -1)) == 1:
                    loot[item] += 1

    if not loot:
        await ctx.send('You got nothing!')
    else:
        loot_string = "\n".join([f"{quantity if quantity > 1 else ''} {item}" for item, quantity in loot.items()])
        total_items = sum(loot.values())
        header = f'From {amount} raids: ' if amount > 1 else ''
        await ctx.send(f'{header}You just got {total_items} items!\n{loot_string}')


@client.command()
async def coinflip(ctx):
    result = random.randint(1, 2)
    if result == 1:
        await ctx.send("Heads!")
    elif result == 2:
        await ctx.send("Tails!")
    else:
        await ctx.send("This is the secret third message!")


@client.command()
async def dps(ctx, min_damage: int = 100, max_damage: int = 100, rate_of_fire: float = 1.0, num_projectiles: int = 1,
              attack: int = 50, dexterity: int = 50):
    base_rate_of_fire = rate_of_fire

    def calculate_damage(min_damage, max_damage, attack):
        raw_damage = (min_damage + max_damage - 2) / 2
        adjusted_damage = raw_damage * ((attack + 25) / 50)
        return adjusted_damage

    def calculate_actual_damage(base_damage, defense):
        actual_damage = max(base_damage - defense, base_damage * 0.1)
        return actual_damage

    def calculate_attacks_per_second(dexterity):
        attacks_per_second = base_rate_of_fire * (6.5 * (dexterity + 17.3) / 75)
        return attacks_per_second

    def calculate_dps(min_damage, max_damage, num_projectiles, defense, attack, dexterity):
        base_damage = calculate_damage(min_damage, max_damage, attack)
        actual_damage = calculate_actual_damage(base_damage, defense)
        attacks_per_second = calculate_attacks_per_second(dexterity)
        dps = actual_damage * num_projectiles * attacks_per_second
        return dps

    dps_values = []
    for defense in range(0, 10, 10):
        dps = calculate_dps(min_damage, max_damage, num_projectiles, defense, attack, dexterity)
        dps_values.append(f'DPS for defense {defense}: {ceil(dps)}')

    await ctx.send('\n'.join(dps_values))


@client.command()
@has_permissions(administrator=True)
async def clean(ctx, llimit: int):
    await ctx.channel.purge(limit=llimit)
    await ctx.send('Cleared by <@{.author.id}>'.format(ctx))


@clean.error
async def clear_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You cant do that!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    classes = [
        "rogue",
        "archer",
        "wizard",
        "priest",
        "warrior",
        "knight",
        "paladin",
        "assassin",
        "necromancer",
        "huntress",
        "mystic",
        "trickster",
        "sorcerer",
        "ninja",
        "tribesman",
    ]

    if message.content == '.random':
        await message.channel.send(f"You should play the {random.choice(classes)} {message.author.mention}!")

    await client.process_commands(message)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.command()
async def dpsa(ctx, min: int, max: int, shots: int, mana: int):
    damage = ((min + max - 2) / 2) * shots
    await ctx.send(f"This ability does {ceil(damage)} per use.\n"
                   f"The ability also does {round(damage / mana, 1)} damage per MP")


@client.command()
async def dpc(ctx, type: str, dex: int, atk: int, ):
    if type == 'staff' or type == 'staffs' or type == 'staves' or type == 'stave' or type == 'stf':
        dps_primal_flame = dpsc.calculate_dps(75, 150, 3, 1.2, dex, atk)
        dps_knightfall = dpsc.calculate_dps(400, 700, 1, .5, dex, atk)
        dps_cremation = dpsc.calculate_dps(255, 315, 2, .45, dex, atk)
        dps_staff_of_holy_terror = dpsc.calculate_dps(100, 115, 3, 1, dex, atk)
        dps_loremakers_staff = dpsc.calculate_dps(400, 700, 1, .5, dex, atk)
        crook_of_carrot_addiction = dpsc.calculate_dps(500, 700, 1, .5, dex, atk)
        dps_bunny_summoner_rod = dpsc.calculate_dps(145, 180, 2, .75, dex, atk)
        dps_eggsplosive_staff = dpsc.calculate_dps(400, 700, 1, .5, dex, atk)
        dps_oathsworns_staff = dpsc.calculate_dps(500, 700, 1, .5, dex, atk)
        dps_tears_of_siren = dpsc.calculate_dps(90, 120, 2, 1.4, dex, atk)
        dps_eyjafjalla = dpsc.calculate_dps(145, 180, 2, .75, dex, atk)
        dps_soulkeeper = dpsc.calculate_dps(135, 245, 1, 1.2, dex, atk)
        dps_blizzard_staff = dpsc.calculate_dps(145, 180, 2, .75, dex, atk)
        dps_staff_of_unending_winter = dpsc.calculate_dps(80, 160, 3, .85, dex, atk)
        dps_wicked_torch = dpsc.calculate_dps(90, 120, 2, 1.4, dex, atk)
        dps_staff_of_the_tide = dpsc.calculate_dps(90, 120, 2, 1.4, dex, atk)
        dps_rod_of_divine_intellect = dpsc.calculate_dps(80, 160, 3, .85, dex, atk)
        dps_hells_inferno = dpsc.calculate_dps(145, 180, 2, .75, dex, atk)
        dps_staff_of_unholy_sacrifice = dpsc.calculate_dps(150, 175, 4, .6, dex, atk)
        dps_bubble_discharger_staff = dpsc.calculate_dps(50, 115, 2, 1.4, dex, atk)
        dps_staff_of_the_crystal_serpent = dpsc.calculate_dps(60, 70, 2, 1.1, dex, atk)
        dps_staff_of_serpant_bane = dpsc.calculate_dps(45, 140, 2, 1.1, dex, atk)
        dps_snow_blast_staff = dpsc.calculate_dps(75, 175, 2, .9, dex, atk)
        dps_skeletal_staff = dpsc.calculate_dps(35, 60, 4, 1.2, dex, atk)
        dps_janitors_broom_staff = dpsc.calculate_dps(65, 105, 2, 1, dex, atk)
        dps_staff_of_extreme_prejudice = dpsc.calculate_dps(60, 70, 10, .5, dex, atk)
        dps_staff_of_magic_fairy = dpsc.calculate_dps(50, 95, 2, 1.2, dex, atk)
        dps_scorching_torch = dpsc.calculate_dps(80, 100, 3, .85, dex, atk)
        dps_gnosticism = dpsc.calculate_dps(45, 80, 3, 1, dex, atk)
        dps_spirit_staff = dpsc.calculate_dps(45, 80, 3, 1, dex, atk)
        dps_staff_of_the_vital_unity = dpsc.calculate_dps(60, 105, 2, 1, dex, atk)
        dps_staff_of_the_cosmic_whole = dpsc.calculate_dps(60, 100, 2, 1, dex, atk)
        dps_staff_of_astral_knowledge = dpsc.calculate_dps(55, 100, 2, 1, dex, atk)
        dps_hells_inferno_awk = dpsc.calculate_dps(150, 190, 2, .84, dex, atk)
        dps_tears_of_siren_awk = dpsc.calculate_dps(105, 135, 2, 1.4, dex, atk)
        dps_staff_of_holy_terror_awk = dpsc.calculate_dps(106, 121, 3, 1, dex, atk)
        dps_staff_of_unholy_sacrifice_awk = dpsc.calculate_dps(190, 210, 4, .55, dex, atk)
        dps_h5_staff = dpsc.calculate_dps(90, 120, 3, .9, dex, atk)

        dps_dict = {
            "Primal Flame": int(dps_primal_flame),
            "Knightfall": int(dps_knightfall),
            "Cremation": int(dps_cremation),
            "Staff of Holy Terror": int(dps_staff_of_holy_terror),
            "Loremaker's Staff": int(dps_loremakers_staff),
            "Crook of Carrot Addiction": int(crook_of_carrot_addiction),
            "Bunny Summoner Rod": int(dps_bunny_summoner_rod),
            "Eggsplosive Staff": int(dps_eggsplosive_staff),
            "Oathsworn's Staff": int(dps_oathsworns_staff),
            "Tears of Siren": int(dps_tears_of_siren),
            "Eyjafjalla": int(dps_eyjafjalla),
            "Soulkeeper": int(dps_soulkeeper),
            "Blizzard Staff": int(dps_blizzard_staff),
            "Staff of Unending Winter": int(dps_staff_of_unending_winter),
            "Wicked Torch": int(dps_wicked_torch),
            "Staff of the Tide": int(dps_staff_of_the_tide),
            "Rod of Divine Intellect": int(dps_rod_of_divine_intellect),
            "Hell's Inferno": int(dps_hells_inferno),
            "Staff of Unholy Sacrifice": int(dps_staff_of_unholy_sacrifice),
            "Bubble Discharger Staff": int(dps_bubble_discharger_staff),
            "Staff of the Crystal Serpent": int(dps_staff_of_the_crystal_serpent),
            "Staff of Serpant Bane": int(dps_staff_of_serpant_bane),
            "Snow Blast Staff": int(dps_snow_blast_staff),
            "Skeletal Staff": int(dps_skeletal_staff),
            "Janitor's Broom Staff": int(dps_janitors_broom_staff),
            "Staff of Extreme Prejudice": int(dps_staff_of_extreme_prejudice),
            "Staff of Magic Fairy": int(dps_staff_of_magic_fairy),
            "Scorching Torch": int(dps_scorching_torch),
            "Gnosticism": int(dps_gnosticism),
            "Spirit Staff": int(dps_spirit_staff),
            "Staff of the Vital Unity": int(dps_staff_of_the_vital_unity),
            "Staff of the Cosmic Whole": int(dps_staff_of_the_cosmic_whole),
            "Staff of Astral Knowledge": int(dps_staff_of_astral_knowledge),
            "Hell's Inferno (AWK):": int(dps_hells_inferno_awk),
            "Tears of Siren (AWK)": int(dps_tears_of_siren_awk),
            "Staff of Holy Terror (AWK)": int(dps_staff_of_holy_terror_awk),
            "Staff of Unholy Sacrifice (AWK)": int(dps_staff_of_unholy_sacrifice_awk),
            "Awoken Hunters Truncheon (H5)": int(dps_h5_staff),
        }

        sorted_dps = sorted(dps_dict.items(), key=lambda item: item[1], reverse=True)

        await ctx.send("\n".join([f"{weapon}: {dps}" for weapon, dps in sorted_dps]))

    if type == 'sword' or type == 'swords' or type == 'sord':
        dps_rhongomyniad = dpsc.calculate_dps(800, 900, 1, .5, dex, atk)
        dps_rigormortis = dpsc.calculate_dps(200, 300, 3, .7, dex, atk)
        dps_vouivre_gunlance = dpsc.calculate_dps(250, 315, 1, 1.2, dex, atk)
        dps_blade_of_the_grave = dpsc.calculate_dps(215, 305, 1, 1.35, dex, atk)
        dps_mudrocks_sledgehammer = dpsc.calculate_dps(150, 180, 4, .75, dex, atk)
        dps_ancient_stone_sword1 = dpsc.calculate_dps(200, 200, 1, .7, dex, atk)
        dps_ancient_stone_sword2 = dpsc.calculate_dps(200, 200, 2, .7, dex, atk)
        dps_forests_edge = dpsc.calculate_dps(215, 305, 1, 1.35, dex, atk)
        dps_oryxs_decapitator = dpsc.calculate_dps(325, 345, 1, 1.35, dex, atk)
        dps_shiny_diamond_sword = dpsc.calculate_dps(0, 650, 1, 1, dex, atk)
        dps_champions_carrot = dpsc.calculate_dps(290, 585, 1, .85, dex, atk)
        dps_eggscalibur = dpsc.calculate_dps(215, 305, 1, 1.35, dex, atk)
        dps_knights_warhammer = dpsc.calculate_dps(666, 777, 2, .31, dex, atk)
        dps_north_poles_slasher = dpsc.calculate_dps(250, 315, 1, 1.2, dex, atk)
        dps_icestriker = dpsc.calculate_dps(215, 305, 1, 1.35, dex, atk)
        dps_pumpkin_smasher = dpsc.calculate_dps(290, 585, 1, .85, dex, atk)
        dps_guts_sword = dpsc.calculate_dps(290, 585, 1, .85, dex, atk)
        dps_stormcaller = dpsc.calculate_dps(400, 480, 1, .95, dex, atk)
        dps_champions_blade = dpsc.calculate_dps(290, 585, 1, .85, dex, atk)
        dps_the_great_lightsword = dpsc.calculate_dps(500, 500, 1, .8, dex, atk)
        dps_brand_of_the_guardian = dpsc.calculate_dps(150, 180, 4, .75, dex, atk)
        dps_spear_of_the_chosen = dpsc.calculate_dps(250, 315, 1, 1.2, dex, atk)
        dps_sword_of_the_colossus = dpsc.calculate_dps(400, 480, 1, .95, dex, atk)
        dps_cursed_pickaxe = dpsc.calculate_dps(1, 777, 1, .8, dex, atk)
        dps_pirate_kings_cutlass = dpsc.calculate_dps(210, 235, 1, 1.3, dex, atk)
        dps_orins_slasher = dpsc.calculate_dps(275, 315, 1, .85, dex, atk)
        dps_sword_of_the_general = dpsc.calculate_dps(285, 385, 1, 1, dex, atk)
        dps_circle_test_sword = dpsc.calculate_dps(0, 100, 1, 1, dex, atk)
        dps_ice_excalibur = dpsc.calculate_dps(165, 365, 1, 1, dex, atk)
        dps_the_ghostreaver = dpsc.calculate_dps(155, 215, 1, 1.4, dex, atk)
        dps_crystal_sword = dpsc.calculate_dps(210, 245, 1, 1, dex, atk)
        dps_demon_blade = dpsc.calculate_dps(135, 175, 2, 1, dex, atk)
        dps_skysplitter_sword = dpsc.calculate_dps(210, 270, 1, 1, dex, atk)
        dps_sword_of_splendor = dpsc.calculate_dps(225, 285, 1, 1, dex, atk)
        dps_sword_of_acclaim = dpsc.calculate_dps(220, 275, 1, 1, dex, atk)
        dps_forests_edge_awk = dpsc.calculate_dps(248, 338, 1, 1.35, dex, atk)
        dps_spear_of_the_chosen_awk = dpsc.calculate_dps(267, 332, 1, 1.3, dex, atk)
        dps_knights_warhammer_awk = dpsc.calculate_dps(688, 799, 2, .31, dex, atk)
        dps_oryxs_decapitator_awk = dpsc.calculate_dps(332, 352, 1, 1.35, dex, atk)
        dps_h5_sword = dpsc.calculate_dps(150, 175, 2, 1.25, dex, atk)

        dps_dict = {
            "Rhongomyniad": int(dps_rhongomyniad),
            "Rigormortis": int(dps_rigormortis),
            "Vouivre Gunlance": int(dps_vouivre_gunlance),
            "Blade of the Grave": int(dps_blade_of_the_grave),
            "Mudrock's Sledgehammer": int(dps_mudrocks_sledgehammer),
            "Ancient Stone Sword": int(dps_ancient_stone_sword1 + dps_ancient_stone_sword2),
            "Forest's Edge": int(dps_forests_edge),
            "Oryx's Decapitator": int(dps_oryxs_decapitator),
            "Shiny Diamond Sword": int(dps_shiny_diamond_sword),
            "Champion's Carrot": int(dps_champions_carrot),
            "Eggscalibur": int(dps_eggscalibur),
            "Knight's Warhammer": int(dps_knights_warhammer),
            "North Pole's Slasher": int(dps_north_poles_slasher),
            "IceStriker": int(dps_icestriker),
            "Pumpkin Smasher": int(dps_pumpkin_smasher),
            "Guts Sword": int(dps_guts_sword),
            "Stormcaller": int(dps_stormcaller),
            "Champion's Blade": int(dps_champions_blade),
            "The Great Lightsword": int(dps_the_great_lightsword),
            "Brand of the Guardian": int(dps_brand_of_the_guardian),
            "Spear of the Chosen": int(dps_spear_of_the_chosen),
            "Sword of the Colossus": int(dps_sword_of_the_colossus),
            "Cursed Pickaxe": int(dps_cursed_pickaxe),
            "Pirate King's Cutlass": int(dps_pirate_kings_cutlass),
            "Orin's Slasher": int(dps_orins_slasher),
            "Sword of the General": int(dps_sword_of_the_general),
            "Circle Test Sword": int(dps_circle_test_sword),
            "Ice Excalibur": int(dps_ice_excalibur),
            "The Ghostreaver": int(dps_the_ghostreaver),
            "Crystal Sword": int(dps_crystal_sword),
            "Demon Blade": int(dps_demon_blade),
            "Skysplitter Sword": int(dps_skysplitter_sword),
            "Sword of Splendor": int(dps_sword_of_splendor),
            "Sword of Acclaim": int(dps_sword_of_acclaim),
            "Forest's Edge (AWK)": int(dps_forests_edge_awk),
            "Spear of the chosen (AWK)": int(dps_spear_of_the_chosen_awk),
            "Knight's Warhammer (AWK)": int(dps_knights_warhammer_awk),
            "Oryx's Decapitator (AWK)": int(dps_oryxs_decapitator_awk),
            "Awoken Hunter's Glaive (H5)": int(dps_h5_sword)
        }

        sorted_dps = sorted(dps_dict.items(), key=lambda item: item[1], reverse=True)

        await ctx.send("\n".join([f"{sword}: {dps}" for sword, dps in sorted_dps]))

    if type == 'dagger' or type == 'daggers' or type == 'dag':
        dps_blazing_machete = dpsc.calculate_dps(235, 335, 1, 1.5, dex, atk)
        dps_frenzied_claw = dpsc.calculate_dps(235, 335, 1, 1.5, dex, atk)
        dps_royal_fangs = dpsc.calculate_dps(50, 185, 2, 1.15, dex, atk)
        dps_stellar_blades = dpsc.calculate_dps(50, 185, 2, 1.15, dex, atk)
        dps_dirk_of_cronus = dpsc.calculate_dps(225, 310, 1, 1.05, dex, atk)
        dps_butterfly_dagger_1 = dpsc.calculate_dps(400, 400, 1, .35, dex, atk)
        dps_butterfly_dagger_2 = dpsc.calculate_dps(95, 95, 4, .35, dex, atk)
        dps_blood_collector_blade = dpsc.calculate_dps(175, 235, 1, 1.3, dex, atk)
        dps_glazed_edge = dpsc.calculate_dps(90, 125, 2, 1.5, dex, atk)
        dps_ravagers_talon = dpsc.calculate_dps(230, 300, 1, 1, dex, atk)
        dps_rabbits_shank = dpsc.calculate_dps(225, 310, 1, 1.05, dex, atk)
        dps_generals_knife = dpsc.calculate_dps(170, 300, 1, 1.3, dex, atk)
        dps_shattered_caliburn = dpsc.calculate_dps(260, 385, 1, .75, dex, atk)
        dps_whip_of_the_sinner = dpsc.calculate_dps(75, 125, 3, 1, dex, atk)
        dps_claws_of_war = dpsc.calculate_dps(120, 145, 3, .85, dex, atk)
        dps_chaotic_dagger = dpsc.calculate_dps(100, 200, 2, 1.05, dex, atk)
        dps_spirit_dagger = dpsc.calculate_dps(115, 265, 1, 1, dex, atk)
        dps_chi_xiao = dpsc.calculate_dps(75, 95, 2, 1.25, dex, atk)
        dps_etherite_dagger = dpsc.calculate_dps(96, 204, 1, 1.09, dex, atk)
        dps_dirk_of_sloth = dpsc.calculate_dps(666, 666, 1, .3, dex, atk)
        dps_ritual_knife = dpsc.calculate_dps(190, 190, 1, 1, dex, atk)
        dps_imposters_knife = dpsc.calculate_dps(100, 100, 1, .5, dex, atk)
        dps_bone_dagger = dpsc.calculate_dps(130, 210, 1, .9, dex, atk)
        dps_poison_fang_dagger = dpsc.calculate_dps(55, 120, 1, 1, dex, atk)
        dps_ghosts_last_breath = dpsc.calculate_dps(155, 250, 1, .9, dex, atk)
        dps_dagger_of_royalty = dpsc.calculate_dps(125, 155, 1, 1.1, dex, atk)
        dps_dragonslayer_blades = dpsc.calculate_dps(75, 95, 2, 1.25, dex, atk)
        dps_sugar_rush = dpsc.calculate_dps(155, 250, 1, .9, dex, atk)
        dps_dagger_of_sinister_deeds = dpsc.calculate_dps(95, 180, 1, 1, dex, atk)
        dps_dagger_of_foul_malevolence = dpsc.calculate_dps(95, 175, 1, 1, dex, atk)
        dps_shattered_caliburn_awk = dpsc.calculate_dps(235, 385, 1, .95, dex, atk)
        dps_stellar_blades_awk = dpsc.calculate_dps(58, 203, 2, 1.15, dex, atk)
        dps_chaotic_dagger_awk = dpsc.calculate_dps(107, 207, 2, 1.06, dex, atk)
        dps_glazed_edge_awk = dpsc.calculate_dps(83, 133, 2, 1.5, dex, atk)
        dps_h5_dagger = dpsc.calculate_dps(110, 125, 2, 1.25, dex, atk)

        dps_dict = {
            "Blazing Machete": int(dps_blazing_machete),
            "Frenzied Claw": int(dps_frenzied_claw),
            "Royal Fangs": int(dps_royal_fangs),
            "Stellar Blades": int(dps_stellar_blades),
            "Dirk of Cronus": int(dps_dirk_of_cronus),
            "Butterfly Dagger": int(dps_butterfly_dagger_1 + dps_butterfly_dagger_2),
            "Blood Collector Blade": int(dps_blood_collector_blade),
            "Glazed Edge": int(dps_glazed_edge),
            "Ravager's Talon": int(dps_ravagers_talon),
            "Rabbit's Shank": int(dps_rabbits_shank),
            "General's Knife": int(dps_generals_knife),
            "Shattered Caliburn": int(dps_shattered_caliburn),
            "Whip of the Sinner": int(dps_whip_of_the_sinner),
            "Claws of War": int(dps_claws_of_war),
            "Chaotic Dagger": int(dps_chaotic_dagger),
            "Spirit Dagger": int(dps_spirit_dagger),
            "Chi Xiao": int(dps_chi_xiao),
            "Etherite Dagger": int(dps_etherite_dagger),
            "Dirk of Sloth": int(dps_dirk_of_sloth),
            "Ritual Knife": int(dps_ritual_knife),
            "Imposter's Knife": int(dps_imposters_knife),
            "Bone Dagger": int(dps_bone_dagger),
            "Poison Fang Dagger": int(dps_poison_fang_dagger),
            "Ghost's Last Breath": int(dps_ghosts_last_breath),
            "Dagger of Royalty": int(dps_dagger_of_royalty),
            "Dragonslayer Blades": int(dps_dragonslayer_blades),
            "Sugar Rush": int(dps_sugar_rush),
            "Dagger of Sinister Deeds": int(dps_dagger_of_sinister_deeds),
            "Dagger of Foul Malevolence": int(dps_dagger_of_foul_malevolence),
            "Shattered Caliburn (AWK)": int(dps_shattered_caliburn_awk),
            "Stellar Blades (AWK)": int(dps_stellar_blades_awk),
            "Chaotic Dagger (AWK)": int(dps_chaotic_dagger_awk),
            "Glazed Edge (AWK)": int(dps_glazed_edge_awk),
            "Awoken Hunter's Shiv (H5)": int(dps_h5_dagger),
        }

        sorted_dps = sorted(dps_dict.items(), key=lambda item: item[1], reverse=True)

        await ctx.send("\n".join([f"{dagger}: {dps}" for dagger, dps in sorted_dps]))


muted_player = 0  # Replace with the real user ID,


# this will disconnect this user instantly upon them joining a voice channel.
# best used to soft-ban someone or can be used for malice if wanted


@client.event
async def on_voice_state_update(member, before, after):
    if member.id == muted_player and after.channel is not None:
        await member.move_to(None)
        print(f'{member.name} has been disconnected from the voice channel.')


client.run(TOKEN)
