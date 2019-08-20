'''
Compares two lists of short names and determines what is missing

-P.S. 1/9/2019
'''

jeanne_list = open("jeanne_list.txt")
jeanne_list = jeanne_list.read().splitlines()
code_list = open("scraper_output.txt")
code_list = code_list.read().splitlines()
# with
# j_list = []
# c_list = []
#
# for line in jeanne_list:
#     j_list.append(line)
# for line in code_list:
#     c_list.append(line)

print(set(jeanne_list) - set(code_list))
# print('FIFE_WIND_SON_139' in c_list)
# print(len(j_list))
# print(len(c_list))
