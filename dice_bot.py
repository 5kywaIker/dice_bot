import traceback
import discord
import CustomErrors
import player
from discord import app_commands
from discord.ext import commands
import bot_functions
from bot_functions import get_command

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)




@bot.event
async def on_ready():
    print(f'Bot: {bot.user} online')
    await bot.tree.sync(guild=discord.Object(id=1174375949081514014))


@bot.command(aliases=['t', 'rm'])
async def r(ctx, to_roll="1d20", *args):
    import bot_functions
    author = ctx.message.author

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.r_command(ctx, to_roll, author.id)

    except CustomErrors.NotEnoughSpellSlots as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"Du hast nicht genug Spell Slots um diesen Spell auf Level {args[0]} zu casten")
    except CustomErrors.NotUniqueMatching as e:                                                             #my custom Error
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht. Use -create_custom um Attribut zu erstellen.")
    except CustomErrors.CustomCommandEnd as e:
        print(e)
    except KeyError as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Custom Attribut nicht in eigener Liste vorhanden. Use -create_custom um Attribut zu erstellen.")
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"RIP, darfst anscheinend nicht mehr würfeln :') Must use Format: -r 1d20+2 oder ein Attribut. [[{e=}]]")

        
@bot.command(aliases=['ra'])
async def ad(ctx, to_roll="1d20", *args):
    #-ad +modifier würfeln, standard wurf auch ausführen wenn nur modifier übergeben wird
    #dafür überprüfen ob ein Buchstabe im Inputstring enthalten ist, ansonsten wurden nur modifier übergeben und der string sollte um "1d20" erweitert werden

    import bot_functions
    author = ctx.message.author

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.ad_command(ctx, to_roll, author.id, 1)

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht. Use -create_custom um Attribut zu erstellen.")
    except CustomErrors.CustomCommandEnd as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Sucks to be you. War auf Vorteil, also sag dem DM einfach du hast ne dirty 20. Must use Format: -r 1d20+2 oder ein Attribut ")


@bot.command(aliases=['rd'])
async def di(ctx, to_roll="1d20", *args):
    import bot_functions
    author = ctx.message.author

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.di_command(ctx, to_roll, author.id, 2)

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht. Use -create_custom um Attribut zu erstellen.")
    except CustomErrors.CustomCommandEnd as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"Hmm, ne, keine Ahnung was passiert ist. Stell dir einfach vor ist ne 1. Must use Format: -r 1d20+2 oder ein Attribut.")


@bot.command(aliases=['att','at','atta','attac'])
async def attack(ctx, to_roll="attack", *args):
    import bot_functions
    author = ctx.message.author
    try:
        if not to_roll == "attack":
            to_roll = to_roll + "+" + "attack"

        if len(args) != 0:
            for item in args:
                to_roll += str(item)
        await bot_functions.r_command(ctx, to_roll, author.id)

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht. Use -create_custom um Attribut zu erstellen.")
    except CustomErrors.CustomCommandEnd as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Bruh, kannst einfach -r attack machen. Aber das war nicht der fehler, hast irgendwas anderes falsch gemacht. ")

@attack.error
async def attack_error(ctx, error):
    if isinstance(error, Exception):
        print(error)
        traceback.print_exc()
        await ctx.reply("Bruh, kannst einfach -r attack machen. Aber das war nicht der fehler, hast irgendwas anderes falsch gemacht. ")

@bot.command()
async def get(ctx, *, request):
    import bot_functions
    author = ctx.message.author
    modifier = await bot_functions.get_command(ctx, request, author.id)
    await ctx.reply(modifier)

@get.error
async def get_error(ctx, error):
    if isinstance(error, CustomErrors.NotUniqueMatching):
        print(error)
        traceback.print_exc()
        await ctx.reply("Attribut Eingabe nicht eindeutig.")
    if isinstance(error, CustomErrors.NotExistingMatching):
        print(error)
        traceback.print_exc()
        await ctx.reply("Attribut Eingabe existiert nicht.")
    if isinstance(error, commands.CommandError):
        print(error)
        traceback.print_exc()
        await ctx.reply("Error")


@bot.command(aliases=['get_all'])
async def getall(ctx, *args):

    import bot_functions
    author = ctx.message.author
    name_list = await bot_functions.getall_command(ctx, author.id)
    await ctx.reply(name_list)

