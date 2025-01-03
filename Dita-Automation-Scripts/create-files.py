encoding = 'utf-8'
from lxml import etree
import json
import os

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

def process_api_change(change_item, templates, platform_configs):
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
                print(f"已更新 {platform} 平台的 API 原型")
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
        update_parameters_section(parameters_section, platform_configs, change_item['description']['dita_params'])
    
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
                    li.tail = '\n                '  # 与前面的 li 对齐
                
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

def process_enum_change(change_item, templates, platform_configs):
    """处理单个枚举变更"""
    if change_item['change_type'] != 'create':
        return
        
    # 处理文件名：删除连字符并转换为小写
    enum_key = change_item['key'].replace('_', '').lower()
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
        
        if 'detailed_desc' in desc:
            dd = detailed_desc_section.find('.//dlentry/dd')
            if dd is not None and 'since' in desc['detailed_desc']:
                dd.text = f"v{desc['detailed_desc']['since']}"
            
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

def process_class_change(change_item, templates, platform_configs):
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
        
        if 'detailed_desc' in desc:
            dd = detailed_desc_section.find('.//dlentry/dd')
            if dd is not None and 'since' in desc['detailed_desc']:
                dd.text = f"v{desc['detailed_desc']['since']}"
            
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
        update_parameters_section(parameters_section, platform_configs, change_item['description']['dita_params'])
    
    # 保存更新后的文件
    tree.write(full_file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

def main(platform_configs, new_file_path):
    """主函数"""
    json_file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    print(f"尝试读取文件：{json_file_path}")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容前100个字符：{content[:100]}")
            changes = json.loads(content)
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"错误：JSON 文件格式不正确: {str(e)}")
        print(f"错误位置附近的内容：{content[max(0, e.pos-50):e.pos+50]}")
        return
    
    templates = {
        'method': method_template,
        'callback': callback_template,
        'enum': enum_template,
        'class': class_template
    }
    
    # 处理所有类型的变更
    if 'api_changes' in changes:
        print("\n开始处理 API 变更...")
        for change in changes['api_changes']:
            try:
                process_api_change(change, templates, platform_configs)
            except Exception as e:
                print(f"处理 API {change.get('key', '未知')} 时出错：{str(e)}")
    
    if 'enum_changes' in changes:
        print("\n开始处理枚举变更...")
        for change in changes['enum_changes']:
            try:
                process_enum_change(change, templates, platform_configs)
            except Exception as e:
                print(f"处理枚举 {change.get('key', '未知')} 时出错：{str(e)}")
    
    if 'struct_changes' in changes:
        print("\n开始处理类变更...")
        for change in changes['struct_changes']:
            try:
                process_class_change(change, templates, platform_configs)
            except Exception as e:
                print(f"处理类 {change.get('key', '未知')} 时出错：{str(e)}")

# 添加到主程序中的调用
if __name__ == "__main__":
    method_template = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/dita/templates-cn/RTC/Method.dita'
    callback_template = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/dita/templates-cn/RTC/Callback.dita'
    enum_template = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/dita/templates-cn/RTC/Enum.dita'
    class_template = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/dita/templates-cn/RTC/Class.dita'
    new_file_path = 'E:/AgoraTWrepo/python-script/Dita-Automation-Scripts/dita/RTC-NG/API'
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
    # 确保目标目录存在
    os.makedirs(new_file_path, exist_ok=True)
    main(platform_configs, new_file_path)