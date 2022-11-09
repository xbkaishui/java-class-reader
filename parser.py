#!usr/bin/env python
#coding:utf-8

from loguru import logger
import sys 
import struct
import binascii
import json

#define JAVA_8_VERSION                    52
#define JAVA_7_VERSION                    51


class JClass(object):
    
    def __init__(self):
        self.version = None
    
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    ...

class ConstantPool(object):
    
    data_dict = {}
    
    def add_constant_info(self, idx, value):
        self.data_dict[idx] = value
        
    def get_string(self, idx):
        return self.data_dict[idx]
    
    def size(self):
        return len(self.data_dict)
    
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

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
            logger.info("tag {}", tag)
            start = self.increment_position(1);
            if tag == 10 or tag == 12 or tag == 9:
                class_index, name_and_type_index = struct.unpack("!HH", self.get_bytes(start, start + 4))
                logger.info("idx {} class idx {}, name_and_type_index {}", i+1, class_index, name_and_type_index);
                const_pool.add_constant_info(i+1, (tag, class_index, name_and_type_index))
                ...
            elif tag == 8:
                ...
            elif tag == 7:
                ...
            elif tag == 1:
                ...
            start = self.increment_position(4);
            ...
        
        ...
        
    def read_methods(self):
        ...
        
    def read_table(self):
        ...
        
if __name__ == '__main__':
    parser = ClassFileParser()
    logger.info("args {}", sys.argv)
    jclass = parser.parse(sys.argv[1])
    logger.info("read jclass is {}", jclass)