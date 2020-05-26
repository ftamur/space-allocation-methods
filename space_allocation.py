#!/usr/bin/env python3

"""
The objective of this project is to understand, implement, 
and empirically measure the performance of two space allocation methods
used in file systems, namely contiguous and linked allocation, against various inputs.
"""

__author__ = "Firat Tamur"
__email__ = "ftamur16@ku.edu.tr"

BLOCK_COUNT = 32768
BLOCK_SIZE = 5


class DirectoryTable():
    
    def __init__(self, block_size, block_count):

        self.block_count = block_count
        self.block_size =  block_size
        self.spaces = [0 for _ in range(block_count)]
        self.capacity = block_count

        # {file_id: {'p': file_pointer, 's': file_size}}
        self.files = {} 
        self.file_ids = []


    def create_file(self, file_id, file_length):

        file_blocks = self._byte_to_block(file_length)
        
        if (self.capacity < file_blocks):
            print("Not enough space!")
            return

        pointer = self._find_pointer(file_blocks)

        if not pointer:
            self._defragmentate()
            pointer = self._find_pointer(file_blocks)

        self.spaces = list(map(lambda x: 1, self.spaces[pointer:pointer+file_blocks]))

        self.capacity -= file_blocks
        self.files[file_id] = {'p': pointer, 's': file_length}


    def _byte_to_block(self, byte):

        if byte % self.block_size == 0:
            return (byte // self.block_size)
        else:
            return (byte // self.block_size) + 1


    def _find_pointer(self, file_length):
        
        end_points = [file['p'] + file['s'] for file in self.files.values()]

        for point in end_points:
            if all(self.spaces[point:point + file_length]):
                return point 
        
        return False


    def _defragmentate(self):
        pass


    def access(self, file_id, byte_offset):
        
        pointer = self.files[file_id]['p']
        return pointer + self._byte_to_block(byte_offset)


    def extend(self, file_id, extension):
        
        if self.capacity < extension:
            print("Not enough space!")
            return

        if self.spaces[self.files[file_id]['p'] + extension] == 1:
            self._defragmentate()

        self.spaces = list(map(lambda x: 1, self.spaces[self.files[file_id]['p']:self.files[file_id]['p'] + extension]))

        self.capacity -= extension
        self.files[file_id]['p'] += extension
        self.files[file_id]['s'] += extension


    def shrink(self, file_id, shrinking):
        
        file_block_size = self._byte_to_block(self.files[file_id]['s'])
        pointer= self.files[file_id]['p']

        self.spaces = list(map(lambda x: 0, self.spaces[pointer + file_block_size:pointer + file_block_size - shrinking:-1])) 

        self.capacity += shrinking
        self.files[file_id]['s'] = (file_block_size - shrinking) * self.block_size




class FileNode():
    pass


class FileAllocationTable():
    pass






