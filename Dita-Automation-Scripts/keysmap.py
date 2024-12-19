encoding = 'utf-8'
import xml.etree.ElementTree as ET

ditmap_files = ['keys-rtc-ng-api-cpp.ditamap', 'keys-rtc-ng-api-cpp.dita']

all_navtitles = {}

for ditmap_file in ditmap_files:
    tree = ET.parse(ditmap_file)
    root = tree.getroot()

# get all navtitles
    navtitles = set()
    for topichead in root.iter('topichead'):
        navtitle = topichead.get('navtitle')
        if navtitle:
           navtitles.add(navtitle)

    file_name = ditmap_file.split('.')[-1]
    all_navtitles[file_name] = navtitles

common_navtitles = set.intersection(*all_navtitles.values())
print("所有文件共有的 navtitles：")
for index, title in enumerate(common_navtitles, 1):
    print(f"{index} - {title}")

# print all navtitles
for file_name, titles in all_navtitles.items():
    print(f'{file_name}:')
    for index, title in enumerate(titles, 1):
        print(f'{index} : {title}')

# get user input of title
title_input = int(input('Enter the title number:'))

if 1 <= title_input <= len(navtitles):
    print(f"{title_input} - {navtitles[title_input - 1]}")
else:
    print("输入的索引无效")

