'''
Compares two lists of short names and determines what is missing

-P.S. 1/9/2019
'''

smartsheet_list = open("ornl_smartsheet.txt")
smartsheet_list = smartsheet_list.read().splitlines()
code_list = open("ORNL_DAAC_shortname.txt")
code_list = code_list.read().splitlines()
# print("Smartsheet Length: ", len(smartsheet_list))
# print("Online Length: ", len(code_list))
# with
# j_list = []
# c_list = []
#
# for line in jeanne_list:
#     j_list.append(line)
# for line in code_list:
#     c_list.append(line)

missing_list = (set(code_list) - set(smartsheet_list))
for entry in missing_list:
    print(entry)
# print('FIFE_WIND_SON_139' in c_list)
# print(len(j_list))
# print(len(c_list))
