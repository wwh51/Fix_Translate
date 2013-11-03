import xml
import os
import sys
import xml.etree.ElementTree as ET


fixdict = {}
fixdesc_dict = {}
tree = ET.parse('cxa.xml')
root = tree.getroot()
fieldsnode = root.find('fields')
field_list = fieldsnode.findall('field')
for fieldnode in field_list:
    number = fieldnode.attrib.get('number')
    name = fieldnode.attrib.get('name')
    #if number is not None and name is not None:
    if number and name:
        fixdict[number] = name
    value_list = fieldnode.findall('value')
    if value_list:
        dict_desc = {}
        for value_desc in value_list:
            v = value_desc.attrib.get('enum')
            d = value_desc.attrib.get('description')
            if v and d:
                dict_desc[v] = d
        fixdesc_dict[number] = dict_desc


with open('./fix.txt') as f:
    s = f.read()
s = s.split('\n')
for fields in s:
    if '=' in fields:
        f_key_value = fields.split('=', 1)
        key_num = f_key_value[0]
        fvalue = f_key_value[1]
        if key_num in fixdict.keys():
            print('Tag', fixdict[key_num], ':Value', fvalue)
            if key_num in fixdesc_dict.keys():
                dict_desc = fixdesc_dict[key_num]
                print('--------------', dict_desc[fvalue])
