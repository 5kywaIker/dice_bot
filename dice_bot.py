import traceback
import discord
import CustomErrors
import player
from discord.ext import commands
import bot_functions


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot: {bot.user} online')


@bot.command(aliases=['t', 'rm'])
async def r(ctx, to_roll="1d20", *args):
    import bot_functions
    author = ctx.message.author

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.r_command(ctx, to_roll, author.id)

    except CustomErrors.NotUniqueMatching as e:                                                             #my custom Error
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except CustomErrors.Custom_Command_End as e:
        print(e)
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
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except CustomErrors.Custom_Command_End as e:
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
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except CustomErrors.Custom_Command_End as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply(f"Hmm, ne, keine Ahnung was passiert ist. Stell dir einfach vor ist ne 1. Must use Format: -r 1d20+2 oder ein Attribut.")


@bot.command(aliases=['att','at','atta','attac'])
async def attack(ctx, to_roll="attack", *args):
    import bot_functions
    author = ctx.message.author

    if not to_roll == "attack":
        to_roll = to_roll + "+" + "attack"

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.r_command(ctx, to_roll, author.id)

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except CustomErrors.Custom_Command_End as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Bruh, kannst einfach -r attack machen. Aber das war nicht der fehler, hast irgendwas anderes falsch gemacht. ")

    
@bot.command()
async def get(ctx, *, request):
    import bot_functions
    author = ctx.message.author
    request_long = await bot_functions.match_substring(player.attribute_list_saves, request)
    user_name = player.user_dict[author.id]
    att_dict = player.player_attribute_dict[user_name]
    await ctx.reply(att_dict[request_long[0]])


@bot.command()
async def change(ctx, request, change_to, *args):
    import bot_functions

    try:
        if not len(args) == 0:
            await ctx.reply("Zu viele Werte zu denen gechanged werden sollen übergeben")
            return

        if change_to is None:
            await ctx.reply("Keinen aktuellen Wert zu dem gechanged werden soll übergeben")
            return

        author = ctx.message.author
        request_long, old_value = await bot_functions.change_command(ctx, request, change_to, author.id)

        await ctx.reply(f"Dein {request_long[0]} Eintrag wurde von {old_value} zu {change_to} geändert")

    except CustomErrors.NotUniqueMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except CustomErrors.Custom_Command_End as e:
        print(e)
    except Exception as e:
        print(e)
        traceback.print_exc()
        await ctx.reply("ALARM. ALARM. Ein Eindringling. Dachtest du kannst hier einfach so rumschleichen und die Uniform klauen.")


@bot.command()
async def update(ctx):
    player.create_player_dict()


##test##
@bot.command(aliases=['cow', 'bow', 'tow'])
async def test(ctx):
    author = ctx.message.author
    import bot_functions
    await ctx.reply("moo")
    await bot_functions.call_custom_command(ctx, "r[1d20]", author.id)
