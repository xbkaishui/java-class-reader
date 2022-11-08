#!usr/bin/env python
#coding:utf-8

from loguru import logger
import sys 
import struct
import binascii

class JClass(object):
    ...

class ConstantPool(object):
    
    data_dict = {}
    
    def add_constant_info(self, idx, value):
        self.data_dict[idx] = value
        
    def get_string(self, idx):
        return self.data_dict[idx]
    
    def size(self):
        return len(self.data_dict)

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
        # parse class file
        
        return self.jclass
        
    def check_magic_version(self):
        ...
        
    def read_const_pool(self):
        ...
        
    def read_methods(self):
        ...
        
    def read_table(self):
        ...
        
if __name__ == '__main__':
    parser = ClassFileParser()
    logger.info("args {}", sys.argv)
    parser.parse(sys.argv[1])