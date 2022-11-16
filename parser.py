#!usr/bin/env python
#coding:utf-8

from loguru import logger
import sys 
import struct
import binascii
import json

#define JAVA_8_VERSION                    52
#define JAVA_7_VERSION                    51

ACC_PUBLIC = 0x0001
ACC_PRIVATE = 0x0002
ACC_PROTECTED = 0x0004
ACC_STATIC = 0x0008
ACC_FINAL = 0x0010
ACC_SUPER = 0x0020
ACC_VOLATILE = 0x0040
ACC_INTERFACE = 0x0200
ACC_ABSTRACT = 0x0400
ACC_SYNTHETIC = 0x1000
ACC_ANNOTATION = 0x2000
ACC_ENUM = 0x4000
flag_dict = {ACC_PUBLIC: "PUBLIC", ACC_PRIVATE: "PRIVATE", ACC_STATIC: "STATIC", ACC_PROTECTED: "PROTECTED", ACC_FINAL: "FINAL", ACC_SUPER: "SUPER", 
            ACC_INTERFACE: "INTERFACE", ACC_ABSTRACT: "ABSTRACT", ACC_SYNTHETIC: "SYNTHETIC",
            ACC_ANNOTATION: "ANNOTATION", ACC_ENUM: "ENUM"}

TAG_Utf8_Info = 1
TAG_Integer_Info = 3
TAG_Float_Info = 4
TAG_Long_Info = 5
TAG_Double_Info = 6
TAG_Class_Info = 7
TAG_String_Info = 8
TAG_Fieldref_Info = 9
TAG_Methodref_Info = 10
TAG_Interface_MethodRef_Info = 11
TAG_NameAndType_Info = 12

tag_dict = {TAG_Utf8_Info: "Utf8_Info", TAG_Integer_Info: "Integer_Info", TAG_Float_Info: "Float_Info", 
            TAG_Long_Info: "Long_Info", TAG_Double_Info: "Double_Info", TAG_Class_Info: "Class_Info",
            TAG_String_Info: "String_Info", TAG_Fieldref_Info: "Fieldref_Info", TAG_Methodref_Info: "Methodref_Info",
            TAG_Interface_MethodRef_Info: "Interface_MethodRef_Info", TAG_NameAndType_Info: "NameAndType_Info"
            }

class FieldInfo(object):
    def __init__(self, idx, name, desc):
        self.index = idx
        self.name = name
        self.desc = desc
        ...
        
class JClass(object):
    
    def __init__(self):
        self.version = None
        self.this_class = None
        self.super_class = None
        self.access_flag = 0
        self.field_infos = []
        self.const_pool = None
    
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    ...

class ConstantPool(object):
    
    def __init__(self):
        self.data_dict = {}
    
    def add_constant_info(self, idx, value):
        self.data_dict[idx] = value
        
    def get_constant_info(self, idx):
        return self.data_dict[idx]
    
    def size(self):
        return len(self.data_dict)
    
    def __str__(self):
        return ""
        # return json.dumps(self.data_dict.keys())

class Utf8Info(object):
    len = 0
    data = None
    def __init__(self, len, data):
        self.len = len
        self.data = data
    @property
    def get_data(self):
        return self.data

