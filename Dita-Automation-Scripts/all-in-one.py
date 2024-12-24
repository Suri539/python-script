encoding = 'utf-8'
from lxml import etree
import json
import os
import shutil

PLATFORM_FILES = {
    "android": "RTC_NG_API_Android.ditamap",
    "ios": "RTC_NG_API_iOS.ditamap",
    "windows": "RTC_NG_API_CPP.ditamap",
    "macos": "RTC_NG_API_macOS.ditamap",
    "flutter": "RTC_NG_API_Flutter.ditamap",
    "unity": "RTC_NG_API_Unity.ditamap",
    "electron": "RTC_NG_API_Electron.ditamap",
    "rn": "RTC_NG_API_RN.ditamap",
    "unreal": "RTC_NG_API_Unreal.ditamap",
    "cs": "RTC_NG_API_CS.ditamap"
}

PLATFORM_TO_KEYSMAP = {
    "android": "java",
    "windows": "cpp",
    "ios": "ios",
    "macos": "macos",
    "unity": "unity",
    "unreal": "unreal",
    "cs": "cs",
    "electron": "electron",
    "flutter": "flutter",
    "rn": "rn"
}

# 获取基础目录路径
base_dir = '/Users/admin/Documents/python-script/Dita-Automation-Scripts/dita'

