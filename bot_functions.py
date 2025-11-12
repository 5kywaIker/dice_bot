import asyncio
import discord
from discord.ext import commands
import re
import random
import player
import CustomErrors
from dice_bot import bot

adv_modifier = 0

#on Bot start, lade alle Spieler-Werte aus der Text Datei in die Player Class
def create_player_dict():
    
    user_attribute_dict = {}

    for user_id, user_name in player.user_dict.items():
        user_attribute_dict[user_name] = player.set_attribute_dict(user_name)
    player.player_attribute_dict = user_attribute_dict
    return(user_attribute_dict)


#Standard Funktion zum Würfeln. Should move to different file. Handled die Logik fürs Würfeln und die Formatierung der Ausgabe.
async def roll_standard_command(ctx, to_roll, player_id, temp_adv_modifier=0):

    global adv_modifier
    adv_modifier = temp_adv_modifier

    #überprüfe ob to_roll nur modifier enthält, wenn ja, dann erweitere to_roll um 1d20 am anfang
    if not re.search(r"[a-zA-Z]", to_roll):
        to_roll = "1d20" + str(to_roll)

    #check ob einer der eingabewerte ein custom command ist und ersetze den custom command durch den custom modifier-wert
    temp_to_roll = await split_dice_string(to_roll)
    temp_player_name = player.user_dict[player_id]
    to_roll = ""

    for i in range(len(temp_to_roll)):
        temp_einzel_eingabe = temp_to_roll[i]
        temp_attribute = [text for text in player.attribute_list if temp_einzel_eingabe in text]

        temp_attribute = [text for text in player.attribute_list_custom if temp_einzel_eingabe in text]
        if len(temp_attribute) == 1:

            temp_to_roll_attribute_modifier = str(player.player_attribute_dict.get(temp_player_name)[temp_attribute[0]])
            temp_to_roll[i] = temp_to_roll_attribute_modifier
            if len(temp_attribute) > 1:
                raise CustomErrors.NotUniqueMatching

    for i in temp_to_roll:
        to_roll += i
    ####



    #mehrfach_würfel, falls anzeigender seperator im string "to_roll"
    if "|" in to_roll:
        to_roll = to_roll.split("|")
        for dice in to_roll:
            roll_result_output_string, roll_result_eval, original_input_modified = await roll_standard(ctx, dice, player_id)
            output_message = str(original_input_modified) + ":" + str(roll_result_output_string) + " = " + str(roll_result_eval)
            await ctx.reply(output_message)
    else:
        roll_result_output_string, roll_result_eval, original_input_modified = await roll_standard(ctx, to_roll, player_id)
        output_message = str(original_input_modified) + ":" + str(roll_result_output_string) + " = " + str(roll_result_eval)
        await ctx.reply(output_message)


async def roll_advantage_command(ctx, to_roll, player_id, temp_adv_modifier):
    await roll_standard_command(ctx, to_roll, player_id, temp_adv_modifier)


async def roll_standard(ctx, to_roll, player_id):
    original_input = to_roll

    
    roll_result_eval_string = ""        #zum tracken und späteren addieren der Würfelergebnisse
    roll_result_output_string = ""      #zum tracken und späteren printen der Würfelergebnisse
    was_rolled = False                  #für die Formatierung der Ausgabe
    original_input_modified = ""


    # Teile den Input Befehl in ein Array auf mit selbstgebauter funktion weiter unten
    # aus '1d20+1d10+7' wird ['1d20', '+', '1d10', '+', '7']
    to_roll_list = await split_dice_string(to_roll)

    #gehe das Array durch, wenn ein Eintrag "d" enthält, würfele den entsprechenden Würfel
    #tracke die Ergebnisse in zwei verschiedenen Strings, eval & output
    for dice in to_roll_list:

        if re.search(r"^[a-zA-Z][a-zA-Z]", dice):                                   #überprüfen, ob attribut übergeben wurde
            dice_output, dice_eval, dice = await roll_attribute(ctx, dice, player_id)
        elif "d" in dice:                                                           #überprüfen ob d20 übergeben wurde
            dice_output, dice_eval = await roll_dice(dice)
            if was_rolled == False:                                                 #Formatierung von []
                roll_result_output_string += " ["
                was_rolled = True
            else:
                roll_result_output_string += ", "
        else:                                                                       #sonst einfach die Übergabe zurück geben
            if was_rolled == True:
                roll_result_output_string += "] "
                was_rolled = False
            else:
                roll_result_output_string += " "
            dice_output = dice
            dice_eval = dice
        roll_result_output_string += str(dice_output)
        roll_result_eval_string += str(dice_eval)

        original_input_modified += str(dice) + " "

    if was_rolled:
        roll_result_output_string += "]"
    roll_result_eval = eval(roll_result_eval_string)

    return(roll_result_output_string, str(roll_result_eval), original_input_modified)
 
    
