import sys
import re
import player
import CustomErrors
import dice_roller
from player import attribute_list


#Standard Funktion zum Würfeln. Should move to different file. Handled die Logik fürs Würfeln und die Formatierung der Ausgabe.
async def r_command(ctx, to_roll, player_id, temp_adv_modifier=0):

    dice_roller.adv_modifier = temp_adv_modifier
    dice_roller.adv_modifier_attribute = temp_adv_modifier

    # notwendig, weil -attack sonst nicht seperat ausgeführt und ausgeprinted werden, bzw alle custom-commands mit "|" seperator. Trennung erfolgt unmittelbar danach
    to_roll = await replace_custom_attribute(to_roll, player_id)

    #auf nested commands prüfen, falls nested command, dann den entsprechend command aufrufen. Nach dem command wird der code beendet. Weitere teile von to_roll werden ignoriert
    if "[" in to_roll:
        await call_custom_command(ctx, to_roll, player_id)

    #mehrfach_würfeln, und die ergebnisse seperat zurückgeben, falls anzeigender seperator im string "to_roll" ("|" oder " ")
    #if und else können maybe entfernt werden, wenn to_roll.split("|") eine Liste mit einem Element zurückgibt, falls "|" nicht im String enthalten ist

    to_roll = to_roll.split("|")
    for dice in to_roll:

        # überprüfe ob to_roll nur modifier enthält, wenn ja, dann erweitere to_roll um 1d20 am anfang. Für custom commands die keinen d20 enthalten und "-r dext|+1 oder so
        if not re.search(r"[a-zA-Z]", dice):
            dice = "1d20" + str(dice)

        roll_result_output_string, roll_result_eval, original_input_modified = await dice_roller.roll_standard(ctx, dice, player_id)
        output_message = str(original_input_modified) + ":" + str(roll_result_output_string) + " = " + str(roll_result_eval)
        await ctx.reply(output_message)

    dice_roller.adv_modifier = 0
    dice_roller.adv_modifier_attribute = 0


async def ad_command(ctx, to_roll, player_id, temp_adv_modifier=1):
    await r_command(ctx, to_roll, player_id, temp_adv_modifier)

async def di_command(ctx, to_roll, player_id, temp_adv_modifier=2):
    await r_command(ctx, to_roll, player_id, temp_adv_modifier)


#maybe auch im schreibcommand einfach nochmal über play_custom.txt loopen, bis line.replace("\n", "").split(";")[0] == player_name,
#und dann line.replace("\n", "").split(";")[content(content.index(line)-1).replace("\n", "").split(";").index(to_change)] = to_change
async def change_command(ctx, request, change_to, player_id):
    request_type = ""               #art des request commands, ob attribute, custom oder spell
    request_index = 0               #index in der attribute liste des spielers, in welchem der requested command steht (in player_type.txt
    att_modifier_list = []          #liste mit allen modifiern des spielers aus der jeweiligen player_type.txt
    request_long_list = await match_substring(player.attribute_list, request)

    ### todo: in match_string einbinden!
    if len(request_long_list) == 0:
        raise CustomErrors.NotExistingMatching
    ###

    request_long = request_long_list[0]

    #gibt zurück ob das attribut in attribute, custom oder spells ist
    for k, v in player.attribute_dict.items():
        if request_long in v:
            request_type = k
            break

    if request_type == "":
        raise CustomErrors.NotExistingMatching

    file_name_string = f'player_{request_type}.txt'
    user_name = player.user_dict[player_id]
    att_dict = player.player_attribute_dict[user_name]

    att_name_list = list(att_dict)                          #gibt alle keys aus dem attribute dict des spielers, der den Command aufgerufen hat
    player_number = list(player.player_attribute_dict)
    player_number = player_number.index(user_name)

    #hole request_index und att_modifier_list aus player_tyoe.txt

    player_number = player_number * 2
    with open(file_name_string) as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            att_modifier_list = lines[player_number].replace("\n", "").split(";")
            for i in range(len(att_modifier_list)):
                if att_modifier_list[i] == request_long:
                    request_index = i
                    att_modifier_list = lines[player_number+1].replace("\n", "").split(";")
                    break
    player_number = player_number + 1                       #setze player_number auf die zeile der textdatei in welcher die Modifier des Spielers stehen


    old_value = att_modifier_list[request_index]
    att_modifier_list[request_index] = change_to
    write_string = str(user_name)

    #schreibe in write string die attribute
    for i in att_modifier_list[1:]:
        write_string += ";" + i


    with open(file_name_string) as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            lines[player_number] = write_string + "\n"
            with open(file_name_string, "w") as file:
                for line in lines:
                    file.write(line)

    player.create_player_dict()
    return(request_long, old_value)


async def split_dice_string(string_w)->list:
    """
    splittet den string an allen charakteren die nicht Buchstabe oder Zahl sind
    """
    split_string_list = re.split(r'(\W)', string_w)
    if "" in split_string_list:
        split_string_list.remove("")
    return(split_string_list)


async def create_costom_command(ctx, command_name, modifier, player_id):

    return

async def create_spell_command(ctx, command_name, modifier, player_id, spell_scaling, spell_level):

    return

async def replace_custom_attribute(to_roll, player_id):
    """
    checkt beim würfeln ob einer der eingabewerte ein custom command ist und ersetze den custom command durch den custom modifier-wert
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
                    custom_modifier_list[custom] = await replace_custom_attribute(nested_command_list[0], player_id)
                elif len(nested_command_list) > 1:
                    raise CustomErrors.NotUniqueMatching
            for custom in range(len(custom_modifier_list)):
                custom_modifier += custom_modifier_list[custom]
            temp_to_roll[i] = custom_modifier

        elif len(custom_attribute_list) > 1:
            raise CustomErrors.NotUniqueMatching

    for i in temp_to_roll:
        to_roll += i

    return(to_roll)


# todo Füge überprüfung ob len(matching_list) >1, == 1 oder 0 ein.
#werfe error auf >1, return andernfalls
#todo: füge überprüfung ein, ob saving throw oder nicht, indem to_roll auf sv überprüft wird, maybe return in welcher liste der wert gefunden wurde (normal, save, custom, spell)
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
    await getattr(current_module, custom_command)(ctx, custom_command_list[1], player_id)
    dice_roller.adv_modifier = 0
    dice_roller.adv_modifier_attribute = 0
    raise CustomErrors.Custom_Command_End