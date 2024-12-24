encoding = 'utf-8'
from lxml import etree
import json
import os

def create_dita_file(template_path, new_file_path):
    """创建新的 dita 文件"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"模板文件内容前100个字符：{content[:100]}")
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            print(f"成功创建文件：{new_file_path}")
    except Exception as e:
        print(f"创建文件时出错：{str(e)}")

def get_platform_prop(platform, platform_configs):
    """根据平台获取对应的 platform3 值"""
    for config in platform_configs:
        if config['platform'] == platform:
            return config['platform3']
    return platform

def update_parameters_section(parameters_section, params_data, platform, platform_configs):
    """更新参数部分"""
    if not params_data or platform not in params_data:
        return
    
    platform_prop = get_platform_prop(platform, platform_configs)
    existing_params = {}
    
    # 找到 parml 元素
    parml = parameters_section.find('parml')
    if parml is None:
        parml = etree.SubElement(parameters_section, 'parml')
    else:
        # 清除模板中的空 plentry
        for empty_plentry in parml.findall('plentry'):
            if not empty_plentry.findall('pt') or not empty_plentry.findall('pd'):
                parml.remove(empty_plentry)
    
    # 添加换行和缩进
    parml.text = '\n            '  # parml 后的首次换行
    
    # 收集现有参数信息
    for plentry in parml.findall('plentry'):
        pts = plentry.findall('pt')
        for pt in pts:
            name = pt.text
            if name:  # 只处理非空参数名
                existing_params[name] = plentry
                
        # 为现有的 plentry 添加合适的缩进
        plentry.tail = '\n            '
        for elem in plentry:
            elem.tail = '\n                '
        # 最后一个元素的 tail 需要调整缩进级别
        if len(plentry) > 0:
            plentry[-1].tail = '\n            '
    
    # 处理新参数
    for param in params_data[platform]:
        if param['change_type'] != 'create':
            continue
            
        param_name = param['name']
        param_desc = param['desc']
        
        if param_name in existing_params:
            # 更新现有参数
            plentry = existing_params[param_name]
            pt_found = False
            pd_found = False
            
            for pt in plentry.findall('pt'):
                if pt.text == param_name:
                    props = pt.get('props', '').split()
                    if platform_prop not in props:
                        props.append(platform_prop)
                        pt.set('props', ' '.join(props))
                    pt_found = True
                    
            for pd in plentry.findall('pd'):
                if pd.text == param_desc:
                    props = pd.get('props', '').split()
                    if platform_prop not in props:
                        props.append(platform_prop)
                        pd.set('props', ' '.join(props))
                    pd_found = True
            
            if not pt_found:
                new_pt = etree.SubElement(plentry, 'pt')
                new_pt.text = param_name
                new_pt.set('props', platform_prop)
                new_pt.tail = '\n                '
                
            if not pd_found:
                new_pd = etree.SubElement(plentry, 'pd')
                new_pd.text = param_desc
                new_pd.set('props', platform_prop)
                new_pd.tail = '\n            '
        else:
            # 创建新参数
            plentry = etree.SubElement(parml, 'plentry')
            plentry.text = '\n                '
            plentry.tail = '\n            '
            
            pt = etree.SubElement(plentry, 'pt')
            pt.text = param_name
            pt.set('props', platform_prop)
            pt.tail = '\n                '
            
            pd = etree.SubElement(plentry, 'pd')
            pd.text = param_desc
            pd.set('props', platform_prop)
            pd.tail = '\n            '
            
            existing_params[param_name] = plentry
    
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
    # 使用 os.path.join 来构建完整的文件路径
    full_file_path = os.path.join(new_file_path, file_name)
    
    # 创建文件
    create_dita_file(template_path, full_file_path)
    
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
        if 'detailed_desc' in desc and isinstance(desc['detailed_desc'], list) and desc['detailed_desc']:
            dd = detailed_desc_section.find('.//dlentry/dd')
            if dd is not None and 'since' in desc['detailed_desc'][0]:
                dd.text = f"v{desc['detailed_desc'][0]['since']}"
        
        # 更新描述
        if 'detailed_desc' in desc and isinstance(desc['detailed_desc'], list) and desc['detailed_desc']:
            p = detailed_desc_section.find('p')
            if p is not None and 'desc' in desc['detailed_desc'][0]:
                p.text = desc['detailed_desc'][0]['desc']
    
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
    if 'parameters' in desc:
        parameters_section = root.find('.//section[@id="parameters"]')
        if parameters_section is not None:
            for platform in desc['parameters'].keys():
                update_parameters_section(parameters_section, desc['parameters'], platform, platform_configs)
    
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
            changes = json.loads(content)  # 使用 loads 而不是 load
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
    
    # 处理 API 变更
    if 'api_changes' in changes:
        for change in changes['api_changes']:
            process_api_change(change, templates, platform_configs, new_file_path)
    
    # TODO: 处理 struct_changes 和 enum_changes

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