import traceback
import discord
import CustomErrors
import player
from discord import app_commands
from discord.ext import commands
import bot_commands
import bot_functions

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot: {bot.user} online')
    await bot.tree.sync(guild=discord.Object(id=1174375949081514014))

def roll_channel_check():
    def predicate(ctx) -> bool:
        return ctx.channel.name == "they-see-me-rolling" or ctx.channel.name == "test"
    return commands.check(predicate)

@bot.command(aliases=['t', 'rm'])
@roll_channel_check()
async def r(ctx, to_roll="1d20", *args):
    async with ctx.channel.typing():
        author = ctx.message.author
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_commands.r_command(ctx, to_roll, author.id)


@bot.command(aliases=['ra'])
@roll_channel_check()
async def ad(ctx, to_roll="1d20", *args):
    #-ad +modifier würfeln, standard wurf auch ausführen wenn nur modifier übergeben wird
    #dafür überprüfen ob ein Buchstabe im Inputstring enthalten ist, ansonsten wurden nur modifier übergeben und der string sollte um "1d20" erweitert werden
    author = ctx.message.author

    async with ctx.channel.typing():
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_commands.ad_command(ctx, to_roll, author.id, 1)

@bot.command(aliases=['rd'])
@roll_channel_check()
async def di(ctx, to_roll="1d20", *args):
    author = ctx.message.author
    async with ctx.channel.typing():
        if len(args) != 0:
            for item in args:
                to_roll += "|"+ str(item)
        await bot_commands.di_command(ctx, to_roll, author.id, 2)

@bot.command(aliases=['att','at','atta','attac'])
@roll_channel_check()
async def attack(ctx, to_roll="attack", *args):
    author = ctx.message.author
    async with ctx.channel.typing():
        if not to_roll == "attack":
            to_roll = to_roll + "+" + "attack"

        if len(args) != 0:
            for item in args:
                to_roll += str(item)
        await bot_commands.r_command(ctx, to_roll, author.id)

@bot.command()
@roll_channel_check()
async def show(ctx, *, request):
    async with ctx.channel.typing():
        author = ctx.message.author
        modifier = await bot_commands.show_command(ctx, request, author.id)
        await ctx.reply(modifier)

@bot.command(aliases=['show_all'])
@roll_channel_check()
async def showall(ctx, *args):
    async with ctx.channel.typing():
        author = ctx.message.author
        name_list = await bot_commands.showall_command(ctx, author.id)
        await ctx.reply(name_list)

@bot.hybrid_command(name="delete", with_app_command=True, description="Löcsht den Namen und Wert eines Attributes", aliases=['del','remove','re'])
@app_commands.guilds(discord.Object(id=1174375949081514014))
@app_commands.describe(attribute='Name des zu löschenden Attributs')
@roll_channel_check()
async def delete(ctx, attribute):
    async with ctx.channel.typing():
        author = ctx.message.author
        request_long, old_value = await bot_commands.delete_command(ctx, attribute, author.id)


@bot.hybrid_command(name="change", with_app_command=True, description="Ändert den Wert eines Attributes", aliases=["change_attr"])
@app_commands.guilds(discord.Object(id=1174375949081514014))
@app_commands.describe(attribute='Name des Attributs', change_to='Neuer Modifier',)
@roll_channel_check()
async def change(ctx, attribute, change_to):
    async with ctx.channel.typing():
        if change_to is None:
            await ctx.reply("Keinen aktuellen Wert zu dem gechanged werden soll übergeben")
            return

        author = ctx.message.author
        request_long, old_value = await bot_commands.change_command(ctx, attribute, change_to, author.id)

@delete.autocomplete("attribute")
async def delete_autocomplete(interaction: discord.Interaction, current):
    """Wenn der Spieler /delete ausführt, werden alle Attribute des Spielers aus player_custom und player_spells angezeigt."""
    #Da nur aus _custom und _spells gelöscht werden darf, werden auch nur Elemente hinter "persuasion" angezeigt (das letzte Element in _attribute).
    #wenn man player.attribute_list_custom_spells nimmt, würde auch custom attribute von anderen Spielern angezeigt werden, darum wird das player_attribute_dict gerufen.
    player_name = player.user_dict[interaction.user.id]
    attribute_list = list(player.player_attribute_dict.get(player_name).keys())
    cut_point = attribute_list.index("persuasion") + 1
    attribute_list = attribute_list[cut_point:]
    return_list = [app_commands.Choice(name=attribute, value=attribute) for attribute in attribute_list if
                   current.lower() in attribute.lower()]
    if len(return_list) > 25:
        return_list = return_list[-25:]
    return return_list
@change.autocomplete("attribute")
async def change_autocomplete(interaction: discord.Interaction, current):
    """Wenn der Spieler /change ausführt, werden für die Eingabe Attribute die ersten 25 Attribute aus attribute_list angezeigt."""
    #maybe auch noch ändern, dass er list(player.player_attribute_dict.get(player_name).keys()) statt attribute_list nimmt, um keine Attribute von anderen Leuten vorgeschlagen zu bekommen.
    attribute_list = player.attribute_list
    return_list = [app_commands.Choice(name=attribute, value=attribute) for attribute in attribute_list if current.lower() in attribute.lower()]
    if len(return_list)>25:
        return_list = return_list[:25]
    return return_list
