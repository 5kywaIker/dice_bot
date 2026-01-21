import bot_functions
import re

def new_call_custom_command(ctx, player_id, custom_command):
    custom_command_list = split_dice_string(custom_command)
    counter = 0
    open_index = 0
    tuple_list = []
    single_list = custom_command_list.copy()
    single_string = ""
    for i in range(len(custom_command_list)):
        to_roll = custom_command_list[i]
        if to_roll == "[":
            if counter == 0:
                command = custom_command_list[i-1]
                tuple_list.append(command)
                open_index = i+1
            counter +=1
        elif to_roll == "]":
            counter -= 1
            if counter == 0:
                command = ""
                for j in range(open_index, i):
                    command += custom_command_list[j]
                for to_replace in range(open_index-2, i+1):
                    single_list[to_replace] = ""
                tuple_list.append(command)

    for single in single_list:
        single_string += single
    tuple_list[1] = str(tuple_list[1])+str(single_string)
    return tuple_list

def split_dice_string(string_w):
    split_string_list = re.split(r'(\W)', string_w)
    while "" in split_string_list:
        split_string_list.remove("")
    return (split_string_list)

print("Freedom".split("/"))

"ad[2]+1d6"
['ad', '[', '2', ']', '+', '1d6']


