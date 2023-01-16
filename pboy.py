#!/usr/bin/python3
import sys
import clang.cindex
from clang.cindex import Cursor, CursorKind, TypeKind
from clang.cindex import TranslationUnit

class PBField:
    def __init__(self):
        self.attribute = "optional"
        self.type = ""
        self.name = ""
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

    def to_string(self):
        return " " .join([self.attribute, self.type, self.name])

class PBMessage:
    def __init__(self, name):
        self.name = name
        self.field_map = {}
        pass

    def add(self, field):
        self.field_map[field.name] = field
    
    def to_string(self):
        pb_data = "message " + self.name + "\n{\n"
        i = 1
        for key in self.field_map:
            pb_data = pb_data + "   " + self.field_map[key].to_string() + " = " + str(i) + ";\n"
            i = i + 1
        pb_data = pb_data + "}\n"
        return pb_data

class PBFile:
    def __init__(self):
        self.msg_map = {}
        pass

    def add (self, msg):
        self.msg_map[msg.name] = msg
    
    def to_string(self):
        pb_data = ""
        for key in self.msg_map:
            pb_data = pb_data + self.msg_map[key].to_string()
        return pb_data


class RepeatedNode:
    def __init__(self):
        self.mark = 1
        self.type = ""

class KVNode:
    def __init__(self):
        self.mark = 2
        self.key_type = ""

class RawNode:
    def __init__(self):
        self.mark = 3
        self.type = ""

def Handle(node_list, cur_msg, field_name):
    msg_list = []
    for i in range(len(node_list)):
        cur_field = PBField()
        if i == 0:
            cur_field.set_name(field_name)
        else:
            cur_field.set_name("data" + str(i))
        print("cur node name ============= ", cur_field.name)
        if node_list[i].mark == 1:
            cur_field.attribute = "repeated"
            next_node = node_list[i+1]
            if next_node.mark == 3:
                cur_field.set_type(next_node.type)
                cur_msg.add(cur_field)
                msg_list.append(cur_msg)
                return msg_list
            else:
                next_msg = PBMessage(cur_msg.name + "_" + cur_field.name)
                cur_field.type = next_msg.name
                cur_msg.add(cur_field)
                msg_list.append(cur_msg)
                cur_msg = next_msg
                continue
        if node_list[i].mark == 2:
            cur_field.attribute = "repeated"
            cur_msg.add(cur_field)
            msg_list.append(cur_msg)

            kv_msg = PBMessage(cur_msg.name + "_" + cur_field.name)
            cur_field.set_type(kv_msg.name)
            key_field = PBField()
            key_field.set_name("key")
            key_field.set_type(node_list[i].key_type)
            kv_msg.add(key_field)

            next_node = node_list[i+1]
            if next_node.mark == 3:
                value_field = PBField()
                value_field.set_name("value")
                value_field.set_type(next_node.type)
                kv_msg.add(value_field)
                msg_list.append(kv_msg)
                return msg_list
            else:
                value_field = PBField()
                value_field.set_name("value")
                value_field.attribute = "repeated"

                next_node = node_list[i+2]
                if next_node.mark == 3:
                    value_field.set_type(next_node.type)
                else:
                    next_msg = PBMessage(kv_msg.name + "_value")
                    value_field.type = next_msg.name
                    kv_msg.add(value_field)
                    msg_list.append(kv_msg)
                    cur_msg = next_msg
                    continue

                kv_msg.add(value_field)
                msg_list.append(kv_msg)
                return msg_list
    return msg_list

class Pboy:
    def __init__(self, filename):
        index = clang.cindex.Index.create()
        self.tu = index.parse(filename, ['c++', '-std=c++11'])
        self.root = None
        self.struct_list = []
        self.contrain = ["vector", "list", "stack", "queue", "set", "unordered_set"]
        self.kv_contrain = ["map", "unordered_map"]

    def to_pb(self, namespace):
        self.root = self.get_cursor(self.tu, namespace)
        self.get_struct()
        return self.struct_to_pb_msg()

    def get_cursor(self, source, spelling):
        root_cursor = source if isinstance(source, Cursor) else source.cursor
        for cursor in root_cursor.walk_preorder():
            if cursor.spelling == spelling:
                return cursor
        return None

    def parse_struct(self, cursor):
        for cur in cursor.get_children():
            if cur.kind is CursorKind.STRUCT_DECL:
                self.struct_list.append(cur)
            self.parse_struct(cur)

    def get_struct(self):
        self.parse_struct(self.root)
    
    def struct_to_pb_msg(self):
        pb_file = PBFile()
        for struct in self.struct_list:
            msg_list = self.parse_struct_memeber(struct)
            for msg in msg_list:
                #print(msg.to_string())
                pb_file.add(msg)
        return pb_file
    
    def parse_struct_memeber(self, struct):
        '''
            value_type := temp_type pod_type | pod_type
            map := key_type, value_type
            vect := value_type
        '''
        field_list = [i for i in struct.get_children() if i.kind in [CursorKind.FIELD_DECL, CursorKind.STRUCT_DECL]]
        print("field_list", len(field_list))
        pb_msg = PBMessage(struct.spelling)
        msg_dict = {}
        for field in field_list:
            pb_field = PBField()
            pb_field.set_name(field.spelling)
            pb_field.set_type(field.type.spelling)
            print(field.spelling,":", str(field.kind))
            field_type_list = [i.spelling for i in field.get_children() if i.kind in [CursorKind.FIELD_DECL, CursorKind.STRUCT_DECL, CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF]]
            print(field_type_list)
            if len(field_type_list) > 0:
                nodelist = self.parse_field_type(field_type_list)
                if len(nodelist) == 1 and nodelist[0].mark == 3:
                    pb_field.set_type(field_type_list[0])
                    pb_msg.add(pb_field)
                else:
                    msg_list = Handle(nodelist, pb_msg, field.spelling)
                    for item in msg_list:
                        msg_dict[item.name] = item
            else:
                pb_msg.add(pb_field)
                print("field : ", pb_field.to_string())
        msg_dict[pb_msg.name] = pb_msg
        return [msg_dict[key] for key in msg_dict]

    def parse_field_type(self, type_list):
        print("type_list = ", type_list)
        node_list = []
        data_list = []
        print(type_list)
        is_skip = False
        for i in range(len(type_list)):
            if is_skip == True:
                is_skip = False
                continue
            if type_list[i] in self.contrain:
                node = RepeatedNode()
                node.type = type_list[i]
                node_list.append(node)
                data_list.append(1)
            elif type_list[i] in self.kv_contrain:
                is_skip = True
                node = KVNode()
                i = i+1
                node.key_type = type_list[i]
                node_list.append(node)
                data_list.append(2)
            else:
                node = RawNode()
                node.type = type_list[i]
                node_list.append(node)
                data_list.append(3)
        print(data_list)
        return node_list


p = Pboy("test.cc")
print(p.to_pb("pb_data").to_string())
