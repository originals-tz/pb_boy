#!/usr/bin/python3
import sys
import clang.cindex
from clang.cindex import Cursor, CursorKind, TypeKind
from clang.cindex import TranslationUnit

class CXXParser:
    def __init__(self, filename) -> None:
        index = clang.cindex.Index.create()
        self.tu = index.parse(filename, ['c++', '-std=c++11'])
    
    def get_struct_from_namespace(self, namespace) -> dict[str,clang.cindex.Cursor]:
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
        self.name = name
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

class PBMessage:
    def __init__(self, cxx_struct : clang.cindex.Cursor) -> None:
        self.name = cxx_struct.spelling
        field_list = [i for i in cxx_struct.get_children() if i.kind in [CursorKind.FIELD_DECL, CursorKind.STRUCT_DECL]]
        for field in field_list:
        pass

    def _parse_field(self, field):
        pb_field = PBField(field.type.spelling, field.spelling)
        field_type_list = [i.spelling for i in field.get_children() if i.kind in [CursorKind.FIELD_DECL, CursorKind.STRUCT_DECL, CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF]]


cxx_parser = CXXParser("test.cc")
struct_dict = cxx_parser.get_struct_from_namespace("pb_data")
