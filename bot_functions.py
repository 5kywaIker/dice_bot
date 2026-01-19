import sys
import re
import player
import CustomErrors
import dice_roller

async def call_custom_command(ctx, custom_command, player_id):
    current_module = sys.modules["bot_commands"]

    # change[stre ad[6]] funktioniert nicht, weil die eckigen klammern im inneren auch aufgelöst werden. Darf nur an der ersten und letzten Klammer splitten.
    # nach dem initialen split muss das innere der klammer noch gesplittet werden. Maybe syntax Kommata, wie bei spell aufrufen
    # ad[6]+5 funktioniert auch nicht
    # nuke the entire thing and rewrite it properly.
    # input an der ersten und letzten klammer splitten. Alles dazwischen bei kommas trennen (was ist mit strings mit kommas (s. print comm)). Was machen wir mit input hinter den eckigen klammern?

    # custom_command_list = re.split(r"\[|\]", custom_command)
    custom_command_list = custom_command.rsplit(']', 1)
    custom_command_list2 = custom_command_list[0].split("[", 1)
    custom_command_list.pop(0)
    custom_command_list = custom_command_list2 + custom_command_list

    while "" in custom_command_list:
        custom_command_list.remove("")
    custom_command = custom_command_list[0]
    custom_command += "_command"
    to_roll = ""

    # if abfragen durch funktionsaufruf mit *args behandeln
    if len(custom_command_list) > 2:
        if custom_command == "spell_command":
            await getattr(current_module, custom_command)(ctx, custom_command_list[1], player_id, custom_command_list[2])
        elif custom_command == "change_command":
            custom_command_list[1] = custom_command_list[1].split(",")
            await getattr(current_module, custom_command)(ctx, custom_command_list[1][0], custom_command_list[1][1], player_id)
        else:
            for modifier in custom_command_list[2:]:
                to_roll += str(modifier)
            await getattr(current_module, custom_command)(ctx, to_roll, player_id)
    elif custom_command == "change_command":
        custom_command_list[1] = custom_command_list[1].split(",")
        await getattr(current_module, custom_command)(ctx, *custom_command_list[1], player_id)
    else:
        await getattr(current_module, custom_command)(ctx, custom_command_list[1], player_id)
    dice_roller.adv_modifier = 0
    dice_roller.adv_modifier_attribute = 0
    return


async def replace_attribute(to_roll, player_id):
    """
    checkt beim würfeln ob einer der eingabewerte ein attribut ist und ersetze das Attribut durch den modifier-wert.
    Ist der selbe Code wie replace_custom_attribute, nur der match_substring Aufruf übergibt die Liste mit allem Attributen.
    Der Rekursive Aufruf ruft auch sich selber auf.
    """
    temp_to_roll = await split_dice_string(to_roll)
    temp_player_name = player.user_dict[player_id]
    pos1 = 0
    pos2 = 0
    to_roll = ""

    for i in range(len(temp_to_roll)):
        temp_einzel_eingabe = temp_to_roll[i]

        custom_attribute_list = await match_substring(player.attribute_list, temp_einzel_eingabe)
        if len(custom_attribute_list) > 0:

            custom_modifier = str(player.player_attribute_dict.get(temp_player_name)[custom_attribute_list[0]])
            custom_modifier_list = await split_dice_string(custom_modifier)
            # Problem: di[1d20] wird aufgeteilt, dann wird di als attribut gesucht, ist in medicine drin, dadurch fehler. dürfen bei [] nur den bereich im inneren ersetzen
            custom_modifier = ""
            temp_custom_modifier_list = custom_modifier_list

            while " " in custom_modifier_list:
                custom_modifier_list.remove(" ")

            if "[" not in custom_modifier_list:
                for custom in range(len(temp_custom_modifier_list)):
                    nested_modifier = temp_custom_modifier_list[custom]
                    nested_command_list = await match_substring(player.attribute_list, nested_modifier)

                    if len(nested_command_list) > 0:
                        custom_modifier_list[custom + pos1] = await replace_attribute(nested_command_list[0], player_id)

            for custom in range(len(custom_modifier_list)):
                custom_modifier += custom_modifier_list[custom]
            temp_to_roll[i] = custom_modifier

    for i in temp_to_roll:
        to_roll += i

    return (to_roll)


async def split_dice_string(string_w) -> list:
    """
    splittet den string an allen charakteren die nicht Buchstabe oder Zahl sind
    """
    split_string_list = re.split(r'(\W)', string_w)
    while "" in split_string_list:
        split_string_list.remove("")
    return (split_string_list)


# todo Füge überprüfung ob len(matching_list) >1, == 1 oder 0 ein.
# werfe error auf >1, return andernfalls
# todo: füge überprüfung ein, ob saving throw oder nicht, indem to_roll auf sv überprüft wird, maybe return in welcher liste der wert gefunden wurde (normal, save, custom, spell)
async def match_substring(list_to_search, search_string):
    """
    Looks through a list of strings and returns all strings that start with "search_string" as a sub_string
    """
    matching_list = [text for text in list_to_search if text.startswith(search_string)]

    return (matching_list)




async def replace_custom_attribute(to_roll, player_id):
    """
    checkt beim würfeln ob einer der eingabewerte ein custom command ist und ersetze den custom command durch den custom modifier-wert
    """
    temp_to_roll = await split_dice_string(to_roll)
    temp_player_name = player.user_dict[player_id]
    pos1=0
    pos2=0
    to_roll = ""

    for i in range(len(temp_to_roll)):
        temp_einzel_eingabe = temp_to_roll[i]

        custom_attribute_list = await match_substring(player.attribute_list_custom_spells, temp_einzel_eingabe)
        if len(custom_attribute_list) > 0:

            custom_modifier = str(player.player_attribute_dict.get(temp_player_name)[custom_attribute_list[0]])
            custom_modifier_list = await split_dice_string(custom_modifier)
            #Problem: di[1d20] wird aufgeteilt, dann wird di als attribut gesucht, ist in medicine drin, dadurch fehler. dürfen bei [] nur den bereich im inneren ersetzen
            custom_modifier = ""
            temp_custom_modifier_list = custom_modifier_list

            if "[" in custom_modifier_list:
                pos1 = custom_modifier_list.index("[")
                pos2 = custom_modifier_list.index("]")
                temp_custom_modifier_list = custom_modifier_list[pos1:pos2]

            for custom in range(len(temp_custom_modifier_list)):
                nested_modifier = temp_custom_modifier_list[custom]
                nested_command_list = await match_substring(player.attribute_list_custom, nested_modifier)

                if len(nested_command_list) > 0:
                    custom_modifier_list[custom+pos1] = await replace_custom_attribute(nested_command_list[0], player_id)

            for custom in range(len(custom_modifier_list)):
                custom_modifier += custom_modifier_list[custom]
            temp_to_roll[i] = custom_modifier

    for i in temp_to_roll:
        to_roll += i

    return(to_roll)