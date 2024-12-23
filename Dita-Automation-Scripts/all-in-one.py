import os
import json
from lxml import etree
import shutil

# Unified platform configuration
platform_configs = [
    {
        'platform': 'android',
        'platform1': 'java',
        'platform2': 'Android',
        'platform3': 'android',
        'file': 'RTC_NG_API_Android.ditamap'
    },
    {
        'platform': 'ios',
        'platform1': 'ios',
        'platform2': 'iOS',
        'platform3': 'ios',
        'file': 'RTC_NG_API_iOS.ditamap'
    },
    {
        'platform': 'windows',
        'platform1': 'cpp',
        'platform2': 'CPP',
        'platform3': 'cpp',
        'file': 'RTC_NG_API_CPP.ditamap'
    },
    {
        'platform': 'macos',
        'platform1': 'macos',
        'platform2': 'macOS',
        'platform3': 'macos',
        'file': 'RTC_NG_API_macOS.ditamap'
    },
    {
        'platform': 'flutter',
        'platform1': 'flutter',
        'platform2': 'Flutter',
        'platform3': 'flutter',
        'file': 'RTC_NG_API_Flutter.ditamap'
    },
    {
        'platform': 'unity',
        'platform1': 'unity',
        'platform2': 'Unity',
        'platform3': 'unity',
        'file': 'RTC_NG_API_Unity.ditamap'
    },
    {
        'platform': 'electron',
        'platform1': 'electron',
        'platform2': 'Electron',
        'platform3': 'electron',
        'file': 'RTC_NG_API_Electron.ditamap'
    },
    {
        'platform': 'rn',
        'platform1': 'rn',
        'platform2': 'RN',
        'platform3': 'rn',
        'file': 'RTC_NG_API_RN.ditamap'
    },
    {
        'platform': 'unreal',
        'platform1': 'unreal',
        'platform2': 'Unreal',
        'platform3': 'unreal',
        'file': 'RTC_NG_API_Unreal.ditamap'
    },
    {
        'platform': 'cs',
        'platform1': 'cs',
        'platform2': 'CS',
        'platform3': 'cs',
        'file': 'RTC_NG_API_CS.ditamap'
    }
]

base_dir = '/Users/admin/Documents/python-script/Dita-Automation-Scripts/dita'

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

def initialize_platform_map():
    """Initialize platform API map."""
    return {config['platform']: [] for config in platform_configs}

def check_and_parse_file(file_path):
    """Check if a file exists and parse it."""
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return None
    return etree.parse(file_path)

def process_api_data(api_data, platform_map):
    """Process API data and categorize by platform."""
    platforms = api_data.get('platforms', [])
    if "all" in platforms:
        for platform in platform_map.keys():
            platform_map[platform].append(api_data)
    else:
        for platform in platforms:
            if platform in platform_map:
                platform_map[platform].append(api_data)

def parse_and_write_xml(file_path, process_function):
    """Parse an XML file, apply a processing function, and write changes."""
    tree = check_and_parse_file(file_path)
    if tree is None:
        return
    root = tree.getroot()
    changes_made = process_function(root)
    if changes_made > 0:
        print(f"Writing {changes_made} changes to {file_path}")
        tree.write(file_path, encoding='UTF-8', xml_declaration=True)
    else:
        print(f"No changes made to {file_path}")

