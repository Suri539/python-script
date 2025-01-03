encoding = 'utf-8'
from lxml import etree
import json
import os
import shutil
import re

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
    "cs": "unity",
    "electron": "electron",
    "flutter": "flutter",
    "rn": "rn"
}

# 定义平台配置
platform_configs = [
    {'platform': 'android', 'platform1': 'java', 'platform2': 'Android', 'platform3': 'android'},
    {'platform': 'ios', 'platform1': 'ios', 'platform2': 'iOS', 'platform3': 'ios'},
    {'platform': 'macos', 'platform1': 'macos', 'platform2': 'macOS', 'platform3': 'mac'},
    {'platform': 'windows', 'platform1': 'cpp', 'platform2': 'CPP', 'platform3': 'cpp'},
    {'platform': 'flutter', 'platform1': 'flutter', 'platform2': 'Flutter', 'platform3': 'flutter'},
    {'platform': 'unity', 'platform1': 'unity', 'platform2': 'Unity', 'platform3': 'unity'},
    {'platform': 'electron', 'platform1': 'electron', 'platform2': 'Electron', 'platform3': 'electron'},
    {'platform': 'rn', 'platform1': 'rn', 'platform2': 'RN', 'platform3': 'rn'},
]

# 获取基础目录路径
base_dir = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/dita'