@change.autocomplete("change_to")
async def change_autocomplete(interaction: discord.Interaction, current):
    """Wenn der Spieler /change ausführt, wird für die Eingabe change_to der Modifier für das in "attribute" ausgewählte Attribut angezeigt."""
    attribute_value_list = []
    player_name = player.user_dict[interaction.user.id]
    attribute_long = await bot_functions.match_substring(player.attribute_list, interaction.namespace.attribute)
    for attribute in attribute_long:
        value = str(player.player_attribute_dict.get(player_name)[attribute])
        attribute_value_list.append(value)
    return_list = [app_commands.Choice(name=change_to, value=change_to) for change_to in attribute_value_list if current.lower() in change_to.lower()]
    if len(return_list)>25:
        return_list = return_list[:25]
    return return_list


@bot.hybrid_command(name="new", with_app_command=True, description="Erstellt ein neues Attribut", aliases=['create_custom', 'create'])
@app_commands.guilds(discord.Object(id=1174375949081514014))
@roll_channel_check()
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
        await bot_commands.new_command(ctx, command_name, modifier, author.id)
        await ctx.reply(f"Custom Command {command_name} wurde mit dem Modifier {modifier} erstellt.")

@bot.hybrid_command(name="new_spell", with_app_command=True, description="Erstellt einen neuen Spell", aliases=['create_spell'])
@app_commands.guilds(discord.Object(id=1174375949081514014))
@app_commands.describe(spell_name='Name des neuen Spells', modifier='Was gewürfelt wird, wenn man den Spell castet',
                       upcast_modifier="Was pro Upcast Level zusätzlich gewürfelt wird, z.B. '+1d6'. Das Pluszeichen ist wichtig.",
                       spell_level="das Grundlevel des Spells. Ist 0 bei cantrips.")
@roll_channel_check()
async def new_spell(ctx, spell_name, modifier, upcast_modifier, spell_level):
    async with ctx.channel.typing():
        author = ctx.message.author
        await bot_commands.new_spell_command(ctx, spell_name, modifier, author.id, upcast_modifier, spell_level)
        await ctx.reply(f"Der Level {spell_level} Spell {spell_name} wurde mit dem Modifier {modifier} erstellt.")

@bot.command()
@roll_channel_check()
async def update(ctx):
    player.create_player_dict()

#TODO on_error handler schreiben, der Errors abfängt, die beim fehlerhaften Aufruf von Befehlen auftreten
@bot.event
async def on_command_error(ctx, error, *args):
    try:
        if isinstance(error.original, CustomErrors.NotUniqueMatching):
            await ctx.reply(f'Attribut Eingabe "{error.original.attr}" nicht eindeutig.')
        elif isinstance(error.original, CustomErrors.NotExistingMatching):
            await ctx.reply(f'Attribut Eingabe "{error.original.attr}" existiert nicht. Wenn du dich nicht vertippt hast, kannst du es mit /new erstellen')
        elif isinstance(error.original, CustomErrors.AlreadyExisistingError):
            await ctx.reply(f'Das Attribut "{error.original.attr}" existiert bereits. Benutze /change um es zu verändern.')
        elif isinstance(error.original, commands.MissingRequiredArgument):
            await ctx.reply('Falsche Eingabe. Übergebe entweder zwei Paramter: "Name_des_Attributs" "Wert des Attributs" um ein Attribut zu erstellen, oder vier Parameter: "Name_des_Spells" "Was_der_Spell_würfeln_soll" "+was_beim_upcast_drauf_kommt" "base_Level_des_spells"' )
        elif isinstance(error.original, CustomErrors.SpecificError):
            await ctx.reply(error.original.message)
        elif isinstance(error.original, CustomErrors.TooManyInputs):
            await ctx.reply('Zu viele Werte übergeben. Sollte "-new command_name modifier" sein. Optional für Spells noch "spell_skalierung spell_level" eingeben' )
        elif isinstance(error.original, CustomErrors.CustomCommandEnd):
            print(error)
        elif isinstance(error.original.original, KeyError):
            await ctx.reply('Custom Attribut nicht in eigener Liste vorhanden. Use -new um Attribut zu erstellen.')
        elif isinstance(error.original.original, IndexError):
            await ctx.reply('Attribut Eingabe existiert nicht.')
        else:
            print(error)
            traceback.print_exc()
            await ctx.reply(f"Error - {error}")
    except Exception:
        print(error)
        traceback.print_exc()
        await ctx.reply(f"Error - {error}")

##test##
@bot.hybrid_command(name="test", with_app_command=True, description="Testing")
@app_commands.guilds(discord.Object(id=1174375949081514014))
async def test(ctx):
    await ctx.reply("moo")