@bot.command(aliases=['del','remove','re'])
async def delete(ctx, request, *args):
    import bot_functions

    try:
        if not len(args) == 0:
            await ctx.reply("Zu viele Werte zu denen gechanged werden sollen übergeben")
            return

        author = ctx.message.author
        request_long, old_value = await bot_functions.delete_command(ctx, request, author.id)

        await ctx.reply(f"Dein {request_long} Eintrag mit dem Inhalt {old_value} wurde gelöscht")

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht. Use -create_custom um Attribut zu erstellen.")
    except CustomErrors.CustomCommandEnd as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"ALARM. ALARM. Ein Eindringling. Dachtest du kannst hier einfach so rumschleichen und eine Uniform klauen. [[{e=}]]")

@bot.hybrid_command(name="change", with_app_command=True, description="Ändert den Wert eines Attributes")
@app_commands.guilds(discord.Object(id=1174375949081514014))
@app_commands.describe(attribute='Name des Attributs', change_to='Neuer Modifier',)
async def change(ctx, attribute, change_to):
    import bot_functions

    try:
        #if not len(args) == 0:
        #    await ctx.reply("Zu viele Werte zu denen gechanged werden sollen übergeben")
        #    return

        if change_to is None:
            await ctx.reply("Keinen aktuellen Wert zu dem gechanged werden soll übergeben")
            return

        author = ctx.message.author
        request_long, old_value = await bot_functions.change_command(ctx, attribute, change_to, author.id)

        await ctx.reply(f"Dein {request_long} Eintrag wurde von {old_value} zu {change_to} geändert")

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht. Use -create_custom um Attribut zu erstellen.")
    except CustomErrors.CustomCommandEnd as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"ALARM. ALARM. Ein Eindringling. Dachtest du kannst hier einfach so rumschleichen und eine Uniform klauen. [[{e=}]]")

@change.autocomplete("attribute")
async def change_autocomplete(ctx, current):
    attribute_list = player.attribute_list
    return [
        app_commands.Choice(name=attribute, value=attribute)
        for attribute in attribute_list if current.lower() in attribute.lower()]
#@change.autocomplete("change_to")
#async def change_autocomplete(ctx, current):
#    current = await bot_functions.match_substring(player.attribute_list, current)
#    return list(player.player_attribute_dict.get(player.user_dict[ctx.message.author])[current[0]])

@bot.command()
async def update(ctx):
    player.create_player_dict()


@bot.command(aliases=['create'])
async def create_custom(ctx, command_name, modifier, *args):
    """
    Adds a custom modifier either to the player_custom.txt or to the players_spells.txt. Eingabeformat: -create_custom attributname was_zu_würfeln_ist
    :param ctx: Unwichtig für den User
    :param command_name: Hier den Namen eingeben wie das Attribut heißen soll.
    :param modifier: Hier eingeben, was gewürfelt werden soll, wenn der Command aufgerufen wird
    :param args: Zum Erstellen von Spells noch zwei weitere Parameter übergeben
    :return:(str,str,str)
    """

    try:
        author = ctx.message.author

        if len(args) == 2:

            await bot_functions.create_spell_command(ctx, command_name, modifier, author.id, args[0], args[1])
            await ctx.reply(f"Der Level {args[1]} Spell {command_name} wurde mit dem Modifier {modifier} erstellt.")
        elif len(args) == 0:
            await bot_functions.create_custom_command(ctx, command_name, modifier, author.id)
            await ctx.reply(f"Custom Command {command_name} wurde mit dem Modifier {modifier} erstellt.")
        else:
            raise CustomErrors.TooManyInputs

    except CustomErrors.TooManyInputs as e:
        print(e)
        await ctx.reply("Zu viele Werte übergeben. Sollte '-create_custom command_name modifier' sein. Optional für Spells noch ' spell_skalierung spell_level' eingeben" )
    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"Wompwomp. I actually have no idea how you could even possible fail this one. Formatierung: '-create_custom command_name modifier( spell_skalierung spell_level)' [[{e=}]]")

@create_custom.error
async def create_custom_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Falsche Eingabe. Übergebe entweder zwei Paramter: 'Name_des_Attributs' 'Wert des Attributs' um ein Attribut zu erstellen, oder vier Parameter: 'Name_des_Spells' 'Was_der_Spell_würfeln_soll' '+was_beim_upcast_drauf_kommt' 'base_Level_des_spells'" )

##test##
@bot.hybrid_command(name="test", with_app_command=True, description="Testing")
@app_commands.guilds(discord.Object(id=1174375949081514014))
async def test(ctx):
    await ctx.reply("moo")
