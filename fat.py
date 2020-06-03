#!/usr/bin/env python3

"""
The objective of this project is to understand, implement, 
and empirically measure the performance of two space allocation methods
used in file systems, namely contiguous and linked allocation, against various inputs.
"""

__author__ = "Firat Tamur"
__email__ = "ftamur16@ku.edu.tr"

BLOCK_SIZE = 10
BLOCK_COUNT = 32768


class FAT:

    def __init__(self, block_count, block_size, fat_entry_size):
        """
        Initializes File Allocation Table.

        :param block_count: int
        :param block_size: int
        :param fat_entry_size: int
        """
        self.block_count = block_count
        self.block_size = block_size
        self.fat_entry_size = fat_entry_size

        # create a list for files:
        #  0: not allocated
        # -1: end of file chain
        self.blocks = [0] * block_count

        # create a dict to keep each file_id and starting block
        # allocated space for fat starts from block 0.
        self.fat = {'fat': 0}

        # allocate blocks for fat
        self.fat_blocks = self._byte_to_block(fat_entry_size * block_count)

        # From 0 to (fat_blocks - 1) allocated to fat.
        # We can start from index fat_blocks to allocate
        # new files.
        for i in range(self.fat_blocks - 1):
            self.blocks[i] = i + 1

        self.blocks[self.fat_blocks - 1] = -1

        # set capacity which is block_count - fat_blocks
        self.capacity = block_count - self.fat_blocks

        # set size
        self.size = 0

    def create_file(self, file_id, file_length):
        """
        Allocates blocks in self.blocks to given file_id
        Also updates fat dict.

        :param file_id: int
        :param file_length: int -> bytes

        :return: False -> failure, True -> success
        """

        if file_id in self.fat.keys():
            print("File already created!")
            return False

        if file_length < 0:
            print("Length value must be positive integer!")
            return False

        # bytes to blocks
        file_block_count = self._byte_to_block(file_length)

        if self.capacity < file_block_count:
            print("Not Enough Space!")
            return False

        self.capacity -= file_block_count
        self.size += file_block_count

        for i in range(self.fat_blocks, self.block_count):
            if self.blocks[i] == 0:
                # set fat initial file to fat_blocks
                self.fat[file_id] = i

                # search block after start point and allocate them.
                self._allocate_fat(i, i + 1, file_block_count)

                break

        return True

    def access_file(self, file_id, byte_offset):
        """
        Accesses file with given byte_offset.

        :param file_id: int
        :param byte_offset: int -> bytes
        :return:
        """

        if file_id not in self.fat.keys():
            print("File doesn't exist!")
            return False

        if byte_offset < 0:
            print("Offset value must be positive integer!")
            return False

        # bytes to block
        block_offset = self._byte_to_block(byte_offset)

        # start index
        start = self.fat[file_id]

        for i in range(block_offset - 1):
            start = self.blocks[start]

        return start

    def extend(self, file_id, extension):
        """
        Extends file with given file_id.

        :param file_id: int
        :param extension: int -> blocks

        :return: False -> failure, True -> success
        """

        if file_id not in self.fat.keys():
            print("File doesn't exist!")
            return False

        if extension < 0:
            print("Extension value must be positive integer!")
            return False

        if self.capacity < extension:
            print("Not Enough Space!")
            return False

        end = self.fat[file_id]

        while True:
            if self.blocks[end] == -1:
                break

            end = self.blocks[end]

        self._allocate_fat(end, self.fat_blocks, extension + 1)

        self.capacity -= extension
        self.size += extension

        return True

    def shrink(self, file_id, shrinking):
        """
        Shrinks file with given file_id.

        :param file_id: int
        :param shrinking: int -> blocks

        :return: False -> failure, True -> success
        """

        if file_id not in self.fat.keys():
            print("File doesn't exist!")
            return False

        if shrinking < 0:
            print("Shrink value must be positive integer!")
            return False

        file_size = self._find_size(file_id)

        if file_size - shrinking < 1:
            print("Too large shrink value!")
            return False

        delete_starts = 0
        end = self.fat[file_id]

        while True:
            delete_starts += 1

            if delete_starts >= file_size - shrinking:
                delete = end
                end = self.blocks[end]

                if delete_starts == file_size - shrinking:
                    self.blocks[delete] = -1
                else:
                    self.blocks[delete] = 0

                if self.blocks[end] == -1:
                    self.blocks[end] = 0
                    break
            else:
                end = self.blocks[end]

        self.capacity += shrinking
        self.size -= shrinking

    """ Utils """

    def _find_size(self, file_id):
        """
        Find file size of given file_id.

        :param file_id: int
        :return: int -> blocks
        """

        file_size = 0

        end = self.fat[file_id]

        while end != -1:
            file_size += 1
            end = self.blocks[end]

        return file_size

    def _allocate_fat(self, end_index, search_starts, blocks):
        """
        Allocates space for given file_index.
        Searches empty blocks starting from start index and blocks count.

        :param end_index: int
        :param search_starts: int
        :param blocks: int

        :return: None
        """

        for i in range(search_starts, self.block_count):

            if self.blocks[i] == 0:

                print("empty: ", i)

                if blocks == 1:
                    self.blocks[end_index] = -1
                    break

                self.blocks[end_index] = i
                end_index = i

                blocks -= 1

        if blocks == 1:
            self.blocks[end_index] = -1

    def _byte_to_block(self, bytes_count):
        """
        Returns givens bytes count to blocks count.

        :param bytes_count: int
        :return: blocks: int
        """

        if bytes_count % self.block_size == 0:
            blocks = bytes_count // self.block_size
        else:
            blocks = (bytes_count // self.block_size) + 1

        return blocks

    def _print(self):

        print("FAT DIRECTORY")
        print("Capacity: ", self.capacity)
        print("Size: ", self.size)

        for key in self.fat.keys():
            print(key, self.fat[key])

        print("FAT BLOCKS")
        print(self.blocks)