def create_dita_files():
    """Create DITA files."""
    template_dir = os.path.join(base_dir, 'templates-cn', 'RTC')
    target_dir = os.path.join(base_dir, 'RTC-NG', 'API')
    os.makedirs(target_dir, exist_ok=True)

    for api_key, api_data in json_data.items():
        attributes = api_data.get('attributes', '')
        parentclass = api_data.get('parentclass', '').lower()
        key = api_data['key'].lower()

        if isinstance(attributes, dict) and attributes.get('type') == 'enum':
            template_file = os.path.join(template_dir, 'Enum.dita')
            output_filename = f'enum_{key}.dita'
        else:
            if attributes == 'api':
                template_file = os.path.join(template_dir, 'Method.dita')
                output_filename = f'api_{parentclass}_{key}.dita' if parentclass != 'none' else f'api_{key}.dita'
            elif attributes == 'enum':
                template_file = os.path.join(template_dir, 'Enum.dita')
                output_filename = f'enum_{key}.dita'
            elif attributes == 'class':
                template_file = os.path.join(template_dir, 'Class.dita')
                output_filename = f'class_{key}.dita'
            elif attributes == 'callback':
                template_file = os.path.join(template_dir, 'Callback.dita')
                output_filename = f'callback_{parentclass}_{key}.dita' if parentclass != 'none' else f'callback_{key}.dita'
            else:
                print(f"Warning: Unknown attributes type '{attributes}' for API {api_key}")
                continue

        output_path = os.path.join(target_dir, output_filename)
        if os.path.exists(output_path):
            print(f"Skipping existing file: {output_filename}")
            continue

        try:
            shutil.copy2(template_file, output_path)
            print(f"Created {output_filename}")
        except FileNotFoundError:
            print(f"Error: Template file not found: {template_file}")
        except Exception as e:
            print(f"Error creating {output_filename}: {str(e)}")

def parse_ditamap(root, platform_apis):
    """Process a single ditamap file."""
    changes_made = 0
    modified_parents = set()

    for api_data in platform_apis:
        if (api_data.get('attributes') == 'class' and api_data.get('navtitle') == 'Interface classes') or \
           api_data.get('attributes') == 'enum':
            continue

        target_href = api_data['toc_href']
        api_key = api_data['key']

        for topicref in root.iter('topicref'):
            if topicref.get('href') == target_href:
                current_indent = ''
                parent = topicref
                while parent is not None:
                    current_indent += '    '
                    parent = parent.getparent()

                topicref.tail = '\n' + current_indent

                new_topicref = etree.Element('topicref')
                new_topicref.set('keyref', api_key)
                new_topicref.set('toc', 'no')
                new_topicref.tail = '\n' + current_indent

                topicref.append(new_topicref)
                changes_made += 1
                modified_parents.add(topicref)

    for parent in modified_parents:
        children = list(parent)
        if children:
            children.sort(key=lambda x: x.get('keyref', '').lower())
            for i, child in enumerate(children):
                if i < len(children) - 1:
                    child.tail = '\n' + current_indent
                else:
                    child.tail = '\n' + current_indent[:-4]
                parent.append(child)

    return changes_made

def process_all_ditamaps():
    """Process all platform ditamap files."""
    platform_api_map = initialize_platform_map()
    for api_data in json_data.values():
        process_api_data(api_data, platform_api_map)

    for config in platform_configs:
        platform = config['platform']
        apis = platform_api_map[platform]
        ditamap_path = os.path.join(base_dir, 'RTC-NG', config['file'])
        parse_and_write_xml(ditamap_path, lambda root: parse_ditamap(root, apis))

def parse_keysmaps():
    """Process all platform keysmaps files."""
    platform_api_map = initialize_platform_map()
    for api_data in json_data.values():
        process_api_data(api_data, platform_api_map)

    keysmaps_dir = os.path.join(base_dir, 'RTC-NG', 'config')

    for config in platform_configs:
        platform = config['platform']
        keysmap_file = os.path.join(keysmaps_dir, f'keys-rtc-ng-api-{config["platform1"]}.ditamap')
        if not os.path.exists(keysmap_file):
            print(f"Warning: Keymap file not found: {keysmap_file}")
            continue

        print(f"\nProcessing keymap for platform: {platform}")

        if not platform_api_map[platform]:
            print(f"No APIs to process for platform {platform}")
            continue

        parse_and_write_xml(keysmap_file, lambda root: create_and_insert_keydef(root, platform_api_map[platform], platform))

