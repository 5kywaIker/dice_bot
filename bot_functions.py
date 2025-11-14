import asyncio
import sys
import discord
from discord.ext import commands
import re
import random
import player
import CustomErrors
from dice_bot import bot

#adv_modifier = 0[normal], 1[advantage], 2[disadvantage]
adv_modifier = 0
adv_modifier_attribute = 0

#on Bot start, lade alle Spieler-Werte aus der Text Datei in die Player Class
def create_player_dict():
    
    user_attribute_dict = {}

    for user_id, user_name in player.user_dict.items():
        user_attribute_dict[user_name] = player.set_attribute_dict(user_name)
    player.player_attribute_dict = user_attribute_dict
    return(user_attribute_dict)


#Standard Funktion zum Würfeln. Should move to different file. Handled die Logik fürs Würfeln und die Formatierung der Ausgabe.
async def r_command(ctx, to_roll, player_id, temp_adv_modifier=0):

    global adv_modifier
    global adv_modifier_attribute
    adv_modifier = temp_adv_modifier
    adv_modifier_attribute = temp_adv_modifier

    # notwendig, weil -attack sonst nicht seperat ausgeführt und ausgeprinted werden, bzw alle custom-commands mit "|" seperator. Trennung erfolgt unmittelbar danach
    to_roll = await replace_custom_commands(to_roll, player_id)

    #mehrfach_würfeln, und die ergebnisse seperat zurückgeben, falls anzeigender seperator im string "to_roll" ("|" oder " ")
    #if und else können maybe entfernt werden, wenn to_roll.split("|") eine Liste mit einem Element zurückgibt, falls "|" nicht im String enthalten ist
    if "|" in to_roll:
        to_roll = to_roll.split("|")
        for dice in to_roll:

            # überprüfe ob to_roll nur modifier enthält, wenn ja, dann erweitere to_roll um 1d20 am anfang. Für custom commands die keinen d20 enthalten und "-r dext|+1 oder so
            if not re.search(r"[a-zA-Z]", dice):
                dice = "1d20" + str(dice)

            roll_result_output_string, roll_result_eval, original_input_modified = await roll_standard(ctx, dice, player_id)
            output_message = str(original_input_modified) + ":" + str(roll_result_output_string) + " = " + str(roll_result_eval)
            await ctx.reply(output_message)
    else:

        # überprüfe im anderen case ebenfalls ob to_roll nur modifier enthält, wenn ja, dann erweitere to_roll um 1d20 am anfang
        if not re.search(r"[a-zA-Z]", to_roll):
            to_roll = "1d20" + str(to_roll)

        roll_result_output_string, roll_result_eval, original_input_modified = await roll_standard(ctx, to_roll, player_id)
        output_message = str(original_input_modified) + ":" + str(roll_result_output_string) + " = " + str(roll_result_eval)
        await ctx.reply(output_message)

        adv_modifier = 0
        adv_modifier_attribute = 0


async def ad_command(ctx, to_roll, player_id, temp_adv_modifier=1):
    await r_command(ctx, to_roll, player_id, temp_adv_modifier)

async def di_command(ctx, to_roll, player_id, temp_adv_modifier=2):
    await r_command(ctx, to_roll, player_id, temp_adv_modifier)


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