class ClassFileParser(object):
    ...
    
    def parse(self, file):
        content = None
        with open(file, 'rb') as f:
            content = f.read()
        logger.info("content type {} file len {}", type(content), len(content))
        self._content = content
        self._position = 0
        return self.parse0()
    
    def parse0(self):
        self.jclass = JClass()
        self.check_magic_version()
        # parse class file
        self.read_const_pool()
        # read access_flags
        self.read_access_flags()
        # read class info
        self.read_class_info()
        # read interface info
        self.read_interface_info()
        # read field info
        self.read_field_info()
        # read method info
        self.read_method_info()
        # read attribue info
        self.read_attribute_info()
        return self.jclass
    
    def get_bytes(self, start, end):
        return self._content[start : end]
    
    def increment_position(self, inc_len):
        self._position += inc_len
        return self._position
        
    def check_magic_version(self):
        start = self._position
        end = start + 4
        magic_number, = struct.unpack("!L", self.get_bytes(start, end))
        logger.info("magic number {} hex value {}", type(magic_number), hex(magic_number))
        if hex(magic_number) != '0xcafebabe':
            raise "Class format error"
        
        minor_version, = struct.unpack("!H", self.get_bytes(end, end + 2))
        major_version, = struct.unpack("!H", self.get_bytes(end+2, end + 4))
        logger.info("minor version {}, major_version {}", minor_version, major_version)
        self.jclass.version = major_version
        # read magic done, should increate position
        self.increment_position(8)
        
        
    def read_const_pool(self):
        start = self._position
        const_pool_size, = struct.unpack("!H", self.get_bytes(start, start + 2))
        const_pool_size = const_pool_size - 1 
        logger.info("const pool size {}", const_pool_size)
        const_pool = ConstantPool()
        
        start = self.increment_position(2);
        for i in range(const_pool_size):
            tag, = struct.unpack("!B", self.get_bytes(start, start + 1))
            logger.info("tag {}", tag_dict[tag])
            start = self.increment_position(1);
            if tag == TAG_Methodref_Info or tag == TAG_NameAndType_Info or tag == TAG_Fieldref_Info:
                class_index, name_and_type_index = struct.unpack("!HH", self.get_bytes(start, start + 4))
                logger.info("idx {} class idx {}, name_and_type_index {}", i+1, class_index, name_and_type_index);
                const_pool.add_constant_info(i+1, (tag, class_index, name_and_type_index))
                start = self.increment_position(4);
            elif tag == TAG_String_Info:
                string_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
                start = self.increment_position(2);
                logger.info("idx {} string_idx {}", i + 1, string_idx);
                const_pool.add_constant_info(i+1, (tag, string_idx))
            elif tag == TAG_Class_Info:
                string_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
                start = self.increment_position(2);
                logger.info("idx {} class info idx {}", i + 1, string_idx);
                const_pool.add_constant_info(i+1, (tag, string_idx))
            elif tag == TAG_Utf8_Info:
                length, =struct.unpack("!H", self.get_bytes(start, start + 2))
                start = self.increment_position(2);
                data, = struct.unpack('{length}s'.format(length=length), self.get_bytes(start, start + length))
                logger.info("read utf8 string len {} data {}", length, data)
                start = self.increment_position(length);
                const_pool.add_constant_info(i+1, (tag, data))
            else:
                logger.info("ignore tag {}", tag)
                # todo implement
                ...
        self.const_pool = const_pool
        # self.jclass.const_pool = const_pool
        logger.info("after read const pool current position {}", self._position)
    
    def read_access_flags(self):
        start = self._position
        access_flag, = struct.unpack("!H", self.get_bytes(start, start + 2))
        logger.info("access flag {} desc {}", access_flag, self.get_access_flag_desc(access_flag))
        start = self.increment_position(2)
        self.jclass.access_flag = access_flag
        return access_flag
    
    def read_class_info(self):
        start = self._position
        this_class_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
        this_string_info = self.get_const_pool_string(this_class_idx)
        logger.info("this class idx {} name {}", this_class_idx, this_string_info)
        start = self.increment_position(2)
        
        super_class_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
        super_string_info = self.get_const_pool_string(super_class_idx)
        logger.info("parent class idx {} name {}", super_class_idx, super_string_info)
        start = self.increment_position(2)
        self.jclass.this_class = this_string_info
        self.jclass.super_class = super_string_info

    def get_access_flag_desc(self, access_flag):
        desc = []
        for flag in flag_dict.keys():
            if (flag & access_flag) == flag:
                desc.append(flag_dict[flag])
            
        return ', '.join(desc)
     
    def read_interface_info(self):
        start = self._position
        interface_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
        start = self.increment_position(2)
        logger.info("interface count {}", interface_cnt)  
    
    def get_const_pool_string(self, idx):
        class_constat = self.const_pool.get_constant_info(idx)
        # logger.info("idx {}, const {}", idx, class_constat)
        if class_constat[0] == TAG_Utf8_Info:
            return class_constat[1].decode("utf-8") 
        else :
            utf8_info = self.const_pool.get_constant_info(class_constat[1])
            assert utf8_info[0] == TAG_Utf8_Info
            return utf8_info[1].decode("utf-8") 
         
    def read_field_info(self):
        start = self._position
        field_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
        start = self.increment_position(2)
        logger.info("field count {}", field_cnt)
        field_infos = []
        for idx in range(field_cnt):
            self.read_access_flags()
            start = self._position
            name_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
            start = self.increment_position(2)
            desc_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
            logger.info("idx {} field name {}, field desc {}", idx, self.get_const_pool_string(name_idx), self.get_const_pool_string(desc_idx))
            start = self.increment_position(2)
            attribute_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
            logger.info("idx {} attribute cnt {}", idx, attribute_cnt)
            start = self.increment_position(2)
            field_infos.append(FieldInfo(idx, self.get_const_pool_string(name_idx), self.get_const_pool_string(desc_idx)))
            ...

        self.jclass.field_infos = field_infos
        logger.info("after read field info position {}", self._position)
        
    def read_method_info(self):
        start = self._position
        method_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
        start = self.increment_position(2)
        logger.info("method count {}", method_cnt)
        method_infos = []
        for idx in range(method_cnt):
            self.read_access_flags()
            start = self._position
            name_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
            start = self.increment_position(2)
            desc_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
            logger.info("idx {} method name {}, method desc {}", idx, self.get_const_pool_string(name_idx), self.get_const_pool_string(desc_idx))
            start = self.increment_position(2)
            attribute_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
            logger.info("idx {} attribute cnt {}", idx, attribute_cnt)
            start = self.increment_position(2)
            if attribute_cnt > 0:
                # start read attribute info
                for attr_idx in range(attribute_cnt):
                    attribute_type , = struct.unpack("!H", self.get_bytes(start, start + 2))
                    start = self.increment_position(2)
                    attribute_name = self.get_const_pool_string(attribute_type)
                    logger.info("idx {} , attribute_type {} value {}", idx, attribute_type, attribute_name)
                    
                    if attribute_name == 'Code':
                        # parse code attribute , 4 bytes length
                        attribute_len , = struct.unpack("!I", self.get_bytes(start, start + 4))
                        start = self.increment_position(4)
                        max_stack, = struct.unpack("!H", self.get_bytes(start, start + 2))
                        start = self.increment_position(2)
                        max_locals, = struct.unpack("!H", self.get_bytes(start, start + 2))
                        start = self.increment_position(2)
                        code_len , = struct.unpack("!I", self.get_bytes(start, start + 4))
                        start = self.increment_position(4)
                        
                        code, = struct.unpack('{length}s'.format(length=code_len), self.get_bytes(start, start + code_len))
                        start = self.increment_position(code_len)
                        logger.info("attribute_name {}, attribute_len {}, max_stack {}, max_locals {}, code_len {}, code {}", 
                                    attribute_name, attribute_len, max_stack, max_locals, code_len, code)
                        exception_table_len, = struct.unpack("!H", self.get_bytes(start, start + 2))
                        start = self.increment_position(2)
                        if exception_table_len > 0:
                            # todo read exception info
                            ...
                        
                        attributes_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
                        start = self.increment_position(2)
                        logger.info("exception_table_len {}, attributes_cnt {}", exception_table_len, attributes_cnt)
                        if attributes_cnt > 0:
                            # todo read attributes
                            for atr_idx in range(attributes_cnt):
                                attribute_name_idx , = struct.unpack("!H", self.get_bytes(start, start + 2))
                                attribute_name = self.get_const_pool_string(attribute_name_idx)
                                start = self.increment_position(2)
                                logger.info("attributes_idx {}, attribute_name {}", atr_idx, attribute_name)
                                # read line number table
                                if attribute_name == 'LineNumberTable':
                                    attribute_len, = struct.unpack("!I", self.get_bytes(start, start + 4))
                                    start = self.increment_position(4)
                                    line_num_len, = struct.unpack("!H", self.get_bytes(start, start + 2))
                                    start = self.increment_position(2)
                                    logger.info("line num length {}", line_num_len)
                                    for i in range(line_num_len):
                                        start_pc, = struct.unpack("!H", self.get_bytes(start, start + 2))
                                        start = self.increment_position(2)
                                        line_num, = struct.unpack("!H", self.get_bytes(start, start + 2))
                                        start = self.increment_position(2)
                                        logger.info("line num: {}, start_pc {}", line_num, start_pc)
                                else:
                                    logger.warning("unkonw attribute name {}", attribute_name)
                                ...
                            ...
                        ...
                    else:
                        logger.warning("unkonw attribute name {}", attribute_name)
                ...
            ...
        
        logger.info("after read method info position {}", self._position)

        
    def read_attribute_info(self):
        start = self._position
        attr_cnt, = struct.unpack("!H", self.get_bytes(start, start + 2))
        start = self.increment_position(2)
        logger.info("attr count {}", attr_cnt)
        for i in range(attr_cnt):
            attribute_name_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
            start = self.increment_position(2)
            attribute_name = self.get_const_pool_string(attribute_name_idx)
            logger.info("attributes_idx {}, attribute_name {}", attribute_name_idx, attribute_name)
            if attribute_name == 'SourceFile':
                attribute_len, = struct.unpack("!I", self.get_bytes(start, start + 4))
                logger.info("attribute_len {}", attribute_len)
                start = self.increment_position(4)
                sourcefile_idx, = struct.unpack("!H", self.get_bytes(start, start + 2))
                start = self.increment_position(2)
                logger.info("sourcefile_idx {} source file name {}", sourcefile_idx, self.get_const_pool_string(sourcefile_idx))
                
        logger.info("after read attribute info position {}", self._position)
        
if __name__ == '__main__':
    parser = ClassFileParser()
    logger.info("args {}", sys.argv)
    jclass = parser.parse(sys.argv[1])
    logger.info("read jclass is {}", jclass)