def create_and_insert_keydef(root, platform_apis, platform):
    """Create and insert new keydef elements."""
    changes_made = 0
    base_indent = '    '

    for api_data in platform_apis:
        if isinstance(api_data.get('attributes'), dict) and api_data['attributes'].get('type') == 'enum':
            target_navtitle = api_data.get('navtitle')
            if not target_navtitle:
                continue

            enum_keydef = etree.Element('keydef')
            enum_keydef.set('keys', api_data['key'])
            enum_keydef.set('href', f"../API/enum_{api_data['key'].lower()}.dita")
            enum_keydef.text = '\n' + base_indent + '    '
            enum_keydef.tail = '\n' + base_indent

            topicmeta = etree.SubElement(enum_keydef, 'topicmeta')
            topicmeta.text = '\n' + base_indent + '        '
            topicmeta.tail = '\n' + base_indent + '    '

            keywords = etree.SubElement(topicmeta, 'keywords')
            keywords.text = '\n' + base_indent + '            '
            keywords.tail = '\n' + base_indent + '        '

            keyword_value = api_data['keyword'] if isinstance(api_data['keyword'], str) else api_data['keyword'].get(platform, api_data['key'])
            keyword = etree.SubElement(keywords, 'keyword')
            keyword.text = keyword_value
            keyword.tail = '\n' + base_indent + '        '

            for topichead in root.iter('topichead'):
                if topichead.get('navtitle') == target_navtitle:
                    topichead.append(enum_keydef)
                    changes_made += 1

                    if platform in api_data['attributes']['enumerations'][0]:
                        enums = api_data['attributes']['enumerations'][0][platform]
                        for enum in enums:
                            for alias, value in enum.items():
                                if any(existing_keydef.get('keys') == alias for existing_keydef in topichead.findall('keydef')):
                                    continue

                                enum_value_keydef = etree.Element('keydef')
                                enum_value_keydef.set('keys', alias)
                                enum_value_keydef.text = '\n' + base_indent + '    '
                                enum_value_keydef.tail = '\n' + base_indent

                                topicmeta = etree.SubElement(enum_value_keydef, 'topicmeta')
                                topicmeta.text = '\n' + base_indent + '        '
                                topicmeta.tail = '\n' + base_indent + '    '

                                keywords = etree.SubElement(topicmeta, 'keywords')
                                keywords.text = '\n' + base_indent + '            '
                                keywords.tail = '\n' + base_indent + '        '

                                keyword = etree.SubElement(keywords, 'keyword')
                                keyword.text = value
                                keyword.tail = '\n' + base_indent + '        '

                                topichead.append(enum_value_keydef)
                                changes_made += 1

    return changes_made

