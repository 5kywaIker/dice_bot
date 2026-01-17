import traceback
import discord
import CustomErrors
import player
from discord import app_commands
from discord.ext import commands
import bot_functions

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot: {bot.user} online')
    await bot.tree.sync(guild=discord.Object(id=1174375949081514014))

def roll_channel_check():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.channel.name == "they-see-me-rolling" or interaction.channel.name == "test"
    return app_commands.check(predicate)

@bot.command(aliases=['t', 'rm'])
@roll_channel_check()
async def r(ctx, to_roll="1d20", *args):
    async with ctx.channel.typing():
        author = ctx.message.author

        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)

            await bot_functions.r_command(ctx, to_roll, author.id)

        
@bot.command(aliases=['ra'])
@roll_channel_check()
async def ad(ctx, to_roll="1d20", *args):
    #-ad +modifier würfeln, standard wurf auch ausführen wenn nur modifier übergeben wird
    #dafür überprüfen ob ein Buchstabe im Inputstring enthalten ist, ansonsten wurden nur modifier übergeben und der string sollte um "1d20" erweitert werden

    import bot_functions
    author = ctx.message.author

    async with ctx.channel.typing():
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.ad_command(ctx, to_roll, author.id, 1)

@bot.command(aliases=['rd'])
@roll_channel_check()
async def di(ctx, to_roll="1d20", *args):
    import bot_functions
    author = ctx.message.author
    async with ctx.channel.typing():
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_functions.di_command(ctx, to_roll, author.id, 2)

@bot.command(aliases=['att','at','atta','attac'])
async def attack(ctx, to_roll="attack", *args):
    author = ctx.message.author
    async with ctx.channel.typing():
        if not to_roll == "attack":
            to_roll = to_roll + "+" + "attack"

        if len(args) != 0:
            for item in args:
                to_roll += str(item)
        await bot_functions.r_command(ctx, to_roll, author.id)

@bot.command()
async def get(ctx, *, request):
    async with ctx.channel.typing():
        import bot_functions
        author = ctx.message.author
        modifier = await bot_functions.get_command(ctx, request, author.id)
        await ctx.reply(modifier)

@bot.command(aliases=['get_all'])
async def getall(ctx, *args):
    async with ctx.channel.typing():
        import bot_functions
        author = ctx.message.author
        name_list = await bot_functions.getall_command(ctx, author.id)
        await ctx.reply(name_list)

@bot.command(aliases=['del','remove','re'])
async def delete(ctx, request, *args):
    import bot_functions

    async with ctx.channel.typing():
        if not len(args) == 0:
            await ctx.reply("Zu viele Werte zu denen gechanged werden sollen übergeben")
            return

        author = ctx.message.author
        request_long, old_value = await bot_functions.delete_command(ctx, request, author.id)

        await ctx.reply(f"Dein {request_long} Eintrag mit dem Inhalt {old_value} wurde gelöscht")


@bot.hybrid_command(name="change", with_app_command=True, description="Ändert den Wert eines Attributes", aliases=["change_attr"])
@app_commands.guilds(discord.Object(id=1174375949081514014))
@app_commands.describe(attribute='Name des Attributs', change_to='Neuer Modifier',)
async def change(ctx, attribute, change_to):
    import bot_functions

    async with ctx.channel.typing():
        if change_to is None:
            await ctx.reply("Keinen aktuellen Wert zu dem gechanged werden soll übergeben")
            return

        author = ctx.message.author
        request_long, old_value = await bot_functions.change_command(ctx, attribute, change_to, author.id)

        await ctx.reply(f"Dein {request_long} Eintrag wurde von {old_value} zu {change_to} geändert")

@change.autocomplete("attribute")
async def change_autocomplete(ctx, current):
    attribute_list = player.attribute_list
    return [
        app_commands.Choice(name=attribute, value=attribute)
        for attribute in attribute_list if current.lower() in attribute.lower()]
#@change.autocomplete("change_to")
#async def change_autocomplete(ctx, current):
#    current = await bot_functions.match_substring(player.attribute_list, current)
#    return list(player.player_attribute_dict.get(player.user_dict[ctx.author])[current[0]])

