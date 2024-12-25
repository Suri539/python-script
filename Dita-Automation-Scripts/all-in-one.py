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
# 找到 parameters 下 change_type 为 'modify' 且 attibutes 为 api 或 callback 的 API
# 根据第二步中找到的 API 的 key，按照这个规则来找到 dita/RTC-NG/API 目录下的对应的 dita 文件：{attributes}_{parentclass}_{key}.dita，均为小写
# 找到对应的 dita 文件后，找到 <section id="parameters">，在这个 section 下新增一个 plentry 元素，其中 <pt>标签里面的内容为 对应 API 的 json parameters 字段里面的 "name" 字段的值，<pd>标签里面的内容为对应 API 的 json parameters 字段里面的 "desc" 字段的值。
# 如果一个 API 的 json parameter 下有多个 platform 的值，如果 name 字段的值一致，则 <pt> 标签上增加一个 props 属性，值为 platform 的值（windows 对应的值为 cpp），如果 name 字段的值不一致，则 <pt> 标签上增加一个 props 属性，值为 platform 的值（windows 对应的值为 cpp）。
# 保存修改后的文件

def modify_dita_files():
    """根据 JSON 数据修改 DITA 文件，同时保持原有格式和缩进一致。"""
    api_dir = os.path.join(base_dir, 'RTC-NG', 'API')

    # 遍历 data.json 中的数据
    for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
        for item in json_data.get(change_type, []):
            # 只处理 modify 类型且 attributes 为 api、callback、enum 或 class 的 API
            if item['change_type'] == 'modify' and item['attributes'] in ['api', 'callback', 'enum', 'class']:
                # 根据 attributes 类型构建 DITA 文件路径
                if item['attributes'] in ['api', 'callback']:
                    filename = f"{item['attributes']}_{item['parentclass']}_{item['key']}.dita".lower()
                elif item['attributes'] in ['enum', 'class']:
                    filename = f"{item['attributes']}_{item['key'].replace('_', '')}.dita".lower()
                else:
                    print(f"Unsupported attribute type: {item['attributes']}")
                    continue

                dita_path = os.path.join(api_dir, filename)

                if not os.path.exists(dita_path):
                    print(f"文件未找到: {dita_path}")
                    continue

                # 解析 DITA 文件
                parser = etree.XMLParser(remove_blank_text=False)
                tree = etree.parse(dita_path, parser)
                root = tree.getroot()

                # 找到 parameters section
                params_section = root.find(".//section[@id='parameters']")
                if params_section is None:
                    print(f"在 {dita_path} 中未找到 parameters section")
                    continue

                # 找到 <parml> 元素
                parml = params_section.find("parml")

                if parml is not None:
                    # 获取 <parml> 内现有 plentry 的缩进
                    existing_plentries = parml.findall('plentry')
                    if existing_plentries:
                        last_plentry = existing_plentries[-1]
                        # 获取最后一个 plentry 的 tail (换行 + 缩进)
                        indent = last_plentry.tail if last_plentry.tail else '\n        '
                        # 获取子元素的缩进（假设子元素比 plentry 多 4 个空格）
                        child_indent = ' ' * (len(indent) + 4)
                    else:
                        # 默认缩进
                        indent = '\n        '
                        child_indent = indent + '    '

                    target_parent = parml
                else:
                    # 如果没有 <parml>，则直接在 section 下添加 plentry
                    existing_plentries = params_section.findall('plentry')
                    if existing_plentries:
                        last_plentry = existing_plentries[-1]
                        indent = last_plentry.tail if last_plentry.tail else '\n        '
                        child_indent = ' ' * (len(indent) + 4)
                    else:
                        # 默认缩进
                        indent = '\n        '
                        child_indent = indent + '    '

                    target_parent = params_section

                # 处理参数
                if 'parameters' in item['description']:
                    params = item['description']['parameters']

                    # 按参数名组织数据
                    param_data = {}
                    for platform, param_list in params.items():
                        for param in param_list:
                            name = param['name']
                            if name not in param_data:
                                param_data[name] = {
                                    'platforms': [],
                                    'desc': param.get('desc', ''),  # 保存第一个遇到的描述
                                    'platform_names': {}  # 存储每个平台对应的参数名
                                }
                            param_data[name]['platforms'].append(platform)
                            param_data[name]['platform_names'][platform] = name

                    # 为每个唯一参数创建 plentry
                    for param_name, data in param_data.items():
                        # 检查是否已存在相同的参数
                        exists = False
                        for existing_pt in params_section.findall(".//pt"):
                            if existing_pt.text == param_name:
                                exists = True
                                break

                        if exists:
                            continue

                        # 创建新的 plentry 结构
                        plentry = etree.SubElement(target_parent, 'plentry')
                        plentry.tail = indent  # 设置 plentry 的 tail 以保持缩进

                        # 设置 plentry 的 text 为换行加缩进
                        plentry.text = '\n' + child_indent

                        pt = etree.SubElement(plentry, 'pt')
                        # 设置 <pt> 的 text 和换行缩进
                        pt.text = param_name
                        pt.tail = '\n' + child_indent

                        pd = etree.SubElement(plentry, 'pd')
                        pd.text = data['desc']
                        # 修改这一行，移除换行符
                        pd.tail = indent  # 设置 <pd> 的 tail 为 plentry 的缩进，让 </plentry> 直接跟随

                        # 设置平台属性
                        if data['platforms']:
                            platform_values = []
                            for platform in data['platforms']:
                                # windows 对应的值为 cpp
                                platform_value = 'cpp' if platform == 'windows' else PLATFORM_TO_KEYSMAP.get(platform, platform)
                                platform_values.append(platform_value)
                            pt.set('props', ' '.join(platform_values))

                # 处理 enums
                if item['attributes'] == 'enum' and 'enumerations' in item['description']:
                    enumerations = item['description']['enumerations']

                    # 按 alias 组织数据
                    enum_data = {}
                    for platform, enum_list in enumerations.items():
                        for enum in enum_list:
                            alias = enum['alias']
                            desc = enum.get('desc', '')
                            if alias not in enum_data:
                                enum_data[alias] = {
                                    'platforms': [],
                                    'desc': desc
                                }
                            enum_data[alias]['platforms'].append(platform)

                    # 为每个唯一枚举创建 plentry
                    for alias, data in enum_data.items():
                        # 检查是否已存在相同的枚举
                        exists = False
                        for existing_pt in params_section.findall(".//pt"):
                            if existing_pt.find('ph') is not None and existing_pt.find('ph').get('keyref') == alias:
                                exists = True
                                break

                        if exists:
                            continue

                        # 创建新的 plentry 结构
                        plentry = etree.SubElement(target_parent, 'plentry')
                        plentry.tail = indent  # 设置 plentry 的 tail 以保持缩进

                        # 设置 plentry 的 text 为换行加缩进
                        plentry.text = '\n' + child_indent

                        pt = etree.SubElement(plentry, 'pt')
                        # 创建 <ph> 元素并设置 keyref
                        ph = etree.SubElement(pt, 'ph')
                        ph.set('keyref', alias)
                        # 设置 <pt> 的 tail
                        pt.tail = '\n' + child_indent

                        pd = etree.SubElement(plentry, 'pd')
                        pd.text = data['desc']
                        # 设置 <pd> 的 tail 为 plentry 的缩进
                        pd.tail = indent

                        # 设置平台属性
                        if data['platforms']:
                            platform_values = []
                            for platform in data['platforms']:
                                # windows 对应的值为 cpp
                                platform_value = 'cpp' if platform == 'windows' else PLATFORM_TO_KEYSMAP.get(platform, platform)
                                platform_values.append(platform_value)
                            pt.set('props', ' '.join(platform_values))

                # 保存修改后的文件
                tree.write(dita_path, encoding='utf-8', xml_declaration=True, pretty_print=False)
                print(f"Successfully updated {dita_path}")

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