# 读取 JSON 数据
with open('data.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# def create_dita_files():
#     """创建 DITA 文件"""
#     import shutil

#     # 定义模板和目标目录路径
#     template_dir = os.path.join(base_dir, 'templates-cn', 'RTC')
#     target_dir = os.path.join(base_dir, 'RTC-NG', 'API')

#     # 确保目标目录存在
#     os.makedirs(target_dir, exist_ok=True)

#     # 遍历 data.json 文件中的每个 API
#     for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
#         for api_data in json_data.get(change_type, []):
#             attributes = api_data.get('attributes', '')
#             key = api_data['key'].lower()

#             # 根据不同的 attributes 选择不同的模板和生成不同的文件名
#             if isinstance(attributes, dict) and attributes.get('type') == 'enum':
#                 # 处理 enum 类型
#                 template_file = os.path.join(template_dir, 'Enum.dita')
#                 output_filename = f'enum_{key.replace("_", "")}.dita'  # 去掉下划线
#             else:
#                 # 处理其他类型
#                 if attributes == 'api':
#                     template_file = os.path.join(template_dir, 'Method.dita')
#                     output_filename = f'api_{key}.dita'
#                 elif attributes == 'enum':
#                     template_file = os.path.join(template_dir, 'Enum.dita')
#                     output_filename = f'enum_{key.replace("_", "")}.dita'  # 去掉下划线
#                 elif attributes == 'class':
#                     template_file = os.path.join(template_dir, 'Class.dita')
#                     output_filename = f'class_{key}.dita'
#                 elif attributes == 'callback':
#                     template_file = os.path.join(template_dir, 'Callback.dita')
#                     output_filename = f'callback_{key}.dita'
#                 else:
#                     print(f"Warning: Unknown attributes type '{attributes}' for API {api_data['key']}")
#                     continue

#             # 构建目标文件路径
#             output_path = os.path.join(target_dir, output_filename)

#             # 如果目标文件已存在，跳过
#             if os.path.exists(output_path):
#                 print(f"Skipping existing file: {output_filename}")
#                 continue

#             try:
#                 # 复制模板文件到目标位置
#                 shutil.copy2(template_file, output_path)
#                 print(f"Created {output_filename}")
#             except FileNotFoundError:
#                 print(f"Error: Template file not found: {template_file}")
#             except Exception as e:
#                 print(f"Error creating {output_filename}: {str(e)}")

# create_dita_files()

# 遍历 data.json 中的数据
# 找到 parameters 下 change_type 为 'modify' 且 attibutes 为 api
# 根据现有的规则来找到对应的 api 文件并进行解析
# 把 <section id="parameters"> 里的内容进行替换，把其中<plentry>里<pt>的值替换为对应api json里面的 new_value
#把 <section id="parameters"> <plentry>里<pd>的值替换为对应api json里的desc

def modify_dita_files():
    """Modify DITA files based on JSON data."""
    api_dir = os.path.join(base_dir, 'RTC-NG', 'API')

    for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
        for api_data in json_data.get(change_type, []):
            if api_data.get('change_type') != 'modify':
                continue

            attributes = api_data.get('attributes', '')
            parentclass = api_data.get('parentclass', '').lower()
            key = api_data['key'].lower()
            dita_file_path = None

            # Construct the file name based on attributes and parentclass
            if attributes in ['api', 'callback']:
                file_name_pattern = f"{attributes}_{parentclass}_{key}.dita"
            else:
                file_name_pattern = key  # Default pattern if not api or callback

            # Search for the file that matches the constructed pattern
            for file_name in os.listdir(api_dir):
                if file_name.endswith('.dita') and file_name_pattern in file_name:
                    dita_file_path = os.path.join(api_dir, file_name)
                    break

            if not dita_file_path:
                print(f"Error: DITA file not found for key {key}")
                continue

            try:
                tree = etree.parse(dita_file_path)
                root = tree.getroot()

                # Replace <ph id="shortdesc">
                shortdesc = api_data['description'].get('shortdesc', '')
                ph_element = root.find(".//ph[@id='shortdesc']")
                if ph_element is not None:
                    ph_element.clear()
                    ph_element.text = shortdesc

                # Replace <section id="detailed_desc">
                detailed_desc = api_data['description'].get('detailed_desc', [])
                detailed_desc_text = ''.join([desc['desc'] for desc in detailed_desc])
                detailed_desc_element = root.find(".//section[@id='detailed_desc']/p")
                if detailed_desc_element is not None:
                    detailed_desc_element.clear()
                    detailed_desc_element.text = detailed_desc_text

                # Replace <section id="scenario">
                scenario = api_data['description'].get('scenarios', '')
                scenario_element = root.find(".//section[@id='scenario']/p")
                if scenario_element is not None:
                    scenario_element.clear()
                    scenario_element.text = scenario

                # Replace <section id="timing">
                timing = api_data['description'].get('timing', '')
                timing_element = root.find(".//section[@id='timing']/p")
                if timing_element is not None:
                    timing_element.clear()
                    timing_element.text = timing

                # Replace <section id="restriction">
                restrictions = api_data['description'].get('restrictions', '')
                restriction_element = root.find(".//section[@id='restriction']/p")
                if restriction_element is not None:
                    restriction_element.clear()
                    restriction_element.text = restrictions

                # Save changes back to the file
                tree.write(dita_file_path, encoding='UTF-8', xml_declaration=True)
                print(f"Modified DITA file: {dita_file_path}")

            except Exception as e:
                print(f"Error modifying DITA file {dita_file_path}: {str(e)}")

modify_dita_files()


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
#         # 跳过 attributes 为 class 且 navtitle 不为 "Interface classes" 的 API
#         # 跳过 attributes 为 enum 的 API
#         if (api_data.get('attributes') == 'class' and api_data.get('navtitle') != 'Interface classes') or \
#            api_data.get('attributes') == 'enum':
#             print(f"Skipping API with key '{api_data['key']}' due to attributes '{api_data['attributes']}' and navtitle '{api_data.get('navtitle', '')}'")
#             continue

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
#     ditamap_base_dir = os.path.join(base_dir, 'RTC-NG')

#     # 首先按平台组织 API 数据
#     platform_api_map = {platform: [] for platform in PLATFORM_FILES.keys()}

#     # 遍历所有 API 数据，按平台分组
#     for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
#         for api_data in json_data.get(change_type, []):
#             platforms = api_data.get('platforms', [])

#             # 如果platforms是"all"，则添加到所有平台
#             if "all" in platforms:
#                 for platform in PLATFORM_FILES.keys():
#                     platform_api_map[platform].append(api_data)
#             else:
#                 # 否则只添加到指定的平台
#                 for platform in platforms:
#                     if platform in platform_api_map:
#                         platform_api_map[platform].append(api_data)

#     # 处理每个平台的 ditamap 文件
#     for platform, apis in platform_api_map.items():
#         if platform in PLATFORM_FILES:
#             ditamap_path = os.path.join(ditamap_base_dir, PLATFORM_FILES[platform])
#             if os.path.exists(ditamap_path):
#                 parse_ditamap(ditamap_path, apis)
#             else:
#                 print(f"Warning: Ditamap file not found for platform {platform}: {ditamap_path}")
#         else:
#             print(f"Warning: No ditamap file mapping for platform {platform}")

# def create_and_insert_keydef(root, api_data, platform):
#     """创建并插入新的 keydef 元素"""
#     # 获取第一个 topichead 下的第一个 keydef 作为参考
#     reference_keydef = root.find('.//topichead/keydef')
#     if reference_keydef is None:
#         print("Warning: No reference keydef found for indentation")
#         return False

#     # 获取基础缩进（keydef 元素的缩进）
#     base_indent = (reference_keydef.tail or '').rpartition('\n')[2]

#     # 检查是否为 enum 类型
#     if api_data.get('attributes') == 'enum' and 'enumerations' in api_data['description']:
#         # 插入 enum keydef
#         target_navtitle = api_data.get('navtitle')
#         if not target_navtitle:
#             print(f"Warning: No navtitle specified for API {api_data['key']}")
#             return False

#         # 为枚举创建 keydef
#         enum_keydef = etree.Element('keydef')
#         enum_keydef.set('keys', api_data['keyword'].get(platform, api_data['key']))
#         # 移除 href 里面的下划线
#         enum_keydef.set('href', f"../API/enum_{api_data['key'].lower().replace('_', '')}.dita")
#         enum_keydef.text = '\n' + base_indent + '    '
#         enum_keydef.tail = '\n' + base_indent

#         topicmeta = etree.SubElement(enum_keydef, 'topicmeta')
#         topicmeta.text = '\n' + base_indent + '        '
#         topicmeta.tail = '\n' + base_indent + '    '

#         keywords = etree.SubElement(topicmeta, 'keywords')
#         keywords.text = '\n' + base_indent + '            '
#         keywords.tail = '\n' + base_indent + '        '

#         keyword = etree.SubElement(keywords, 'keyword')
#         keyword.text = api_data['keyword'].get(platform, api_data['key'])
#         keyword.tail = '\n' + base_indent + '        '

#         #  插入枚举 keydef
#         for topichead in root.iter('topichead'):
#             if topichead.get('navtitle') == target_navtitle:
#                 topichead.append(enum_keydef)

#                 # 添加枚举值 keydef
#                 for enum_platform, enums in api_data['description']['enumerations'].items():
#                     if platform == enum_platform:
#                         for enum in enums:
#                             alias = enum.get('alias')
#                             value = enum.get('value')
#                             if alias and value:
#                                 # 为每个枚举创建 keydef
#                                 enum_value_keydef = etree.Element('keydef')
#                                 enum_value_keydef.set('keys', alias)  # 设置 keys 为 alias
#                                 enum_value_keydef.text = '\n' + base_indent + '    '
#                                 enum_value_keydef.tail = '\n' + base_indent

#                                 topicmeta = etree.SubElement(enum_value_keydef, 'topicmeta')
#                                 topicmeta.text = '\n' + base_indent + '        '
#                                 topicmeta.tail = '\n' + base_indent + '    '

#                                 keywords = etree.SubElement(topicmeta, 'keywords')
#                                 keywords.text = '\n' + base_indent + '            '
#                                 keywords.tail = '\n' + base_indent + '        '

#                                 keyword = etree.SubElement(keywords, 'keyword')
#                                 keyword.text = value  # Set keyword to value
#                                 keyword.tail = '\n' + base_indent + '        '

#                                 # 插入枚举值 keydef
#                                 topichead.append(enum_value_keydef)

#                 return True

#         print(f"Warning: No matching topichead found for navtitle '{target_navtitle}'")
#         return False

#     # 处理非 enum 类型的 keydef
#     new_keydef = etree.Element('keydef')
#     new_keydef.set('keys', api_data['key'])

#     # 获取attributes和parentclass
#     attributes = api_data.get('attributes', '')
#     parentclass = api_data.get('parentclass', '').lower()

#     # 根据不同条件构建href
#     if attributes == 'enum':
#         # enum类型的特殊处理，移除keyname中的下划线
#         keyname = api_data['key'].lower().replace('_', '')
#         new_keydef.set('href', f"../API/{attributes}_{keyname}.dita")
#     elif parentclass == 'none':
#         # parentclass为none的处理
#         new_keydef.set('href', f"../API/{attributes}_{api_data['key'].lower()}.dita")
#     else:
#         # 默认处理
#         new_keydef.set('href', f"../API/{attributes}_{parentclass}_{api_data['key'].lower()}.dita")

#     new_keydef.text = '\n' + base_indent + '    '  # 为第一个子元素添加缩进
#     new_keydef.tail = '\n' + base_indent

#     if 'keyword' in api_data:
#         # 创建 topicmeta
#         topicmeta = etree.SubElement(new_keydef, 'topicmeta')
#         topicmeta.text = '\n' + base_indent + '        '  # 为 keywords 添加缩进
#         topicmeta.tail = '\n' + base_indent + '    '

#         # 创建 keywords
#         keywords = etree.SubElement(topicmeta, 'keywords')
#         keywords.text = '\n' + base_indent + '            '  # 为 keyword 添加缩进
#         keywords.tail = '\n' + base_indent + '        '

#         # 获取当前平台的关键字
#         keyword_value = api_data['keyword'] if isinstance(api_data['keyword'], str) else api_data['keyword'].get(platform, api_data['key'])
#         keyword = etree.SubElement(keywords, 'keyword')
#         keyword.text = keyword_value
#         keyword.tail = '\n' + base_indent + '        '

#     # 查找目标 topichead 并插入
#     target_navtitle = api_data.get('navtitle')
#     if not target_navtitle:
#         print(f"Warning: No navtitle specified for API {api_data['key']}")
#         return False

#     for topichead in root.iter('topichead'):
#         if topichead.get('navtitle') == target_navtitle:
#             # 检查是否已存在相同的 keydef
#             for existing_keydef in topichead.findall('keydef'):
#                 if existing_keydef.get('keys') == api_data['key']:
#                     print(f"Warning: Keydef with key '{api_data['key']}' already exists in {target_navtitle}")
#                     return False
#             # 添加元素
#             topichead.append(new_keydef)
#             return True

#     print(f"Warning: No matching topichead found for navtitle '{target_navtitle}'")
#     return False

# def parse_keysmaps():
#     """处理所有平台的 keysmaps 文件"""
#     # 创建平台到API的映射
#     platform_apis = {
#         'android': [],
#         'ios': [],
#         'windows': [],
#         'macos': [],
#         'unreal': [],
#         'cs': [],
#         'electron': [],
#         'flutter': [],
#         'rn': [],
#         'unity': []
#     }
#     # 将 API 按平台分类
#     for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
#         for api_data in json_data.get(change_type, []):
#             platforms = api_data.get('platforms', [])
#             # 如果platforms是"all"，添加到所有平台
#             if "all" in platforms:
#                 for platform in platform_apis.keys():
#                     platform_apis[platform].append(api_data)
#             else:
#                 # 否则只添加到指定的平台
#                 for platform in platforms:
#                     if platform in platform_apis:
#                         platform_apis[platform].append(api_data)

#     # 解析 RTC-NG/config 路径下所有的 keys-rtc-ng-api-{platform}.ditamap 文件
#     keysmaps_dir = os.path.join(base_dir, 'RTC-NG','config')

#     # 遍历每个平台
#     for json_platform, keysmap_platform in PLATFORM_TO_KEYSMAP.items():
#         keysmap_file = os.path.join(keysmaps_dir, f'keys-rtc-ng-api-{keysmap_platform}.ditamap')
#         if not os.path.exists(keysmap_file):
#             print(f"Warning: Keymap file not found: {keysmap_file}")
#             continue

#         print(f"\nProcessing keymap for platform: {json_platform}")

#         # 检查该平台是否有需要处理的API
#         if not platform_apis[json_platform]:
#             print(f"No APIs to process for platform {json_platform}")
#             continue

#         tree = etree.parse(keysmap_file)
#         root = tree.getroot()
#         changes_made = 0

#         # 处理该平台的所有API
#         for api_data in platform_apis[json_platform]:
#             if create_and_insert_keydef(root, api_data, json_platform):
#                 changes_made += 1
#                 print(f"Added keydef for API {api_data['key']} to {json_platform}")

#         # 如果有修改，保存文件
#         if changes_made > 0:
#             print(f"Writing {changes_made} changes to {keysmap_file}")
#             tree.write(keysmap_file, encoding='UTF-8', xml_declaration=True)
#         else:
#             print(f"No changes made to {keysmap_file}")
# parse_keysmaps()

# def insert_relations(relations_path):
#     """处理 relations 文件，插入 API 关系"""
#     print(f"\nProcessing relations file: {relations_path}")

#     # 解析 relations 文件
#     tree = etree.parse(relations_path)
#     root = tree.getroot()
#     changes_made = 0

#     # 创建平台映射字典
#     platform_map = {config['platform']: config['platform1'] for config in platform_configs}

#     # 遍历所有 API 数据
#     for api_key, api_data in json_data.items():
#         # 检查是否需要处理该 API
#         if api_data.get('attributes') not in ['api', 'callback']:
#             continue

#         # 获取必要的数据
#         key = api_data['key']
#         parentclass = api_data.get('parentclass')
#         platforms = api_data.get('platforms', [])

#         # 转换平台名称
#         props = []
#         for platform in platforms:
#             if platform in platform_map:
#                 props.append(platform_map[platform])

#         if not props or not parentclass:
#             continue

#         # 构建 props 属性字符串
#         props_str = ' '.join(props)

#         # 在 reltable 中查找对应的 parentclass
#         for relrow in root.findall('.//relrow'):
#             found = False
#             has_props = False  # 初始化 props 检查标志
#             target_cell = None

#             # 查找包含目标 parentclass 的 relcell
#             for relcell in relrow.findall('relcell'):
#                 for topicref in relcell.findall('topicref'):
#                     if topicref.get('keyref') == parentclass:
#                         # 检查是否有任何 props 属性
#                         for ancestor in topicref.iterancestors():
#                             if ancestor.get('props') is not None:
#                                 has_props = True
#                                 print(f"Skipping API {key} as its parent has props attribute")
#                                 break

#                         if has_props:
#                             break

#                         # 找到目标 relcell，获取另一个 relcell
#                         target_cell = relrow.findall('relcell')[0]
#                         found = True
#                         break
#                 if found or has_props:
#                     break

#             if found and target_cell is not None and not has_props:
#                 # 检查是否已存在相同的 keyref
#                 exists = False
#                 for existing_topicref in target_cell.findall('topicref'):
#                     if existing_topicref.get('keyref') == key:
#                         exists = True
#                         break

#                 if not exists:
#                     # 创建新的 topicref 元素
#                     new_topicref = etree.Element('topicref')
#                     new_topicref.set('keyref', key)
#                     new_topicref.set('props', props_str)

#                     # 获取当前缩进级别
#                     current_indent = ''
#                     parent = target_cell
#                     while parent is not None:
#                         current_indent += '    '
#                         parent = parent.getparent()

#                     # 设置新元素的缩进
#                     new_topicref.tail = '\n' + current_indent

#                     # 添加到目标 relcell 并按字母顺序排序
#                     target_cell.append(new_topicref)
#                     changes_made += 1
#                     print(f"Added relation for API {key} under {parentclass}")

#                     # 获取所有 topicref 元素并排序
#                     topicrefs = target_cell.findall('topicref')
#                     sorted_topicrefs = sorted(topicrefs, key=lambda x: x.get('keyref', ''))

#                     # 清空 relcell
#                     for child in list(target_cell):
#                         target_cell.remove(child)

#                     # 重新按顺序添加元素
#                     for i, topicref in enumerate(sorted_topicrefs):
#                         # 设置适当的缩进
#                         if i < len(sorted_topicrefs) - 1:
#                             topicref.tail = '\n' + current_indent
#                         else:
#                             # 最后一个元素的缩进需要特殊处理
#                             topicref.tail = '\n' + current_indent[:-4]
#                         target_cell.append(topicref)

#     # 如果有修改，保存文件
#     if changes_made > 0:
#         print(f"Writing {changes_made} changes to {relations_path}")
#         tree.write(relations_path, encoding='UTF-8', xml_declaration=True)
#     else:
#         print(f"No changes made to {relations_path}")

# def insert_datatype(datatype_path):
#     """处理 datatype 文件，插入类和枚举的引用"""
#     print(f"\n处理 datatype 文件: {datatype_path}")

#     # 解析 datatype 文件
#     tree = etree.parse(datatype_path)
#     root = tree.getroot()
#     changes_made = 0

#     # 创建平台映射字典
#     platform_map = {config['platform']: config['platform3'] for config in platform_configs}

#     # 遍历所有 API 数据
#     for api_key, api_data in json_data.items():
#         # 只处理 class 和 enum 类型
#         attributes = api_data.get('attributes')
#         if attributes not in ['class', 'enum']:
#             continue

#         # 获取平台信息并转换
#         platforms = api_data.get('platforms', [])
#         props = []
#         for platform in platforms:
#             if platform in platform_map:
#                 props.append(platform_map[platform])

#         if not props:
#             continue

#         # 查找对应的 section
#         section = root.find(f".//section[@id='{attributes}']")
#         if section is None:
#             print(f"警告: 未找到 section id='{attributes}'")
#             continue

#         changes_in_api = 0

#         # 为每个平台创建或更新 ul 元素
#         for prop in props:
#             # 查找或创建对应平台的 ul
#             ul = section.find(f"ul[@props='{prop}']")
#             if ul is None:
#                 ul = etree.SubElement(section, 'ul')
#                 ul.set('props', prop)
#                 # 设置适当的缩进
#                 ul.tail = '\n            '

#             # 检查是否已存在相同的 xref
#             exists = False
#             for li in ul.findall('li'):
#                 xref = li.find('xref')
#                 if xref is not None and xref.get('keyref') == api_data['key']:
#                     exists = True
#                     break

#             if not exists:
#                 # 创建新的 li 和 xref 元素
#                 new_li = etree.SubElement(ul, 'li')
#                 new_xref = etree.SubElement(new_li, 'xref')
#                 new_xref.set('keyref', api_data['key'])

#                 # 设置缩进
#                 new_li.tail = '\n            '

#                 changes_in_api += 1
#                 print(f"添加了 {api_data['key']} 到 {prop} 平台的 {attributes} 部分")

#                 # 对 li 元素进行排序
#                 lis = ul.findall('li')
#                 sorted_lis = sorted(lis, key=lambda x: x.find('xref').get('keyref', ''))

#                 # 清空 ul
#                 for child in list(ul):
#                     ul.remove(child)

#                 # 重新按顺序添加元素
#                 for i, li in enumerate(sorted_lis):
#                     if i < len(sorted_lis) - 1:
#                         li.tail = '\n            '
#                     else:
#                         li.tail = '\n        '
#                     ul.append(li)

#         changes_made += changes_in_api

#     # 如果有修改，保存文件
#     if changes_made > 0:
#         print(f"总共向 {datatype_path} 添加了 {changes_made} 处修改")
#         tree.write(datatype_path, encoding='UTF-8', xml_declaration=True)
#     else:
#         print(f"未对 {datatype_path} 进行任何修改")

# def main(platform_configs):
#     create_dita_files()
#     process_all_ditamaps()
#     parse_keysmaps()
#     insert_relations(relations_path)
#     insert_datatype(datatype_path)

# # 添加到主程序中的调用
# if __name__ == "__main__":
#     relations_path = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/RTC-NG/config/relations-rtc-ng-api.ditamap'
#     datatype_path = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/RTC-NG/API/rtc_api_data_type.dita'
#     platform_configs = [
#         {'platform': 'android', 'platform1': 'java', 'platform2': 'Android', 'platform3': 'android'},
#         {'platform': 'ios', 'platform1': 'ios', 'platform2': 'iOS', 'platform3': 'ios'},
#         {'platform': 'macos', 'platform1': 'macos', 'platform2': 'macOS', 'platform3': 'mac'},
#         {'platform': 'windows', 'platform1': 'cpp', 'platform2': 'CPP', 'platform3': 'cpp'},
#         {'platform': 'flutter', 'platform1': 'flutter', 'platform2': 'Flutter', 'platform3': 'flutter'},
#         {'platform': 'unity', 'platform1': 'unity', 'platform2': 'Unity', 'platform3': 'unity'},
#         {'platform': 'electron', 'platform1': 'electron', 'platform2': 'Electron', 'platform3': 'electron'},
#         {'platform': 'rn', 'platform1': 'rn', 'platform2': 'RN', 'platform3': 'rn'},
#     ]
#     main(platform_configs)