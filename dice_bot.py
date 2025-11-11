import discord
import CustomErrors
import player
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot: {bot.user} online')


@bot.command()
async def r(ctx, to_roll="1d20", *args):
    import bot_functions
    author = ctx.message.author

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.roll_standard_command(ctx, to_roll, author.id)

    except CustomErrors.NotUniqueMatching:                                                             #my custom Error
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching:
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except Exception as e:
        print(e)
        await ctx.reply("Hast Pech gehabt, geht wohl nicht. Must use Format: -r 1d20+2 oder ein Attribut ")

        
        
@bot.command()
async def t(ctx, to_roll="1d20", *args):
    import bot_functions
    author = ctx.message.author

    try:
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.roll_attribute_command(ctx, to_roll, author.id)

    except CustomErrors.NotUniqueMatching:                                                             #my custom Error
        await ctx.reply("Attribut-Eingabe nicht eindeutig")
    except CustomErrors.NotExistingMatching:
        await ctx.reply("Attribut-Eingabe existiert nicht")
    except Exception as e:
        print(e)
        await ctx.reply("Falsches Format. Must use: -r 1d20+2 oder Abwandlungen davon")
    
@bot.command()
async def get(ctx, *, request):
    import bot_functions
    author = ctx.message.author
    request_long = [text for text in player.attribute_list_saves if request in text]
    user_name = player.user_dict[author.id]
    att_dict = player.player_attribute_dict[user_name]
    await ctx.reply(att_dict[request_long[0]])
    
@bot.command()
async def change(ctx, request, change_to):
    import bot_functions
    
    if change_to == None:
        return
    
    author = ctx.message.author
    request_long = [text for text in player.attribute_list_saves if request in text]
    user_name = player.user_dict[author.id]
    att_dict = player.player_attribute_dict[user_name]
    
    att_name_list = list(att_dict)
    att_number_list = list(att_dict.values())
    player_number = list(player.player_attribute_dict)
    player_number = player_number.index(user_name) + 1
    
    request_index = att_name_list.index(request_long[0])
    old_value = att_number_list[request_index]
    att_number_list[request_index] = change_to
    write_string = str(user_name) 
    
    for i in att_number_list:
        write_string += "," + i 
        
    
    with open('player_attribute.txt') as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            lines[player_number] = write_string + "\n"
            with open('player_attribute.txt', "w") as file:
                for line in lines:
                    file.write(line)
                
    await ctx.reply(f"Dein {request_long[0]} Eintrag wurde von {old_value} zu {change_to} geändert")
    
    bot_functions.create_player_dict()
    
@bot.command()
async def ad(ctx, *, to_roll):
    import bot_functions
    author = ctx.message.author
    
    await bot_functions.roll_advantage_command(ctx, to_roll, author.id)

@bot.command()
async def di(ctx, *, to_roll):
    import bot_functions
    author = ctx.message.author
    
    await bot_functions.roll_disadvantage_command(ctx, to_roll, author.id)