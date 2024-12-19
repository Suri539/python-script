encoding = 'utf-8'
from lxml import etree
ditamap_files = ['/Users/fanyuanyuan/Documents/GitHub/python-scripts/Dita-Automation-Scripts/keys-rtc-ng-api-cpp.ditamap', '/Users/fanyuanyuan/Documents/GitHub/python-scripts/Dita-Automation-Scripts/keys-rtc-ng-api-ios.ditamap']

def parse_ditamaps():

    all_navtitles = {}
    for ditamap_file in ditamap_files:
        tree = etree.parse(ditamap_file)
        root = tree.getroot()

        navtitles = set()
        for topichead in root.iter('topichead'):
            navtitle = topichead.get('navtitle')
            if navtitle:
                navtitles.add(navtitle)

        file_name = ditamap_file.split('-')[-1].split('.')[0]
        all_navtitles[file_name] = navtitles

    common_navtitles = set.intersection(*all_navtitles.values())
    return common_navtitles,tree,root

    
def insert_api(id,tree,root,ditamap_files):
    
    api_category = input('请输入 API 类型：\napi/class/enum/callback:')
    href = f'../API/{api_category}_{id}.dita'

    # 创建新的 keydef
    new_keydef = etree.Element('keydef',
                               keys=id,
                               href=href,
                               nsmap=root.nsmap)
    # 添加 topicmeta 和 keyword
    topicmeta = etree.SubElement(new_keydef, 'topicmeta')
    keywords = etree.SubElement(topicmeta, 'keywords')
    keyword = etree.SubElement(keywords, 'keyword')
    keyword.text = id

    # 添加到文档并保存
    root.append(new_keydef)
    tree.write(ditamap_files, encoding='utf-8')
    print("文件已修改并保存")

def main():
    # 获取共同的 navtitles
    common_navtitles, tree, root = parse_ditamaps()
    
    print("\nAPI 分类如下")
    for i, title in enumerate(common_navtitles, 1):
        print(f"{i}. {title}")
    
    selected_category = input('请输入要插入的分类：')

    # 检查输入是否有效
    if selected_category in common_navtitles:
        id = input('请输入 API key: ')

        for ditamap_file in ditamap_files:
            tree = etree.parse(ditamap_file)
            root = tree.getroot()
            insert_api(id,tree,root,ditamap_file)
    else:
        print("未找到该分类")

if __name__ == '__main__':
    main()


# #TODO
# 1. 格式化
# 2. 加在指定位置，先找到 navtitle=input的keydef元素，再插入
# 3. 批量插入
# 4. break
# class Insert:

#     def __init__(self,topic,id,keyword):
#         self.topic = input('Enter the topic you want to insert the API key to:')
#         self.id = input('Enter the API key you want to insert:')
#         self.href = (format('../API/'+'{id}.dita'))
#         self.keyword = str('yy 最棒')
#         self.topic_index, self.common_navtitles, self.tree, self.root = parse_ditamaps()
        
        

#     def insert_api(self):
#         # check if the topic is in the ditamap
#         if self.topic in self.topic_index:
#             # create a new keydef element
#             new_keydef = etree.Element('keydef',keys=self.id,href=self.href,keyword=self.keyword)

#             topicmeta = etree.SubElement(new_keydef,'topicmeta')
#             keywords = etree.SubElement(topicmeta,'keywords')
#             keyword = etree.SubElement(keywords,'keyword')
#             keyword.text = self.keyword
#             # add the new keydef
#             self.root.append(new_keydef)
#             # save the modified ditamap
#             self.tree.write(self.ditamap_file,encoding=encoding)
#             print(f"The file has been modified and saved")


# func = Insert('topic','id','keyword')
# func.insert_api()