def insert_relations(relations_path):
    """Process relations file and insert API relations."""
    print(f"\nProcessing relations file: {relations_path}")
    tree = check_and_parse_file(relations_path)
    if tree is None:
        return
    root = tree.getroot()
    changes_made = 0

    platform_map = {config['platform']: config['platform1'] for config in platform_configs}

    for api_key, api_data in json_data.items():
        if api_data.get('attributes') not in ['api', 'callback']:
            continue

        key = api_data['key']
        parentclass = api_data.get('parentclass')
        platforms = api_data.get('platforms', [])

        props = [platform_map[platform] for platform in platforms if platform in platform_map]

        if not props or not parentclass:
            continue

        props_str = ' '.join(props)

        for relrow in root.findall('.//relrow'):
            found = False
            has_props = False
            target_cell = None

            for relcell in relrow.findall('relcell'):
                for topicref in relcell.findall('topicref'):
                    if topicref.get('keyref') == parentclass:
                        for ancestor in topicref.iterancestors():
                            if ancestor.get('props') is not None:
                                has_props = True
                                break

                        if has_props:
                            break

                        target_cell = relrow.findall('relcell')[0]
                        found = True
                        break
                if found or has_props:
                    break

            if found and target_cell is not None and not has_props:
                exists = any(existing_topicref.get('keyref') == key for existing_topicref in target_cell.findall('topicref'))

                if not exists:
                    new_topicref = etree.Element('topicref')
                    new_topicref.set('keyref', key)
                    new_topicref.set('props', props_str)

                    current_indent = ''
                    parent = target_cell
                    while parent is not None:
                        current_indent += '    '
                        parent = parent.getparent()

                    new_topicref.tail = '\n' + current_indent

                    target_cell.append(new_topicref)
                    changes_made += 1

                    topicrefs = target_cell.findall('topicref')
                    sorted_topicrefs = sorted(topicrefs, key=lambda x: x.get('keyref', ''))

                    for child in list(target_cell):
                        target_cell.remove(child)

                    for i, topicref in enumerate(sorted_topicrefs):
                        if i < len(sorted_topicrefs) - 1:
                            topicref.tail = '\n' + current_indent
                        else:
                            topicref.tail = '\n' + current_indent[:-4]
                        target_cell.append(topicref)

    if changes_made > 0:
        print(f"Writing {changes_made} changes to {relations_path}")
        tree.write(relations_path, encoding='UTF-8', xml_declaration=True)
    else:
        print(f"No changes made to {relations_path}")

def insert_datatype(datatype_path):
    """Process datatype file and insert class and enum references."""
    print(f"\nProcessing datatype file: {datatype_path}")
    tree = check_and_parse_file(datatype_path)
    if tree is None:
        return
    root = tree.getroot()
    changes_made = 0

    platform_map = {config['platform']: config['platform3'] for config in platform_configs}

    for api_key, api_data in json_data.items():
        attributes = api_data.get('attributes')
        if attributes not in ['class', 'enum']:
            continue

        platforms = api_data.get('platforms', [])
        props = [platform_map[platform] for platform in platforms if platform in platform_map]

        if not props:
            continue

        section = root.find(f".//section[@id='{attributes}']")
        if section is None:
            print(f"Warning: No section found for id='{attributes}'")
            continue

        changes_in_api = 0

        for prop in props:
            ul = section.find(f"ul[@props='{prop}']")
            if ul is None:
                ul = etree.SubElement(section, 'ul')
                ul.set('props', prop)
                ul.tail = '\n            '

            exists = any(li.find('xref').get('keyref') == api_data['key'] for li in ul.findall('li'))

            if not exists:
                new_li = etree.SubElement(ul, 'li')
                new_xref = etree.SubElement(new_li, 'xref')
                new_xref.set('keyref', api_data['key'])
                new_li.tail = '\n            '

                changes_in_api += 1

                lis = ul.findall('li')
                sorted_lis = sorted(lis, key=lambda x: x.find('xref').get('keyref', ''))

                for child in list(ul):
                    ul.remove(child)

                for i, li in enumerate(sorted_lis):
                    if i < len(sorted_lis) - 1:
                        li.tail = '\n            '
                    else:
                        li.tail = '\n        '
                    ul.append(li)

        changes_made += changes_in_api

    if changes_made > 0:
        print(f"Total {changes_made} changes added to {datatype_path}")
        tree.write(datatype_path, encoding='UTF-8', xml_declaration=True)
    else:
        print(f"No changes made to {datatype_path}")

def main():
    create_dita_files()
    process_all_ditamaps()
    parse_keysmaps()
    relations_path = '/Users/admin/Documents/python-script/Dita-Automation-Scripts/dita/RTC-NG/config/relations-rtc-ng-api.ditamap'
    datatype_path = '/Users/admin/Documents/python-script/Dita-Automation-Scripts/dita/RTC-NG/API/rtc_api_data_type.dita'
    insert_relations(relations_path)
    insert_datatype(datatype_path)

if __name__ == "__main__":
    main()