async def roll_attribute(ctx, to_roll, player_id):
    '''
    bekommt den Namen eines Attributs in to_roll übergeben, guckt den Attr Wert des Spielers nach und würfelt einen d20 mit dem Ergebnis
    :param ctx:Context
    :param to_roll:str
    :param player_id:str
    :return:(str,str,str)
    '''
    #global adv_modifier
    #global adv_modifier_attribute
    #adv_modifier = adv_modifier_attribute
    #code above hat noch probleme, wenn ein custom command mehrere custom commands enthält. Dann kann eventuell damage auf vorteil gewürfelt werden
    #at that point user issue ig

    player_name = player.user_dict[player_id]
    
    if "sav" in to_roll or "sv" in to_roll:                                         #überprüfen ob das Attr ein Modifier ist
        to_roll = re.sub(r"(sav|sv).*", "", to_roll)
        to_roll = await match_substring(player.attribute_list_saves, to_roll)
    else:
        to_roll = await match_substring(player.attribute_list_normal, to_roll)
    
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
    # case wird aktuell bereits in r_command abgefangen
    #kann weiterhin ausgeführt werden, falls der wert von einem custom command mehrere custom commands sind -> muss auf
    if "d" in to_roll_attribute_modifier:

        to_roll_attribute_modifier_list = to_roll_attribute_modifier.split()

        roll_result_output, roll_result_eval, original_input_modified = await roll_standard(ctx, str(to_roll_attribute_modifier), player_id)
    else:
        to_roll_attribute_modifier = int(to_roll_attribute_modifier)    #remove extra leerzeichen, oder mathematische operanten
        roll_result_output, roll_result_eval = await roll_dice()
    
        roll_result_eval += "+" + str(to_roll_attribute_modifier)
        roll_result_output = " [" + roll_result_output + "]" + " + " + str(to_roll_attribute_modifier)

    
    return(roll_result_output, str(roll_result_eval), str(original_input_modified))



async def split_dice_string(string_w)->list:
    """
    splittet den string an allen charakteren die nicht Buchstabe oder Zahl sind
    """
    split_string_list = re.split(r'(\W)', string_w)
    if "" in split_string_list:
        split_string_list.remove("")
    return(split_string_list)


async def replace_custom_commands(to_roll, player_id):
    """
    check ob einer der eingabewerte ein custom command ist und ersetze den custom command durch den custom modifier-wert
    """
    temp_to_roll = await split_dice_string(to_roll)
    temp_player_name = player.user_dict[player_id]
    to_roll = ""

    for i in range(len(temp_to_roll)):
        temp_einzel_eingabe = temp_to_roll[i]

        custom_attribute_list = await match_substring(player.attribute_list_custom, temp_einzel_eingabe)
        if len(custom_attribute_list) == 1:

            custom_modifier = str(player.player_attribute_dict.get(temp_player_name)[custom_attribute_list[0]])
            custom_modifier_list = await split_dice_string(custom_modifier)
            custom_modifier = ""
            for custom in range(len(custom_modifier_list)):
                nested_modifier = custom_modifier_list[custom]
                nested_command_list = await match_substring(player.attribute_list_custom, nested_modifier)

                if len(nested_command_list) == 1:
                    custom_modifier_list[custom] = await replace_custom_commands(nested_command_list[0], player_id)
                elif len(nested_command_list) > 1:
                    raise CustomErrors.NotUniqueMatching
            for custom in range(len(custom_modifier_list)):
                custom_modifier += custom_modifier_list[custom]
            temp_to_roll[i] = custom_modifier

        elif len(custom_attribute_list) > 1:
            raise CustomErrors.NotUniqueMatching

    for i in temp_to_roll:
        to_roll += i
    ####

    return(to_roll)


# to do Füge überprüfung ob len(matching_list) >1, == 1 oder 0 ein.
#werfe error auf >1, return andernfalls
async def match_substring(list_to_search, search_string):
    """
    Looks through a list of strings and returns all strings that match or contain "search_string" as a sub_string
    """
    matching_list = [text for text in list_to_search if search_string in text]

    return(matching_list)


async def call_custom_command(ctx, custom_command, player_id):
    current_module = sys.modules["bot_functions"]
    custom_command_list = re.split(r'\[|\]', custom_command)
    if "" in custom_command_list:
        custom_command_list.remove("")
    custom_command = custom_command_list[0]
    custom_command += "_command"
    custom_command = await getattr(current_module, custom_command)(ctx, custom_command_list[1], player_id)
    print(custom_command)



    

