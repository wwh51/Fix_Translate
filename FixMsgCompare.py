import xml
import os
import re
import sys
import fnmatch
from tkinter import *
from tkinter.constants import *
import xml.etree.ElementTree as ET


class FixCompare:
    ignore_fields = ['8', '9', '34', '10']
    text_width = 70
    XMLDictFiles = []
    DefaultDest = 'CXA'

    def __init__(self, root):
        left_frame = Frame(root)
        right_frame = Frame(root)
        rt_frame = Frame(right_frame)
        rb_frame = Frame(right_frame)
        self.text_raw1 = Text(rt_frame, height=30, width=self.text_width,
                                       background='white')
        self.text_raw2 = Text(rt_frame, height=30, width=self.text_width,
                                        background='white')
        self.text_raw1.pack(side=LEFT)
        self.text_raw2.pack(side=RIGHT)
        self.text_raw1.bind("<KeyRelease>", self.EditUpdated)
        self.text_raw2.bind("<KeyRelease>", self.EditUpdated)

        self.text_result = Text(rb_frame, height=30, width=self.text_width*2,
                                    background='white')
        scroll = Scrollbar(rb_frame)
        self.text_result.configure(yscrollcommand=scroll.set)
        self.text_result.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)
        rt_frame.pack(side=TOP, fill=BOTH, expand=True)
        rb_frame.pack(side=BOTTOM, fill=BOTH, expand=True)

        self.MarketOption = IntVar()
        radiolist = []
        for file in os.listdir(sys.path[0]):
            radio_text = ''
            if fnmatch.fnmatch(file, '*.xml'):
                if 'DataDictionary.xml' in file:
                    radio_text = file[:-len('DataDictionary.xml')]
                else:
                    radio_text = file[:-len('.xml')]
                self.XMLDictFiles.append(file)
                radiolist.append(Radiobutton(left_frame, text=radio_text, variable=self.MarketOption,
                    value=len(radiolist), command=self.OnRadioSelected))
                radiolist[-1].pack(anchor=W, side=TOP)
                if radio_text == self.DefaultDest:
                    radiolist[-1].select()

        label = Label(left_frame, text="ignore fields")
        label.pack(anchor=W)
        self.textIgnoreList = Text(left_frame, height=1,
                                            width=20, background='white')
        self.textIgnoreList.insert(END, ','.join(self.ignore_fields))
        self.textIgnoreList.pack(anchor=W, side=TOP)
        self.textIgnoreList.bind("<KeyRelease>", self.EditUpdated)

        left_frame.pack(side=LEFT)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        self.LoadSpecDictionary()
        return

    def OnRadioSelected(self):
        self.LoadSpecDictionary()
        self.DoComparing()

    def EditUpdated(self, event):
        txtignore = self.textIgnoreList.get('1.0', END)
        txtignore = txtignore.rstrip('\n')
        self.ignore_fields = txtignore.split(',')
        self.DoComparing()

    def DoComparing(self):
        '''
        the main function
        '''
        msg = self.text_raw1.get('1.0', END)
        msg2 = self.text_raw2.get('1.0', END)
        s1 = re.split('\n|\t|\||\001| ', msg)
        s2 = re.split('\n|\t|\||\001| ', msg2)
        list_field1 = [(f[:f.index('=')].strip(), f[f.index('=')+1:].strip())
                            for f in s1
                            if '=' in f
                                and f[:f.index('=')].isnumeric()
                                and f[:f.index('=')] not in self.ignore_fields ]
        list_field2 = [(f[:f.index('=')].strip(), f[f.index('=')+1:].strip())
            for f in s2
                if '=' in f
                and f[:f.index('=')].isnumeric()
                and f[:f.index('=')] not in self.ignore_fields
                ]
        list_field2_key = [f[0] for f in list_field2]
        msg2_empty = not list_field2

        if not self.TagNumDict:
            return

        diff_rows = []
        diff_rows_count = 0
        rows_index = 0
        msg_result = ''
        for fields in list_field1:
            newline = ''
            f_key = fields[0]
            f_value = fields[1]
            key_desc = ''
            f_value2 = ''
            if f_key in list_field2_key:
                idx_key = list_field2_key.index(f_key)
                f_value2 = list_field2[idx_key][1]
                # for tag group
                list_field2_key.pop(idx_key)
                list_field2.pop(idx_key)

            if f_value2 != f_value:
                diff_rows.append(rows_index)
            rows_index += 1

            if f_key in self.TagNumDict.keys():
                key_desc = self.TagNumDict[f_key]
                if f_key in self.TagValueDict.keys():
                    if f_value in self.TagValueDict[f_key].keys():
                        f_value += '(%s)' % self.TagValueDict[f_key][f_value]
                    if f_value2 in self.TagValueDict[f_key].keys():
                        f_value2 += '(%s)' % self.TagValueDict[f_key][f_value2]

            newline = '{:>5}'.format(f_key) + '{:>20}'.format(key_desc) + '{:>50}'.format(f_value) + '{:>50}'.format(f_value2)
            msg_result += newline + '\n'

        for i in range(len(list_field2)):
            f_key = list_field2[i][0]
            f_value = ''
            f_value2 = list_field2[i][1]
            key_desc = ''
            if f_key in self.TagNumDict.keys():
                key_desc = self.TagNumDict[f_key]
            if f_key in self.TagValueDict.keys():
                if f_value2 in self.TagValueDict[f_key].keys():
                    f_value2 += '(%s)' % self.TagValueDict[f_key][f_value2]
            newline = '{:>5}'.format(f_key) + '{:>20}'.format(key_desc) + '{:>50}'.format(f_value) + '{:>50}'.format(f_value2)
            msg_result += newline + '\n'
            diff_rows.append(rows_index)
            rows_index += 1

        self.text_result.delete('0.0',END)
        self.text_result.insert(END, msg_result)

        for i in range(rows_index):
            tag_name = 'r%d' % i
            self.text_result.tag_add(tag_name, '%d.0' % (i+1), '%d.0' % (i+2) )
            self.text_result.tag_config(tag_name, background= i% 2 != 0  and "white" or "grey")
            if  i in diff_rows and not msg2_empty:
                 self.text_result.tag_config(tag_name, background= "green")

    def LoadSpecDictionary(self):
        self.TagNumDict = {}
        self.TagValueDict = {}
        xmlfile = os.path.join(sys.path[0], self.XMLDictFiles[self.MarketOption.get()])
        if not os.path.exists(xmlfile):
            return False

        tree = ET.parse(xmlfile)
        root = tree.getroot()
        fieldsnode = root.find('fields')
        field_list = fieldsnode.findall('field')
        for fieldnode in field_list:
            number = fieldnode.attrib.get('number')
            name = fieldnode.attrib.get('name')
            if number and name:
                self.TagNumDict[number] = name
            value_list = fieldnode.findall('value')
            if value_list:
                dict_desc = {}
                for value_desc in value_list:
                    v = value_desc.attrib.get('enum')
                    d = value_desc.attrib.get('description')
                    if v and d:
                        dict_desc[v] = d
                self.TagValueDict[number] = dict_desc
        return True


def main():
    root = Tk()
    fc = FixCompare(root)
    root.title('Fix Comparing')
    root.mainloop()
main()
