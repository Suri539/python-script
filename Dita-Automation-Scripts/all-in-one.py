encoding = 'utf-8'
from lxml import etree
import json
import os

PLATFORM_FILES = {
    "android": "RTC_NG_API_Android.ditamap",
    "ios": "RTC_NG_API_iOS.ditamap",
    "windows": "RTC_NG_API_CPP.ditamap",
    "macos": "RTC_NG_API_macOS.ditamap"
}

PLATFORM_TO_KEYSMAP = {
    "android": "java",
    "windows": "cpp",
    "ios": "ios",
    "macos": "macos"
}

# 获取基础目录路径
base_dir = '/Users/admin/Documents/python-scripts/Dita-Automation-Scripts/RTC-NG'

# 读取 JSON 数据
with open('data.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# def parse_ditamap(ditamap_path, platform_apis):
#     """处理单个 ditamap 文件"""
#     print(f"\nProcessing ditamap: {ditamap_path}")
#     print(f"Total APIs to process: {len(platform_apis)}")

#     tree = etree.parse(ditamap_path)
#     root = tree.getroot()
#     changes_made = 0

#     # 记录需要重新排序的 topicref父元素
#     modified_parents = set()

#     # 遍历该平台需要处理的 API 数据
#     for api_data in platform_apis:
#         target_href = api_data['toc_href']
#         api_key = api_data['key']

#         # 查找目标位置并添加新的 topicref
#         for topicref in root.iter('topicref'):
#             if topicref.get('href') == target_href:
#                 # 获取当前 topicref 的缩进级别
#                 current_indent = ''
#                 parent = topicref
#                 while parent is not None:
#                     current_indent += '    '
#                     parent = parent.getparent()

#                 # 先添加一个换行和缩进
#                 topicref.tail = '\n' + current_indent

#                 new_topicref = etree.Element('topicref')
#                 new_topicref.set('keyref', api_key)
#                 new_topicref.set('toc', 'no')
#                 # 设置新元素的缩进
#                 new_topicref.tail = '\n' + current_indent

#                 topicref.append(new_topicref)
#                 changes_made += 1
#                 print(f"Added new topicref with keyref='{api_key}' under {target_href}")

#                 # 将修改过的父元素添加到集合中
#                 modified_parents.add(topicref)

#     # 对所有修改过的父元素进行子元素排序
#     for parent in modified_parents:
#         # 获取所有子元素
#         children = list(parent)
#         if children:
#             # 按字母顺序排序
#             children.sort(key=lambda x: x.get('keyref', '').lower())

#             # 重新设置子元素的顺序
#             for i, child in enumerate(children):
#                 # 如果不是最后一个元素，设置换行和缩进
#                 if i < len(children) - 1:
#                     child.tail = '\n' + current_indent
#                 # 如果是最后一个元素，设置换行和父级缩进
#                 else:
#                     child.tail = '\n' + current_indent[:-4]
#                 # 把元素加到正确的位置
#                 parent.append(child)

#     # 如果有修改，写入文件
#     if changes_made > 0:
#         print(f"\nWriting {changes_made} changes to {ditamap_path}")
#         tree.write(ditamap_path, encoding='UTF-8', xml_declaration=True)
#     else:
#         print(f"\nNo changes made to {ditamap_path}")

# def process_all_ditamaps():
#     """处理所有平台的 ditamap 文件"""
#     # 首先按平台组织 API 数据
#     platform_api_map = {}

#     # 遍历所有 API 数据，按平台分组
#     for api_data in json_data.values():
#         for platform in api_data['platforms']:
#             if platform not in platform_api_map:
#                 platform_api_map[platform] = []
#             platform_api_map[platform].append(api_data)

#     # 处理每个平台的 ditamap 文件
#     for platform, apis in platform_api_map.items():
#         if platform in PLATFORM_FILES:
#             ditamap_path = os.path.join(base_dir, PLATFORM_FILES[platform])
#             if os.path.exists(ditamap_path):
#                 parse_ditamap(ditamap_path, apis)
#             else:
#                 print(f"Warning: Ditamap file not found for platform {platform}: {ditamap_path}")
#         else:
#             print(f"Warning: No ditamap file mapping for platform {platform}")

# # 添加所有的 ditamap
# process_all_ditamaps()

def create_and_insert_keydef(root, api_data):
    """创建并插入新的 keydef 元素"""
    # 创建新的 keydef 元素
    new_keydef = etree.Element('keydef')
    new_keydef.set('keys', api_data['key'])

    # 构建 href 属性
    href = f"../API/{api_data.get('attributes', '')}_{api_data.get('parentclass', '')}_{api_data['key'].lower()}.dita"
    new_keydef.set('href', href)

    # 如果有 keyword，添加 topicmeta 和 keywords
    if 'keyword' in api_data:
        topicmeta = etree.SubElement(new_keydef, 'topicmeta')
        keywords = etree.SubElement(topicmeta, 'keywords')
        keyword = etree.SubElement(keywords, 'keyword')
        keyword.text = api_data['keyword']

    # 查找目标 topichead
    target_navtitle = api_data.get('navtitle')
    if not target_navtitle:
        print(f"Warning: No navtitle specified for API {api_data['key']}")
        return False

    # 查找对应的 topichead
    for topichead in root.iter('topichead'):
        if topichead.get('navtitle') == target_navtitle:
            # 获取当前缩进级别
            current_indent = ''
            parent = topichead
            while parent is not None:
                current_indent += '    '
                parent = parent.getparent()

            # 设置新元素的缩进
            new_keydef.tail = '\n' + current_indent

            # 检查是否已存在相同的 keydef
            for existing_keydef in topichead.findall('keydef'):
                if existing_keydef.get('keys') == api_data['key']:
                    print(f"Warning: Keydef with key '{api_data['key']}' already exists in {target_navtitle}")
                    return False

            # 添加到 topichead 中
            topichead.append(new_keydef)
            return True

    print(f"Warning: No matching topichead found for navtitle '{target_navtitle}'")
    return False

def parse_keysmaps():
    """处理所有平台的 keysmaps 文件"""
    # 创建平台到API的映射
    platform_apis = {
        'android': [],
        'ios': [],
        'windows': [],
        'macos': []
    }

    # 将API按平台分类
    for api_key, api_data in json_data.items():
        for platform in api_data.get('platforms', []):
            if platform in platform_apis:
                platform_apis[platform].append(api_data)

    # 解析 RTC-NG/config 路径下所有的 keys-rtc-ng-api-{platform}.ditamap 文件
    keysmaps_dir = os.path.join(base_dir, 'config')


    # 遍历每个平台
    for json_platform, keysmap_platform in PLATFORM_TO_KEYSMAP.items():
        keysmap_file = os.path.join(keysmaps_dir, f'keys-rtc-ng-api-{keysmap_platform}.ditamap')
        if not os.path.exists(keysmap_file):
            print(f"Warning: Keymap file not found: {keysmap_file}")
            continue

        print(f"\nProcessing keymap for platform: {json_platform}")

        # 检查该平台是否有需要处理的API
        if not platform_apis[json_platform]:
            print(f"No APIs to process for platform {json_platform}")
            continue

        tree = etree.parse(keysmap_file)
        root = tree.getroot()
        changes_made = 0

        # 处理该平台的所有API
        for api_data in platform_apis[json_platform]:
            if create_and_insert_keydef(root, api_data):
                changes_made += 1
                print(f"Added keydef for API {api_data['key']} to {json_platform}")

        # 如果有修改，保存文件
        if changes_made > 0:
            print(f"Writing {changes_made} changes to {keysmap_file}")
            tree.write(keysmap_file, encoding='UTF-8', xml_declaration=True)
        else:
            print(f"No changes made to {keysmap_file}")

# 添加到主程序中的调用
if __name__ == "__main__":
    parse_keysmaps()