# 读取 JSON 数据
with open('data.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

def create_dita_file(template_path, new_file_path):
    """创建新的 dita 文件"""
    # 检查文件是否已存在
    if os.path.exists(new_file_path):
        print(f"警告：文件已存在，跳过创建：{new_file_path}")
        return False

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            print(f"成功创建文件：{new_file_path}")
        return True
    except Exception as e:
        print(f"创建文件时出错：{str(e)}")
        return False

def get_platform_prop(platform, platform_configs):
    """根据平台获取对应的 platform3 值"""
    for config in platform_configs:
        if config['platform'] == platform:
            return config['platform3']
    return platform

def update_parameters_section(parameters_section, platform_configs, dita_params):
    """更新参数部分"""
    # 找到 parml 元素
    parml = parameters_section.find('parml')
    if parml is None:
        parml = etree.SubElement(parameters_section, 'parml')
    else:
        # 清除模板中的空 plentry
        for empty_plentry in parml.findall('plentry'):
            if not empty_plentry.findall('pt') or not empty_plentry.findall('pd'):
                parml.remove(empty_plentry)
            else:
                pts = empty_plentry.findall('pt')
                pds = empty_plentry.findall('pd')
                if all(not pt.text for pt in pts) and all(not pd.text for pd in pds):
                    parml.remove(empty_plentry)
    
    # 添加换行和缩进
    parml.text = '\n            '
    
    # 处理每个参数
    for param in dita_params:
        # 获取支持的平台列表并转换为 platform3
        platform_props = []
        for p in param['platforms']:
            platform_prop = get_platform_prop(p, platform_configs)
            if platform_prop:
                platform_props.append(platform_prop)
        
        # 创建 plentry
        plentry = etree.SubElement(parml, 'plentry')
        plentry.set('props', ' '.join(platform_props))
        plentry.text = '\n                '
        plentry.tail = '\n            '
        
        # 添加通用参数名
        pt = etree.SubElement(plentry, 'pt')
        pt.text = param['name']
        pt.tail = '\n                '
        
        # 处理平台特定的参数名
        if 'platform_only_name' in param:
            # 按参数名分组平台
            name_platforms = {}
            for p, name in param['platform_only_name'].items():
                platform_prop = get_platform_prop(p, platform_configs)
                if name not in name_platforms:
                    name_platforms[name] = []
                name_platforms[name].append(platform_prop)
            
            # 为每组创建 pt
            for name, props in name_platforms.items():
                pt = etree.SubElement(plentry, 'pt')
                pt.text = name
                pt.set('props', ' '.join(props))
                pt.tail = '\n                '
        
        # 添加通用描述
        pd = etree.SubElement(plentry, 'pd')
        pd.text = param['desc']
        pd.tail = '\n                '
        
        # 处理平台特定的描述
        if 'platform_only_desc' in param:
            # 按描述分组平台
            desc_platforms = {}
            for p, desc in param['platform_only_desc'].items():
                platform_prop = get_platform_prop(p, platform_configs)
                if desc not in desc_platforms:
                    desc_platforms[desc] = []
                desc_platforms[desc].append(platform_prop)
            
            # 为每组创建 pd
            for desc, props in desc_platforms.items():
                pd = etree.SubElement(plentry, 'pd')
                pd.text = desc
                pd.set('props', ' '.join(props))
                pd.tail = '\n                '
        
        # 调整最后一个元素的缩进
        if len(plentry) > 0:
            plentry[-1].tail = '\n            '
    
    # 调整最后一个 plentry 的缩进
    if len(parml) > 0:
        parml[-1].tail = '\n        '

def process_api_change(change_item, templates, platform_configs, new_file_path):
    """处理单个 API 变更"""
    if change_item['change_type'] != 'create':
        return

    # 确定模板和文件名
    is_callback = change_item['attributes'] == 'callback'
    template_path = templates['callback'] if is_callback else templates['method']
    prefix = 'callback' if is_callback else 'api'

    file_name = f"{prefix}_{change_item['parentclass']}_{change_item['key']}.dita".lower()
    full_file_path = os.path.join(new_file_path, file_name)

    # 创建文件，如果文件已存在则返回
    if not create_dita_file(template_path, full_file_path):
        return

    # 解析并更新文件
    tree = etree.parse(full_file_path)
    root = tree.getroot()

    # 更新各个字段，添加错误检查
    if root.tag != 'reference':
        print(f"错误：根元素不是 reference，而是 {root.tag}")
        return
    root.set('id', file_name[:-5])

    title_ph = root.find('.//ph[@keyref]')
    if title_ph is None:
        print(f"错误：在文件 {file_name} 中找不到 title ph 标签")
    else:
        title_ph.set('keyref', change_item['key'])

    # 1. 更新 shortdesc，删除 oxy-placeholder
    try:
        shortdesc_ph = root.find('.//shortdesc/ph')
        if shortdesc_ph is None:
            print(f"警告：找不到 shortdesc/ph 标签")
        else:
            for child in shortdesc_ph:
                shortdesc_ph.remove(child)
            shortdesc_ph.text = change_item['description']['shortdesc']
            print(f"成功更新 shortdesc")
    except Exception as e:
        print(f"更新 shortdesc 时出错：{str(e)}")

    # 2. 更新 API 原型
    prototype_section = root.find('.//section[@id="prototype"]')
    if prototype_section is not None and 'api_signature' in change_item:
        for platform, signature in change_item['api_signature'].items():
            # 获取正确的平台属性
            platform_prop = get_platform_prop(platform, platform_configs)

            # 根据平台找到对应的 codeblock
            if platform == 'windows':
                codeblock = prototype_section.find('.//codeblock[@props="cpp unreal"]')
            elif platform == 'macos':
                codeblock = prototype_section.find('.//codeblock[@props="ios mac"]')
            elif platform == 'ios':
                codeblock = prototype_section.find('.//codeblock[@props="ios mac"]')
            else:
                codeblock = prototype_section.find(f'.//codeblock[@props="{platform_prop}"]')

            if codeblock is not None:
                codeblock.text = signature
            else:
                print(f"警告：找不到 {platform} 平台的 codeblock")

    # 3. 更新 detailed_desc 部分
    detailed_desc_section = root.find('.//section[@id="detailed_desc"]')
    if detailed_desc_section is not None:
        desc = change_item.get('description', {})
        
        # 更新 since 版本
        if 'detailed_desc' in desc:
            dd = detailed_desc_section.find('.//dlentry/dd')
            if dd is not None and 'since' in desc['detailed_desc']:
                dd.text = f"v{desc['detailed_desc']['since']}"
        
        # 更新通用描述
        if 'detailed_desc' in desc:
            p = detailed_desc_section.find('p')
            if p is not None and 'desc' in desc['detailed_desc']:
                p.text = desc['detailed_desc']['desc']
                p.tail = '\n            '
                
                # 处理平台特定的描述
                if 'platform_only_desc' in desc:
                    desc_platforms = {}
                    for platform, platform_desc in desc['platform_only_desc'].items():
                        platform_prop = get_platform_prop(platform, platform_configs)
                        if platform_desc not in desc_platforms:
                            desc_platforms[platform_desc] = []
                        desc_platforms[platform_desc].append(platform_prop)
                    
                    for platform_desc, props in desc_platforms.items():
                        platform_p = etree.SubElement(detailed_desc_section, 'p')
                        platform_p.text = platform_desc
                        platform_p.set('props', ' '.join(props))
                        platform_p.tail = '\n            '
    
    # 4. 更新调用限制和相关回调
    desc = change_item.get('description', {})

    # 更新调用限制
    restriction_section = root.find('.//section[@id="restriction"]/p')
    if restriction_section is not None and 'restrictions' in desc:
        restriction_section.text = desc['restrictions']

    # 更新相关回调
    related_section = root.find('.//section[@id="related"]/p')
    if related_section is not None and 'related' in desc:
        related_section.text = desc['related']

    indexterm = root.find('.//indexterm')
    if indexterm is None:
        print(f"错误：在文件 {file_name} 中找不到 indexterm 标签")
    else:
        indexterm.set('keyref', change_item['key'])

    # 更新描述相关字段
    desc = change_item['description']

    detailed_desc_dd = root.find('.//section[@id="detailed_desc"]//dlentry/dd')
    if detailed_desc_dd is not None and 'since' in desc:
        detailed_desc_dd.text = f"v{desc['since']}"

    if 'detailed_desc' in desc and 'desc' in desc['detailed_desc']:
        detailed_desc_p = root.find('.//section[@id="detailed_desc"]/p')
        if detailed_desc_p is not None:
            detailed_desc_p.text = desc['detailed_desc']['desc']

    # 更新其他描述字段
    field_mappings = {
        'scenarios': 'scenario',
        'timing': 'timing',
        'restriction': 'restriction',
        'related': 'related'
    }

    for json_field, section_id in field_mappings.items():
        if json_field in desc:
            section = root.find(f'.//section[@id="{section_id}"]/p')
            if section is not None:
                section.text = desc[json_field]

    # 更新参数部分
    parameters_section = root.find('.//section[@id="parameters"]')
    if parameters_section is not None and 'dita_params' in change_item.get('description', {}):
        update_parameters_section(parameters_section, platform_configs, 
                               change_item['description']['dita_params'])
    
    # 更新返回值部分
    return_values_section = root.find('.//section[@id="return_values"]')
    if return_values_section is not None:
        desc = change_item.get('description', {})
        if 'return_values' in desc:
            # 找到目标 ul 元素
            ul = return_values_section.find('ul[@props="native unreal bp electron unity rn cs"]')
            if ul is not None:
                # 按返回值描述分组平台
                desc_platforms = {}
                for platform, return_desc in desc['return_values'].items():
                    platform_prop = get_platform_prop(platform, platform_configs)
                    if return_desc not in desc_platforms:
                        desc_platforms[return_desc] = []
                    desc_platforms[return_desc].append(platform_prop)
                
                # 确保 ul 有正确的缩进
                ul.text = '\n                '
                
                # 为每组创建新的 li 元素
                for return_desc, props in desc_platforms.items():
                    li = etree.SubElement(ul, 'li')
                    li.text = return_desc
                    li.set('props', ' '.join(props))
                    li.tail = '\n                '
                
                # 调整所有 li 的缩进
                for li in ul.findall('li'):
                    li.tail = '\n                '
                
                # 最后一个 li 的缩进需要特殊处理
                if len(ul) > 0:
                    ul[-1].tail = '\n            '
                
                # 调整 ul 的缩进
                ul.tail = '\n        '
    
    # 获取描述相关字段
    desc = change_item.get('description', {})

    # 1. 处理可能需要删除的部分
    sections_to_check = {
        'scenario': desc.get('scenarios', ''),
        'related': desc.get('related', ''),
        'parameters': desc.get('parameters', {})
    }

    for section_id, content in sections_to_check.items():
        section = root.find(f'.//section[@id="{section_id}"]')
        if section is not None:
            if not content:  # 如果内容为空
                section.getparent().remove(section)
                print(f"已删除空的 {section_id} section")
            elif section_id == 'parameters':
                # parameters 需要特殊处理，如果没有任何平台的参数，也删除
                if not any(content.values()):
                    section.getparent().remove(section)
                    print("已删除空的 parameters section")

    # 2. 处理 timing section
    timing_section = root.find('.//section[@id="timing"]/p')
    if timing_section is not None:
        timing_content = desc.get('timing', '')
        if not timing_content:
            timing_section.text = "加入频道前后均可调用。"
            print("已设置默认的 timing 内容")
        else:
            timing_section.text = timing_content

    # 3. 处理 restriction section
    restriction_section = root.find('.//section[@id="restriction"]/p')
    if restriction_section is not None:
        restriction_content = desc.get('restrictions', '')
        if not restriction_content:
            restriction_section.text = "无。"
            print("已设置默认的 restriction 内容")
        else:
            restriction_section.text = restriction_content

    # 保存更新后的文件
    tree.write(full_file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

def process_enum_change(change_item, templates, platform_configs, new_file_path):
    """处理单个枚举变更"""
    if change_item['change_type'] != 'create':
        return

    # 处理文件名：删除连字符并转换为小写
    enum_key = change_item['key'].replace('-', '').lower()
    file_name = f"enum_{enum_key}.dita"
    full_file_path = os.path.join(new_file_path, file_name)

    # 创建文件，如果文件已存在则返回
    if not create_dita_file(templates['enum'], full_file_path):
        return

    # 解析并更新文件
    tree = etree.parse(full_file_path)
    root = tree.getroot()

    # 更新各个字段，添加错误检查
    if root.tag != 'reference':
        print(f"错误：根元素不是 reference，而是 {root.tag}")
        return
    root.set('id', file_name[:-5])

    # 更新 title
    title_ph = root.find('.//ph[@keyref]')
    if title_ph is None:
        print(f"错误：在文件 {file_name} 中找不到 title ph 标签")
    else:
        title_ph.set('keyref', change_item['key'])

    # 更新 shortdesc
    try:
        shortdesc_ph = root.find('.//shortdesc/ph')
        if shortdesc_ph is None:
            print(f"警告：找不到 shortdesc/ph 标签")
        else:
            for child in shortdesc_ph:
                shortdesc_ph.remove(child)
            shortdesc_ph.text = change_item['description']['shortdesc']
            print(f"成功更新 shortdesc")
    except Exception as e:
        print(f"更新 shortdesc 时出错：{str(e)}")

    # 更新 detailed_desc 部分
    detailed_desc_section = root.find('.//section[@id="detailed_desc"]')
    if detailed_desc_section is not None:
        desc = change_item.get('description', {})

        # 更新 since 版本
        if 'detailed_desc' in desc and isinstance(desc['detailed_desc'], list) and desc['detailed_desc']:
            dd = detailed_desc_section.find('.//dlentry/dd')
            if dd is not None and 'since' in desc['detailed_desc'][0]:
                dd.text = f"v{desc['detailed_desc'][0]['since']}"

        # 更新描述
        if 'detailed_desc' in desc and isinstance(desc['detailed_desc'], list) and desc['detailed_desc']:
            p = detailed_desc_section.find('p')
            if p is not None and 'desc' in desc['detailed_desc'][0]:
                p.text = desc['detailed_desc'][0]['desc']

    # 更新枚举值部分
    if 'enumerations' in change_item['description']:
        enums_section = root.find('.//section[@id="parameters"]')
        if enums_section is not None:
            # 获取或创建 parml 元素
            parml = enums_section.find('parml')
            if parml is None:
                parml = etree.SubElement(enums_section, 'parml')

            # 清除模板中的空 plentry
            for empty_plentry in parml.findall('plentry'):
                if not empty_plentry.findall('pt') or not empty_plentry.findall('pd'):
                    parml.remove(empty_plentry)
                else:
                    pts = empty_plentry.findall('pt')
                    pds = empty_plentry.findall('pd')
                    if all(not pt.text for pt in pts) and all(not pd.text for pd in pds):
                        parml.remove(empty_plentry)

            # 添加换行和缩进
            parml.text = '\n            '

            # 按 alias 组织枚举值
            enum_groups = {}
            for platform, enums in change_item['description']['enumerations'].items():
                platform_prop = get_platform_prop(platform, platform_configs)
                for enum in enums:
                    if enum['change_type'] != 'create':
                        continue

                    alias = enum['alias']
                    if alias not in enum_groups:
                        enum_groups[alias] = {}

                    if platform not in enum_groups[alias]:
                        enum_groups[alias][platform] = {
                            'value': enum['value'],
                            'desc': enum['desc'],
                            'platform_prop': platform_prop
                        }

            # 创建枚举值条目
            for alias, platforms in enum_groups.items():
                plentry = etree.SubElement(parml, 'plentry')
                plentry.text = '\n                '
                plentry.tail = '\n            '

                # 收集所有平台的值和描述
                values = {}
                descs = {}
                platform_props = set()

                for platform, info in platforms.items():
                    values[info['value']] = info['platform_prop']
                    descs[info['desc']] = info['platform_prop']
                    platform_props.add(info['platform_prop'])

                # 先创建所有的 pt 元素
                for value, prop in values.items():
                    pt = etree.SubElement(plentry, 'pt')
                    pt.text = value
                    pt.set('props', prop)
                    pt.tail = '\n                '

                # 再创建 pd 元素
                for desc in set(info['desc'] for info in platforms.values()):
                    pd = etree.SubElement(plentry, 'pd')
                    pd.text = desc
                    pd.set('props', ' '.join(platform_props))
                    pd.tail = '\n            '

                # 调整最后一个元素的缩进
                if len(plentry) > 0:
                    plentry[-1].tail = '\n            '

            # 调整 parml 的缩进
            parml.tail = '\n        '

    # 保存更新后的文件
    tree.write(full_file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

def process_class_change(change_item, templates, platform_configs, new_file_path):
    """处理单个类变更"""
    if change_item['change_type'] != 'create':
        return

    # 处理文件名
    class_key = change_item['key'].lower()
    file_name = f"class_{class_key}.dita"
    full_file_path = os.path.join(new_file_path, file_name)

    # 创建文件，如果文件已存在则返回
    if not create_dita_file(templates['class'], full_file_path):
        return

    # 解析并更新文件
    tree = etree.parse(full_file_path)
    root = tree.getroot()

    # 更新各个字段
    if root.tag != 'reference':
        print(f"错误：根元素不是 reference，而是 {root.tag}")
        return
    root.set('id', file_name[:-5])

    # 更新 title
    title_ph = root.find('.//ph[@keyref]')
    if title_ph is None:
        print(f"错误：在文件 {file_name} 中找不到 title ph 标签")
    else:
        title_ph.set('keyref', change_item['key'])

    # 更新 shortdesc
    try:
        shortdesc_ph = root.find('.//shortdesc/ph')
        if shortdesc_ph is None:
            print(f"警告：找不到 shortdesc/ph 标签")
        else:
            for child in shortdesc_ph:
                shortdesc_ph.remove(child)
            shortdesc_ph.text = change_item['description']['shortdesc']
            print(f"成功更新 shortdesc")
    except Exception as e:
        print(f"更新 shortdesc 时出错：{str(e)}")

    # 更新 detailed_desc 部分
    detailed_desc_section = root.find('.//section[@id="detailed_desc"]')
    if detailed_desc_section is not None:
        desc = change_item.get('description', {})
        
        # 更新 since 版本
        if 'detailed_desc' in desc:
            dd = detailed_desc_section.find('.//dlentry/dd')
            if dd is not None and 'since' in desc['detailed_desc']:
                dd.text = f"v{desc['detailed_desc']['since']}"
        
        # 更新通用描述
        if 'detailed_desc' in desc:
            p = detailed_desc_section.find('p')
            if p is not None and 'desc' in desc['detailed_desc']:
                p.text = desc['detailed_desc']['desc']
                p.tail = '\n            '
                
                # 处理平台特定的描述
                if 'platform_only_desc' in desc:
                    desc_platforms = {}
                    for platform, platform_desc in desc['platform_only_desc'].items():
                        platform_prop = get_platform_prop(platform, platform_configs)
                        if platform_desc not in desc_platforms:
                            desc_platforms[platform_desc] = []
                        desc_platforms[platform_desc].append(platform_prop)
                    
                    for platform_desc, props in desc_platforms.items():
                        platform_p = etree.SubElement(detailed_desc_section, 'p')
                        platform_p.text = platform_desc
                        platform_p.set('props', ' '.join(props))
                        platform_p.tail = '\n            '

    # 删除 sub-class 和 sub-method sections
    for section_id in ['sub-class', 'sub-method']:
        section = root.find(f'.//section[@id="{section_id}"]')
        if section is not None:
            section.getparent().remove(section)

    # 更新参数部分
    parameters_section = root.find('.//section[@id="parameters"]')
    if parameters_section is not None and 'dita_params' in change_item.get('description', {}):
        update_parameters_section(parameters_section, platform_configs, 
                               change_item['description']['dita_params'])

    # 更新返回值部分
    return_values_section = root.find('.//section[@id="return_values"]')
    if return_values_section is not None:
        desc = change_item.get('description', {})
        if 'return_values' in desc:
            # 找到目标 ul 元素
            ul = return_values_section.find('ul[@props="native unreal bp electron unity rn cs"]')
            if ul is not None:
                # 按返回值描述分组平台
                desc_platforms = {}
                for platform, return_desc in desc['return_values'].items():
                    platform_prop = get_platform_prop(platform, platform_configs)
                    if return_desc not in desc_platforms:
                        desc_platforms[return_desc] = []
                    desc_platforms[return_desc].append(platform_prop)
                
                # 确保 ul 有正确的缩进
                ul.text = '\n                '
                
                # 为每组创建新的 li 元素
                for return_desc, props in desc_platforms.items():
                    li = etree.SubElement(ul, 'li')
                    li.text = return_desc
                    li.set('props', ' '.join(props))
                    li.tail = '\n                '
                
                # 调整所有 li 的缩进
                for li in ul.findall('li'):
                    li.tail = '\n                '
                
                # 最后一个 li 的缩进需要特殊处理
                if len(ul) > 0:
                    ul[-1].tail = '\n            '
                
                # 调整 ul 的缩进
                ul.tail = '\n        '

    # 保存更新后的文件
    tree.write(full_file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

def create_dita_files(json_file_path, templates, platform_configs, new_file_path):
    """创建 DITA 文件的主函数"""
    print(f"尝试读取文件：{json_file_path}")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"成功读取 JSON 文件")
            changes = json.loads(content)

            # 检查变更数据
            print("\n变更数据统计：")
            print(f"API 变更数量: {len(changes.get('api_changes', []))}")
            print(f"枚举变更数量: {len(changes.get('enum_changes', []))}")
            print(f"类变更数量: {len(changes.get('struct_changes', []))}")

            # 检查是否有 create 类型的变更
            create_apis = [c for c in changes.get('api_changes', []) if c.get('change_type') == 'create']
            create_enums = [c for c in changes.get('enum_changes', []) if c.get('change_type') == 'create']
            create_structs = [c for c in changes.get('struct_changes', []) if c.get('change_type') == 'create']

            print("\n新建类型的变更数量：")
            print(f"新建 API 数量: {len(create_apis)}")
            print(f"新建枚举数量: {len(create_enums)}")
            print(f"新建类数量: {len(create_structs)}")

    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"错误：JSON 文件格式不正确: {str(e)}")
        print(f"错误位置附近的内容：{content[max(0, e.pos-50):e.pos+50]}")
        return
    except Exception as e:
        print(f"发生未预期的错误：{str(e)}")
        return

    # 检查输出目录
    if not os.path.exists(new_file_path):
        print("输出目录不存在，尝试创建...")
        try:
            os.makedirs(new_file_path)
            print("成功创建输出目录")
        except Exception as e:
            print(f"创建输出目录失败：{str(e)}")
            return

    # 处理变更
    if create_apis:
        print("\n开始处理 API 变更...")
        for change in create_apis:
            try:
                process_api_change(change, templates, platform_configs, new_file_path)
            except Exception as e:
                print(f"处理 API {change.get('key', '未知')} 时出错：{str(e)}")

    if create_enums:
        print("\n开始处理枚举变更...")
        for change in create_enums:
            try:
                process_enum_change(change, templates, platform_configs, new_file_path)
            except Exception as e:
                print(f"处理枚举 {change.get('key', '未知')} 时出错：{str(e)}")

    if create_structs:
        print("\n开始处理类变更...")
        for change in create_structs:
            try:
                process_class_change(change, templates, platform_configs, new_file_path)
            except Exception as e:
                print(f"处理类 {change.get('key', '未知')} 时出错：{str(e)}")

def modify_dita_files():
    """根据 JSON 数据修改 DITA 文件，同时保持原有格式和缩进一致。"""
    api_dir = os.path.join(base_dir, 'RTC-NG', 'API')

    # 初始化成功和错误信息列表
    success_messages = []
    error_messages = []

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
                    error_messages.append(f"Unsupported attribute type: {item['attributes']}")
                    continue

                dita_path = os.path.join(api_dir, filename)

                if not os.path.exists(dita_path):
                    error_messages.append(f"文件未找到: {dita_path}")
                    continue

                # 读取原始文件内容
                try:
                    with open(dita_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    error_messages.append(f"Error reading {dita_path}: {str(e)}")
                    continue

                # 使用正则表达式提取 <section id="parameters">
                pattern = re.compile(r'(<section\s+id="parameters">.*?</section>)', re.DOTALL)
                match = pattern.search(content)
                if not match:
                    error_messages.append(f"在 {dita_path} 中未找到 parameters section")
                    continue

                parameters_section = match.group(1)

                # 解析 parameters_section
                parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
                try:
                    parameters_tree = etree.fromstring(parameters_section, parser)
                except etree.XMLSyntaxError as e:
                    error_messages.append(f"解析 {dita_path} 中的 parameters section 时出错: {e}")
                    continue

                # 找到 <parml>
                parml = parameters_tree.find("parml")

                if parml is not None:
                    # 获取 <parml> 内现有 plentry 的缩进
                    existing_plentries = parml.findall('plentry')
                    if existing_plentries:
                        last_plentry = existing_plentries[-1]
                        indent = last_plentry.tail if last_plentry.tail else '\n        '
                        child_indent = ' ' * (len(indent) + 4)
                    else:
                        # 默认缩进
                        indent = '\n        '
                        child_indent = indent + '    '

                    target_parent = parml
                else:
                    # 如果没有 <parml>，则直接在 section 下添加 plentry
                    existing_plentries = parameters_tree.findall('plentry')
                    if existing_plentries:
                        last_plentry = existing_plentries[-1]
                        indent = last_plentry.tail if last_plentry.tail else '\n        '
                        child_indent = ' ' * (len(indent) + 4)
                    else:
                        # 默认缩进
                        indent = '\n        '
                        child_indent = indent + '    '

                    target_parent = parameters_tree

                # 处理参数
                params = item['description'].get('parameters', {})
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
                        for existing_pt in parameters_tree.findall(".//pt"):
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
                        # 移除换行符
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
                        for existing_pt in parameters_tree.findall(".//pt"):
                            ph = existing_pt.find('ph')
                            if ph is not None and ph.get('keyref') == alias:
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

                # 序列化修改后的 parameters_section
                modified_parameters = etree.tostring(parameters_tree, encoding='unicode', pretty_print=False)

                # 替换原始的 parameters_section 为修改后的部分
                new_content = pattern.sub(modified_parameters, content)

                # 写回修改后的内容到文件
                try:
                    with open(dita_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    success_messages.append(f"Successfully updated {dita_path}")
                except Exception as e:
                    error_messages.append(f"Error writing to {dita_path}: {str(e)}")

    # 打印成功和错误信息
    if success_messages:
        print("=== 修改 DITA 文件成功信息 ===")
        print("\n".join(success_messages))
    if error_messages:
        print("\n=== 修改 DITA 文件错误信息 ===")
        print("\n".join(error_messages))

def parse_ditamap(ditamap_path, platform_apis):
    """处理单个 ditamap 文件"""
    success_messages = []
    error_messages = []

    print(f"\nProcessing ditamap: {ditamap_path}")
    print(f"Total APIs to process: {len(platform_apis)}")

    try:
        tree = etree.parse(ditamap_path)
        root = tree.getroot()
    except Exception as e:
        error_messages.append(f"Error parsing ditamap {ditamap_path}: {str(e)}")
        print("\n".join(error_messages))
        return

    changes_made = 0

    # 记录需要重新排序的 topicref父元素
    modified_parents = set()

    # 遍历该平台需要处理的 API 数据
    for api_data in platform_apis:
        # 跳过 attributes 为 class 且 navtitle 不为 "Interface classes" 的 API
        # 跳过 attributes 为 enum 的 API
        if (api_data.get('attributes') == 'class' and api_data.get('navtitle') != 'Interface classes') or \
           api_data.get('attributes') == 'enum':
            success_messages.append(f"Skipping API with key '{api_data['key']}' due to attributes '{api_data['attributes']}' and navtitle '{api_data.get('navtitle', '')}'")
            continue

        target_href = api_data['toc_href']
        api_key = api_data['key']

        # 查找目标位置并添加新的 topicref
        for topicref in root.iter('topicref'):
            if topicref.get('href') == target_href:
                # 获取当前 topicref 的缩进级别
                current_indent = ''
                parent = topicref
                while parent is not None:
                    current_indent += '    '
                    parent = parent.getparent()

                # 先添加一个换行和缩进
                topicref.tail = '\n' + current_indent

                new_topicref = etree.Element('topicref')
                new_topicref.set('keyref', api_key)
                new_topicref.set('toc', 'no')
                # 设置新元素的缩进
                new_topicref.tail = '\n' + current_indent

                topicref.append(new_topicref)
                changes_made += 1
                success_messages.append(f"Added new topicref with keyref='{api_key}' under {target_href}")

                # 将修改过的父元素添加到集合中
                modified_parents.add(topicref)

    # 对所有修改过的父元素进行子元素排序
    for parent in modified_parents:
        # 获取所有子元素
        children = list(parent)
        if children:
            # 按字母顺序排序
            children.sort(key=lambda x: x.get('keyref', '').lower())

            # 重新设置子元素的顺序
            for i, child in enumerate(children):
                # 如果不是最后一个元素，设置换行和缩进
                if i < len(children) - 1:
                    child.tail = '\n' + current_indent
                # 如果是最后一个元素，设置换行和父级缩进
                else:
                    child.tail = '\n' + current_indent[:-4]
                # 把元素加到正确的位置
                parent.append(child)

    # 如果有修改，写入文件
    if changes_made > 0:
        try:
            tree.write(ditamap_path, encoding='UTF-8', xml_declaration=True)
            success_messages.append(f"Writing {changes_made} changes to {ditamap_path}")
        except Exception as e:
            error_messages.append(f"Error writing to ditamap {ditamap_path}: {str(e)}")
    else:
        success_messages.append(f"No changes made to {ditamap_path}")

    # 打印成功和错误信息
    if success_messages:
        print("=== 处理 ditamap 成功信息 ===")
        print("\n".join(success_messages))
    if error_messages:
        print("\n=== 处理 ditamap 错误信息 ===")
        print("\n".join(error_messages))

def process_all_ditamaps():
    """处理所有平台的 ditamap 文件"""
    ditamap_base_dir = os.path.join(base_dir, 'RTC-NG')

    # 初始化成功和错误信息列表
    success_messages = []
    error_messages = []

    # 首先按平台组织 API 数据
    platform_api_map = {platform: [] for platform in PLATFORM_FILES.keys()}

    # 遍历所有 API 数据，按平台分组
    for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
        for api_data in json_data.get(change_type, []):
            platforms = api_data.get('platforms', [])

            # 如果platforms是"all"，则添加到所有平台
            if "all" in platforms:
                for platform in PLATFORM_FILES.keys():
                    platform_api_map[platform].append(api_data)
            else:
                # 否则只添加到指定的平台
                for platform in platforms:
                    if platform in platform_api_map:
                        platform_api_map[platform].append(api_data)

    # 解析 RTC-NG/config 路径下所有的 keys-rtc-ng-api-{platform}.ditamap 文件
    keysmaps_dir = os.path.join(base_dir, 'RTC-NG','config')

    # 遍历每个平台
    for platform, apis in platform_api_map.items():
        keysmap_platform = PLATFORM_TO_KEYSMAP.get(platform)
        if not keysmap_platform:
            error_messages.append(f"Warning: No keysmap mapping found for platform {platform}")
            continue

        ditamap_path = os.path.join(ditamap_base_dir, PLATFORM_FILES.get(platform, ''))
        if not os.path.exists(ditamap_path):
            error_messages.append(f"Warning: Ditamap file not found for platform {platform}: {ditamap_path}")
            continue

        # 处理该平台的 ditamap
        parse_ditamap(ditamap_path, apis)
        success_messages.append(f"Processed ditamap for platform {platform}")

    # 打印成功和错误信息
    if success_messages:
        print("\n=== 处理所有 ditamap 成功信息 ===")
        print("\n".join(success_messages))
    if error_messages:
        print("\n=== 处理所有 ditamap 错误信息 ===")
        print("\n".join(error_messages))

def create_and_insert_keydef(root, api_data, platform):
    """创建并插入新的 keydef 元素"""
    success_messages = []
    error_messages = []

    # 获取第一个 topichead 下的第一个 keydef 作为参考
    reference_keydef = root.find('.//topichead/keydef')
    if reference_keydef is None:
        error_messages.append("Warning: No reference keydef found for indentation")
        print("\n".join(error_messages))
        return False

    # 获取基础缩进（keydef 元素的缩进）
    base_indent = (reference_keydef.tail or '').rpartition('\n')[2]

    # 检查是否为 enum 类型
    if api_data.get('attributes') == 'enum' and 'enumerations' in api_data['description']:
        # 插入 enum keydef
        target_navtitle = api_data.get('navtitle')
        if not target_navtitle:
            error_messages.append(f"Warning: No navtitle specified for API {api_data['key']}")
            print("\n".join(error_messages))
            return False

        # 为枚举创建 keydef
        enum_keydef = etree.Element('keydef')
        enum_keydef.set('keys', api_data['keyword'].get(platform, api_data['key']))
        # 移除 href 里面的下划线
        enum_keydef.set('href', f"../API/enum_{api_data['key'].lower().replace('_', '')}.dita")
        enum_keydef.text = '\n' + base_indent + '    '
        enum_keydef.tail = '\n' + base_indent

        topicmeta = etree.SubElement(enum_keydef, 'topicmeta')
        topicmeta.text = '\n' + base_indent + '        '
        topicmeta.tail = '\n' + base_indent + '    '

        keywords = etree.SubElement(topicmeta, 'keywords')
        keywords.text = '\n' + base_indent + '            '
        keywords.tail = '\n' + base_indent + '        '

        keyword = etree.SubElement(keywords, 'keyword')
        keyword.text = api_data['keyword'].get(platform, api_data['key'])
        keyword.tail = '\n' + base_indent + '        '

        # 插入枚举 keydef
        for topichead in root.iter('topichead'):
            if topichead.get('navtitle') == target_navtitle:
                topichead.append(enum_keydef)
                success_messages.append(f"Added enum keydef for API {api_data['key']} to navtitle '{target_navtitle}'")

                # 添加枚举值 keydef
                for enum_platform, enums in api_data['description']['enumerations'].items():
                    if platform == enum_platform:
                        for enum in enums:
                            alias = enum.get('alias')
                            value = enum.get('value')
                            if alias and value:
                                # 为每个枚举创建 keydef
                                enum_value_keydef = etree.Element('keydef')
                                enum_value_keydef.set('keys', alias)  # 设置 keys 为 alias
                                enum_value_keydef.text = '\n' + base_indent + '    '
                                enum_value_keydef.tail = '\n' + base_indent

                                topicmeta = etree.SubElement(enum_value_keydef, 'topicmeta')
                                topicmeta.text = '\n' + base_indent + '        '
                                topicmeta.tail = '\n' + base_indent + '    '

                                keywords = etree.SubElement(topicmeta, 'keywords')
                                keywords.text = '\n' + base_indent + '            '
                                keywords.tail = '\n' + base_indent + '        '

                                keyword = etree.SubElement(keywords, 'keyword')
                                keyword.text = value  # Set keyword to value
                                keyword.tail = '\n' + base_indent + '        '

                                # 插入枚举值 keydef
                                topichead.append(enum_value_keydef)
                                success_messages.append(f"Added enum value keydef '{alias}' with value '{value}'")

                print("\n".join(success_messages))
                return True

        error_messages.append(f"Warning: No matching topichead found for navtitle '{target_navtitle}'")
        print("\n".join(error_messages))
        return False

    # 处理非 enum 类型的 keydef
    new_keydef = etree.Element('keydef')
    new_keydef.set('keys', api_data['key'])

    # 获取attributes和parentclass
    attributes = api_data.get('attributes', '')
    parentclass = api_data.get('parentclass', '').lower()

    # 根据不同条件构建href
    if attributes == 'enum':
        # enum类型的特殊处理，移除keyname中的下划线
        keyname = api_data['key'].lower().replace('_', '')
        new_keydef.set('href', f"../API/{attributes}_{keyname}.dita")
    elif parentclass == 'none':
        # parentclass为none的处理
        new_keydef.set('href', f"../API/{attributes}_{api_data['key'].lower()}.dita")
    else:
        # 默认处理
        new_keydef.set('href', f"../API/{attributes}_{parentclass}_{api_data['key'].lower()}.dita")

    new_keydef.text = '\n' + base_indent + '    '  # 为第一个子元素添加缩进
    new_keydef.tail = '\n' + base_indent

    if 'keyword' in api_data:
        # 创建 topicmeta
        topicmeta = etree.SubElement(new_keydef, 'topicmeta')
        topicmeta.text = '\n' + base_indent + '        '  # 为 keywords 添加缩进
        topicmeta.tail = '\n' + base_indent + '    '

        # 创建 keywords
        keywords = etree.SubElement(topicmeta, 'keywords')
        keywords.text = '\n' + base_indent + '            '  # 为 keyword 添加缩进
        keywords.tail = '\n' + base_indent + '        '

        # 获取当前平台的关键字
        keyword_value = api_data['keyword'] if isinstance(api_data['keyword'], str) else api_data['keyword'].get(platform, api_data['key'])
        keyword = etree.SubElement(keywords, 'keyword')
        keyword.text = keyword_value
        keyword.tail = '\n' + base_indent + '        '

    # 查找目标 topichead 并插入
    target_navtitle = api_data.get('navtitle')
    if not target_navtitle:
        error_messages.append(f"Warning: No navtitle specified for API {api_data['key']}")
        print("\n".join(error_messages))
        return False

    for topichead in root.iter('topichead'):
        if topichead.get('navtitle') == target_navtitle:
            # 检查是否已存在相同的 keydef
            exists = False
            for existing_keydef in topichead.findall('keydef'):
                if existing_keydef.get('keys') == api_data['key']:
                    exists = True
                    break
            if exists:
                error_messages.append(f"Warning: Keydef with key '{api_data['key']}' already exists in {target_navtitle}")
                print("\n".join(error_messages))
                return False

            # 添加元素
            topichead.append(new_keydef)
            success_messages.append(f"Added keydef for API {api_data['key']} to navtitle '{target_navtitle}'")
            print("\n".join(success_messages))
            return True

    error_messages.append(f"Warning: No matching topichead found for navtitle '{target_navtitle}'")
    print("\n".join(error_messages))
    return False

def parse_keysmaps():
    """处理所有平台的 keysmaps 文件"""
    # 创建平台到API的映射
    platform_apis = {
        'android': [],
        'ios': [],
        'windows': [],
        'macos': [],
        'unreal': [],
        'cs': [],
        'electron': [],
        'flutter': [],
        'rn': [],
        'unity': []
    }
    # 将 API 按平台分类
    for change_type in ['api_changes', 'struct_changes', 'enum_changes']:
        for api_data in json_data.get(change_type, []):
            platforms = api_data.get('platforms', [])
            # 如果platforms是"all"，添加到所有平台
            if "all" in platforms:
                for platform in platform_apis.keys():
                    platform_apis[platform].append(api_data)
            else:
                # 否则只添加到指定的平台
                for platform in platforms:
                    if platform in platform_apis:
                        platform_apis[platform].append(api_data)

    # 解析 RTC-NG/config 路径下所有的 keys-rtc-ng-api-{platform}.ditamap 文件
    keysmaps_dir = os.path.join(base_dir, 'RTC-NG','config')

    # 初始化成功和错误信息列表
    success_messages = []
    error_messages = []

    # 遍历每个平台
    for json_platform, keysmap_platform in PLATFORM_TO_KEYSMAP.items():
        keysmap_file = os.path.join(keysmaps_dir, f'keys-rtc-ng-api-{keysmap_platform}.ditamap')
        if not os.path.exists(keysmap_file):
            error_messages.append(f"Warning: Keymap file not found: {keysmap_file}")
            continue

        print(f"\nProcessing keymap for platform: {json_platform}")

        # 检查该平台是否有需要处理的API
        if not platform_apis[json_platform]:
            success_messages.append(f"No APIs to process for platform {json_platform}")
            continue

        tree = etree.parse(keysmap_file)
        root = tree.getroot()
        changes_made = 0

        # 处理该平台的所有API
        for api_data in platform_apis[json_platform]:
            # 仅在指定的平台中添加 keydef
            if json_platform in api_data.get('platforms', []) or "all" in api_data.get('platforms', []):
                if create_and_insert_keydef(root, api_data, json_platform):
                    changes_made += 1
                    success_messages.append(f"Added keydef for API {api_data['key']} to {json_platform}")

        # 如果有修改，保存文件
        if changes_made > 0:
            try:
                tree.write(keysmap_file, encoding='UTF-8', xml_declaration=True)
                success_messages.append(f"Writing {changes_made} changes to {keysmap_file}")
            except Exception as e:
                error_messages.append(f"Error writing to keymap {keysmap_file}: {str(e)}")
        else:
            success_messages.append(f"No changes made to {keysmap_file}")

    # 打印成功和错误信息
    if success_messages:
        print("\n=== 处理 keysmaps 成功信息 ===")
        print("\n".join(success_messages))
    if error_messages:
        print("\n=== 处理 keysmaps 错误信息 ===")
        print("\n".join(error_messages))

def insert_relations(relations_path):
    """处理 relations 文件，插入 API 关系"""
    print(f"\nProcessing relations file: {relations_path}")

    # 解析 relations 文件
    tree = etree.parse(relations_path)
    root = tree.getroot()
    changes_made = 0

    # 创建平台映射字典
    platform_map = {config['platform']: config['platform1'] for config in platform_configs}

    # 遍历所有类型的变更
    for change_type in ['api_changes']:
        # struct_changes 和 enum_changes 不需要处理 relations
        if change_type not in json_data:
            continue

        for change_item in json_data[change_type]:
            # 检查是否需要处理该 API
            if change_item.get('attributes') not in ['api', 'callback']:
                continue

            # 获取必要的数据
            key = change_item['key']
            parentclass = change_item.get('parentclass')
            platforms = change_item.get('platforms', [])

            # 转换平台名称
            props = []
            if "all" not in platforms:  # 只有当不是 "all" 时才添加 props
                props = [platform_map[p] for p in platforms if p in platform_map]

            if not parentclass:
                continue

            # 构建 props 属性字符串
            props_str = ' '.join(props)

            # 在 reltable 中查找对应的 parentclass
            for relrow in root.findall('.//relrow'):
                found = False
                has_props = False
                target_cell = None

                # 查找包含目标 parentclass 的 relcell
                for relcell in relrow.findall('relcell'):
                    for topicref in relcell.findall('topicref'):
                        if topicref.get('keyref') == parentclass:
                            # 检查父节点是否有 props="hide" 属性
                            for ancestor in topicref.iterancestors():
                                if ancestor.get('props') == 'hide':
                                    has_props = True
                                    print(f"Skipping API {key} as its parent has props='hide' attribute")
                                    break

                            if has_props:
                                break

                            # 找到目标 relcell，获取另一个 relcell
                            target_cell = relrow.findall('relcell')[0]
                            found = True
                            break
                    if found or has_props:
                        break

                if found and target_cell is not None and not has_props:
                    # 检查是否已存在相同的 keyref
                    exists = False
                    for existing_topicref in target_cell.findall('topicref'):
                        if existing_topicref.get('keyref') == key:
                            exists = True
                            break

                    if not exists:
                        # 创建新的 topicref 元素
                        new_topicref = etree.Element('topicref')
                        new_topicref.set('keyref', key)
                        if props:  # 只有当 props 不为空时才添加
                            new_topicref.set('props', ' '.join(props))

                        # 获取当前缩进级别
                        current_indent = ''
                        parent = target_cell
                        while parent is not None:
                            current_indent += '    '
                            parent = parent.getparent()

                        # 设置新元素的缩进
                        new_topicref.tail = '\n' + current_indent

                        # 添加到目标 relcell 并按字母顺序排序
                        target_cell.append(new_topicref)
                        changes_made += 1
                        print(f"Added relation for API {key} under {parentclass}")

                        # 获取所有 topicref 元素并排序
                        topicrefs = target_cell.findall('topicref')
                        sorted_topicrefs = sorted(topicrefs, key=lambda x: x.get('keyref', ''))

                        # 清空 relcell
                        for child in list(target_cell):
                            target_cell.remove(child)

                        # 重新按顺序添加元素
                        for i, topicref in enumerate(sorted_topicrefs):
                            if i < len(sorted_topicrefs) - 1:
                                topicref.tail = '\n' + current_indent
                            else:
                                topicref.tail = '\n' + current_indent[:-4]
                            target_cell.append(topicref)

    # 如果有修改，保存文件
    if changes_made > 0:
        print(f"Writing {changes_made} changes to {relations_path}")
        tree.write(relations_path, encoding='UTF-8', xml_declaration=True)
    else:
        print(f"No changes made to {relations_path}")

def insert_datatype(datatype_path):
    """处理 datatype 文件，插入类和枚举的引用"""
    print(f"\n处理 datatype 文件: {datatype_path}")

    # 解析 datatype 文件
    tree = etree.parse(datatype_path)
    root = tree.getroot()
    changes_made = 0

    # 创建平台映射字典
    platform_map = {config['platform']: config['platform3'] for config in platform_configs}

    # 遍历所有类型的变更
    for change_type, section_id in [('struct_changes', 'class'), ('enum_changes', 'enum')]:
        if change_type not in json_data:
            continue

        for change_item in json_data[change_type]:
            platforms = change_item.get('platforms', [])
            props = []
            if "all" in platforms:
                props = [platform_map[p] for p in platform_map.keys()]
            else:
                props = [platform_map[p] for p in platforms if p in platform_map]

            if not props:
                continue

            # 查找对应的 section
            section = root.find(f".//section[@id='{section_id}']")
            if section is None:
                print(f"警告: 未找到 section id='{section_id}'")
                continue

            changes_in_api = 0

            # 为每个平台创建或更新 ul 元素
            for prop in props:
                # 查找或创建对应平台的 ul
                ul = section.find(f"ul[@props='{prop}']")
                if ul is not None:
                    # 检查是否已存在相同的 xref
                    exists = False
                    for li in ul.findall('li'):
                        xref = li.find('xref')
                        if xref is not None and xref.get('keyref') == change_item['key']:
                            exists = True
                            break

                    if not exists:
                        # 创建新的 li 和 xref 元素
                        new_li = etree.SubElement(ul, 'li')
                        new_xref = etree.SubElement(new_li, 'xref')
                        new_xref.set('keyref', change_item['key'])

                        # 设置缩进
                        new_li.tail = '\n            '

                        changes_in_api += 1
                        print(f"添加了 {change_item['key']} 到 {prop} 平台的 {section_id} 部分")

                        # 对 li 元素进行排序
                        lis = ul.findall('li')
                        sorted_lis = sorted(lis, key=lambda x: x.find('xref').get('keyref', ''))

                        # 清空 ul
                        for child in list(ul):
                            ul.remove(child)

                        # 重新按顺序添加元素
                        for i, li in enumerate(sorted_lis):
                            if i < len(sorted_lis) - 1:
                                li.tail = '\n            '
                            else:
                                li.tail = '\n        '
                            ul.append(li)

            changes_made += changes_in_api

    # 如果有修改，保存文件
    if changes_made > 0:
        print(f"总共向 {datatype_path} 添加了 {changes_made} 处修改")
        tree.write(datatype_path, encoding='UTF-8', xml_declaration=True)
    else:
        print(f"未对 {datatype_path} 进行任何修改")

def main():

    # 定义模板文件路径
    templates = {
        'method': os.path.join(base_dir, 'templates-cn/RTC/Method.dita'),
        'callback': os.path.join(base_dir, 'templates-cn/RTC/Callback.dita'),
        'enum': os.path.join(base_dir, 'templates-cn/RTC/Enum.dita'),
        'class': os.path.join(base_dir, 'templates-cn/RTC/Class.dita')
    }

    # 定义输出目录
    new_file_path = os.path.join(base_dir, 'RTC-NG/API')
    # 定义 relations 和 datatype 文件路径
    relations_path = os.path.join(base_dir, 'RTC-NG/config/relations-rtc-ng-api.ditamap')
    datatype_path = os.path.join(base_dir, 'RTC-NG/API/rtc_api_data_type.dita')

    # 检查并创建输出目录
    os.makedirs(new_file_path, exist_ok=True)

    # 读取 JSON 数据
    json_file_path = 'data.json'

    try:
        # 创建新的 DITA 文件
        create_dita_files(json_file_path, templates, platform_configs, new_file_path)

        process_all_ditamaps()
        parse_keysmaps()
        insert_relations(relations_path)
        insert_datatype(datatype_path)
        modify_dita_files()

        print("所有操作已完成")

    except Exception as e:
        print(f"执行过程中发生错误：{str(e)}")
        raise

if __name__ == "__main__":
    main()