#würfele "1d20" Würfel o.ä. - Eingabe als String mit dem Würfel ohne Modifier. Ohne Eingabe Würfele einen d20
async def roll_dice(to_roll="1d20"):
    to_roll_list = re.split(r'd', to_roll)
    number_of_dice = int(to_roll_list[0])
    dice_size = int(to_roll_list[1])
    roll_result_output = ""
    roll_result_eval = 0
    global adv_modifier

    if not adv_modifier == 0:

        if adv_modifier == 1:
            for i in range(0, number_of_dice):

                rolled_number1 = random.randint(1, dice_size)
                rolled_number2 = random.randint(1, dice_size)
                rolled_number = max(rolled_number1, rolled_number2)
                if 0 < i < number_of_dice:
                    roll_result_output += "]" " + " "["
                roll_result_output += str(rolled_number1) + ", " + str(rolled_number2)
                roll_result_eval += rolled_number

        if adv_modifier == 2:
            for i in range(0, number_of_dice):

                rolled_number1 = random.randint(1, dice_size)
                rolled_number2 = random.randint(1, dice_size)
                rolled_number = min(rolled_number1, rolled_number2)
                if 0 < i < number_of_dice:
                    roll_result_output += "]" " + " "["
                roll_result_output += str(rolled_number1) + ", " + str(rolled_number2)
                roll_result_eval += rolled_number

    else:
        for i in range(0, number_of_dice):

            rolled_number = random.randint(1, dice_size)
            if 0 < i < number_of_dice:
                roll_result_output += ", "
            roll_result_output += str(rolled_number)
            roll_result_eval += rolled_number

    adv_modifier = 0
    return(roll_result_output, str(roll_result_eval))


#bekommt den Namen eines Attributs in to_roll übergeben, guckt den Attr Wert des Spielers nach und mit dem Ergebnis
async def roll_attribute(ctx, to_roll, player_id):
    
    player_name = player.user_dict[player_id]
    
    if "sav" in to_roll or "sv" in to_roll:                                         #überprüfen ob das Attr ein Modifier ist
        to_roll = re.sub(r"(sav|sv).*", "", to_roll)
        to_roll = [text for text in player.attribute_list_saves if to_roll in text]
    else:
        to_roll = [text for text in player.attribute_list_normal if to_roll in text]               
    
    if len(to_roll) == 0:
        raise CustomErrors.NotExistingMatching
    if len(to_roll) > 1:    
        raise CustomErrors.NotUniqueMatching                                            #custom Error
    
    to_roll = to_roll[0]
    
    #Mit dem Spielernamen wird das Dict des Spielers abgerufen
    #daraus wird der Wert des angefragten Attributs in to_roll_attribute_modifier geschrieben
    to_roll_attribute_modifier = str(player.player_attribute_dict.get(player_name)[to_roll])

    #original_input auf attribute_namen_kurz setzen, wenn standard attribut gewürfelt wurde
    if "save" in to_roll:
        original_input_modified = str(to_roll[:4]) + "sv"
    else:
        original_input_modified = to_roll[:4]

    #wenn das Attribut als Wert einen String im Format "1d20+6|2d6+4" o.ä. hat
    #dann muss der String aufgesplittet werden, und die einzelnen Eingaben seperat gewürfelt werden
    #if "|" in to_roll_attribute_modifier:
        #to_roll_attribute_modifier_list = to_roll_attribute_modifier.split("|")
        #for attribute_modifier

    #wenn custom attribut mit d20/d12/d10 etc im modifier, dann roll_standard mit modifier aufrufen, ansonsten 1d20 würfeln und standard attribut addieren
    if "d" in to_roll_attribute_modifier:

        to_roll_attribute_modifier_list = to_roll_attribute_modifier.split()

        roll_result_output, roll_result_eval, original_input_modified = await roll_standard(ctx, str(to_roll_attribute_modifier), player_id)
    else:
        to_roll_attribute_modifier = int(to_roll_attribute_modifier)    #remove extra leerzeichen, oder mathematische operanten
        roll_result_output, roll_result_eval = await roll_dice()
    
        roll_result_eval += "+" + str(to_roll_attribute_modifier)
        roll_result_output = " [" + roll_result_output + "]" + " + " + str(to_roll_attribute_modifier)

    
    return(roll_result_output, str(roll_result_eval), str(original_input_modified))

async def roll_attribute_command(ctx, to_roll, player_id):
    await roll_standard_command(ctx, to_roll, player_id)
    return

    
async def split_dice_string(string_w)->list:
    split_string_list = re.split(r'(\W)', string_w)
    if "" in split_string_list:
        split_string_list.remove("")
    return(split_string_list)






async def befehle_command(ctx):
    command_list = [f'- {command.name}' for command in bot.commands]
    formatted_commands = '\n'.join(command_list)
    response = f'Command Liste:\n{formatted_commands}\n'
    await send_formatted(ctx, response)

async def send_formatted(ctx, msg):
    formatted_msg = f'{msg}'
    await ctx.send(formatted_msg)



    