@bot.command()
async def update(ctx):
    player.create_player_dict()


@bot.hybrid_command(name="new", with_app_command=True, description="Erstellt ein neues Attribut", aliases=['create_custom', 'create'])
@app_commands.guilds(discord.Object(id=1174375949081514014))
async def new(ctx, command_name, modifier):
    """
    Adds a custom modifier either to the player_custom.txt or to the players_spells.txt. Eingabeformat: -new attributname was_zu_würfeln_ist
    :param ctx: Unwichtig für den User
    :param command_name: Hier den Namen eingeben wie das Attribut heißen soll.
    :param modifier: Hier eingeben, was gewürfelt werden soll, wenn der Command aufgerufen wird
    :return:(str,str,str)
    """
    async with ctx.channel.typing():
        author = ctx.message.author
        await bot_functions.new_command(ctx, command_name, modifier, author.id)
        await ctx.reply(f"Custom Command {command_name} wurde mit dem Modifier {modifier} erstellt.")

@bot.hybrid_command(name="new_spell", with_app_command=True, description="Erstellt einen neuen Spell", aliases=['create_spell'])
@app_commands.guilds(discord.Object(id=1174375949081514014))
@app_commands.describe(spell_name='Name des neuen Spells', modifier='Was gewürfelt wird, wenn man den Spell castet',
                       upcast_modifier="Was pro Upcast Level zusätzlich gewürfelt wird, z.B. '+1d6'. Das Pluszeichen ist wichtig.",
                       spell_level="das Grundlevel des Spells. Ist 0 bei cantrips.")
async def new_spell(ctx, spell_name, modifier, upcast_modifier, spell_level):
    async with ctx.channel.typing():
        author = ctx.message.author
        await bot_functions.new_spell_command(ctx, spell_name, modifier, author.id, upcast_modifier, spell_level)
        await ctx.reply(f"Der Level {spell_level} Spell {spell_name} wurde mit dem Modifier {modifier} erstellt.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error.original, CustomErrors.NotUniqueMatching):
        await ctx.reply("Attribut Eingabe nicht eindeutig.")
    elif isinstance(error.original, IndexError):
        await ctx.reply("Attribut Eingabe existiert nicht.")
    elif isinstance(error.original, CustomErrors.NotExistingMatching):
        await ctx.reply("Attribut Eingabe existiert nicht. Wenn du dich nicht vertippt hast, kannst du erstellen mit /new")
    elif isinstance(error.original, commands.MissingRequiredArgument):
        await ctx.reply("Falsche Eingabe. Übergebe entweder zwei Paramter: 'Name_des_Attributs' 'Wert des Attributs' um ein Attribut zu erstellen, oder vier Parameter: 'Name_des_Spells' 'Was_der_Spell_würfeln_soll' '+was_beim_upcast_drauf_kommt' 'base_Level_des_spells'" )
    elif isinstance(error.original, CustomErrors.NotEnoughSpellSlots):
        await ctx.reply(f"Du hast nicht genug Spell Slots um diesen Spell auf Level {CustomErrors.NotEnoughSpellSlots.args[0]} zu casten")
    elif isinstance(error.original, CustomErrors.TooManyInputs):
        await ctx.reply("Zu viele Werte übergeben. Sollte '-new command_name modifier' sein. Optional für Spells noch ' spell_skalierung spell_level' eingeben" )
    elif isinstance(error.original, CustomErrors.CustomCommandEnd):
        print(error)
    elif isinstance(error.original, KeyError):
        await ctx.reply("Custom Attribut nicht in eigener Liste vorhanden. Use -new um Attribut zu erstellen.")
    else:
        print(error)
        traceback.print_exc()
        await ctx.reply(f"Error - {error}")


##test##
@bot.hybrid_command(name="test", with_app_command=True, description="Testing")
@app_commands.guilds(discord.Object(id=1174375949081514014))
async def test(ctx):
    await ctx.reply("moo")
