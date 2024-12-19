from xml.dom import minidom

# List of XML files
xml_files = ['RTC_NG_API_iOS.ditamap', 'RTC_NG_API_Flutter.ditamap']

topic = input('Enter the toc under which the API is to be put:')
new_keyrefs = input('Enter the keys of the APIs to be added, separated by comma:').split(',')

# Loop over each XML file
for xml_file in xml_files:
    # Parse the XML files
    file = minidom.parse(xml_file)

    # Get all topicrefs
    elements = file.getElementsByTagName('topicref')

    # Get the href value and chunk value of tocs
    for elem in elements:
        href_attribute = elem.attributes.get('href')
        chunk_attribute = elem.attributes.get('chunk')
        # Skip the element if it does not has href and chunk attributes
        if not (href_attribute and chunk_attribute):
            continue
        # Locate the toc after which new APIs are to be added
        if href_attribute.value == topic and chunk_attribute.value == "to-content":
            # If the last child of the element is a text node containing only whitespace, remove it
            if elem.lastChild.nodeType == elem.TEXT_NODE and elem.lastChild.data.strip() == '':
                elem.removeChild(elem.lastChild)

            for new_keyref in new_keyrefs:
                # Create a new topicref
                new_topicref = file.createElement('topicref')
                # Set keyref and its value
                new_topicref.setAttribute('keyref', new_keyref.strip())
                # Set toc=no
                new_topicref.setAttribute('toc', 'no')

                # Create a text node for indentation and line break, so that newly-added topicrefs will not displayed in one line
                text_node = file.createTextNode('\n            ')

                # Add the new topicref and text node to the end of the children of the given toc
                lastChild = elem.lastChild
                if lastChild.nodeType == lastChild.TEXT_NODE:
                    lastChild.data = lastChild.data + text_node.data
                else:
                    elem.appendChild(text_node)
                elem.appendChild(new_topicref)

                print(f'{new_keyref} is successfully added!')

            # Add a new line after the last topicref
            elem.appendChild(file.createTextNode('\n        '))

            # Save the modified file
            with open(xml_file, 'w') as f:
                f.write(file.toxml())

            print(f"The file {xml_file} has been modified and saved")
            break
    else:
        print(f"{topic} not found in {xml_file}")