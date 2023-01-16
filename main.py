#!/usr/bin/python3
import clang.cindex
from clang.cindex import Cursor, CursorKind

class CXXParser:
    def __init__(self, filename) -> None:
        index = clang.cindex.Index.create()
        self.tu = index.parse(filename, ['c++', '-std=c++11'])
    
    def parse_namespace(self, namespace) -> dict[str,clang.cindex.Cursor]:
        self.root = None
        self.struct_dict = {}
        self.root = self._get_cursor(self.tu, namespace)
        self._get_struct(self.root)
        return self.struct_dict

    def _get_cursor(self, source, spelling):
        root_cursor = source if isinstance(source, Cursor) else source.cursor
        for cursor in root_cursor.walk_preorder():
            if cursor.spelling == spelling:
                return cursor
        return None
    
    def _get_struct(self, cursor):
        for cur in cursor.get_children():
            if cur.kind is CursorKind.STRUCT_DECL:
                self.struct_dict[cur.spelling] = cur
            self._get_struct(cur)

class PBField:
    def __init__(self, type = "", name = "", attribute = "optional"):
        self.attribute = attribute
        self.set_type(type)
        self.set_name(name)
        pass

    def set_name(self, name):
        if len(name) > 2 and name[0:2] == "m_":
            self.name = name[2:]
            return
        self.name = name
    
    def set_type(self, type):
        if "int" in type:
            type = type.split('_')[0]
        type = type.split(':')[-1]
        self.type = type

    def set_repeated(self):
        self.attribute = "repeated"

class PBMessage:
    def __init__(self, cxx_struct : clang.cindex.Cursor) -> None:
        self.name = cxx_struct.spelling
        self.cxx_struct = cxx_struct
        self.sub_msg = {}

    def parse(self):
        print("[Struct] : parse ", self.name)
        self.field_list = []
        self.sub_msg_list = []
        for field in [i for i in self.cxx_struct.get_children() if i.kind in [CursorKind.FIELD_DECL, CursorKind.STRUCT_DECL]]:
            self._parse_field(field)
        pass

    def print(self):
        pb_data = "\nmessage " + self.name + "\n{\n"
        idx = 1
        for field in self.field_list:
            pb_data = pb_data + "    %s %s %s = %d;\n"%(field.attribute, field.type, field.name, idx)
            idx = idx + 1
        pb_data = pb_data + "}\n\n"
        return pb_data

    def get_submsg(self):
        return self.sub_msg

    def _parse_field(self, field : clang.cindex.Cursor):
        pb_field = PBField(field.type.spelling, field.spelling)
        field_type_list = [i.spelling for i in field.get_children() if i.kind in [CursorKind.FIELD_DECL, CursorKind.STRUCT_DECL, CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF]]
        if len(field_type_list) == 0: 
            self.field_list.append(pb_field)
            return
        self._parse_type_list(field_type_list, pb_field)
    
    def _parse_type_list(self, typelist, pb_field : PBField):
        typelist_size = len(typelist)
        print("[Field] parse {}::{} type {} ".format(self.name, pb_field.name, typelist))
        first_type = typelist[0]
        if first_type in ["vector", "list", "set", "queue", "stack", "unordered_set"]:
            if typelist_size != 2:
                print('[Field] {}::{} {} type error'.format(self.name, pb_field.name, typelist))
                return;
            pb_field.set_repeated()
            pb_field.set_type(typelist[1])
        elif first_type in ["map", "unorder_map"]:
            if typelist_size != 3:
                print('[Field] {}::{} {} type error'.format(self.name, pb_field.name, typelist))
                return;
            self.sub_msg[pb_field.name] = typelist[1:]
            return
        else: 
            pb_field.set_type(first_type)
        self.field_list.append(pb_field)
        print("%s %s %s"%(pb_field.attribute, pb_field.type, pb_field.name))

cxx_parser = CXXParser("test.cc")
struct_dict = cxx_parser.parse_namespace("pb_data")
pbfile = ""
for key in struct_dict:
    pbmessage = PBMessage(struct_dict[key])
    pbmessage.parse()
    pbfile += pbmessage.print()
print(pbfile)
    # print(pbmessage.get_submsg())
