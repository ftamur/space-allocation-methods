#!/usr/bin/env python3

"""
The objective of this project is to understand, implement,
and empirically measure the performance of two space allocation methods
used in file systems, namely contiguous and linked allocation, against various inputs.
"""

__author__ = "Firat Tamur"
__email__ = "ftamur16@ku.edu.tr"

import random

BLOCK_SIZE = 10
BLOCK_COUNT = 32768


class DT:

    def __init__(self, block_count, block_size):
        """
        Initializes Directory Table.

        :param block_count: int -> blocks
        :param block_size: int
        """

        self.block_count = block_count
        self.block_size = block_size
        self.uniques = list(range(1, block_count + 1))
        random.shuffle(self.uniques)


        # create a list for files:
        #  0: not allocated
        # id: allocated to file with file_id = id.
        self.blocks = [0] * block_count

        # dt dictionary keeps each file_id and its file start pointer and file size.
        # dict[int, dict[str, int]]
        # {10: {'p': 10, 's': 20}}
        self.dt = {}

        self.capacity = block_count
        self.size = 0

    def create_file(self, file_id, file_length):
        """
        Allocates blocks in self.blocks to given file_id
        Also updates dt dict.

        :param file_id: int
        :param file_length: int -> bytes

        :return: False -> failure, True -> success
        """

        if file_id in self.dt.keys():
            print("File already exits!")
            return False

        if file_length < 1:
            print("File length must be positive integer!")
            return False

        # bytes to blocks
        block_count = self._byte_to_block(file_length)

        if self.capacity < block_count:
            print("Not enough space!")
            return False

        # find a start pointer for file
        start = self._find_start(block_count)

        # if start point not found compact blocks.
        while start == -1:
            self._compact()
            start = self._find_start(block_count)

        # set dt
        self.dt[file_id] = {'p': start, 's': file_length}

        # set to blocks
        for i in range(start, start + block_count):
            self.blocks[i] = self.uniques.pop(0)

        self.capacity -= block_count
        self.size += block_count

        return True

    def access(self, file_id, byte_offset):
        """
        Returns the location of the byte having the given offset in the directory,
        where byte offset is the offset of that byte from the beginning of the file.

        :param file_id: int
        :param byte_offset: int -> bytes

        :return: -1 -> failure location -> success
        """

        if file_id not in self.dt.keys():
            print("File doesn't exit!")
            return -1

        if byte_offset < 1:
            print("Byte offset value must be positive integer!")
            return -1

        # bytes to blocks
        block_count = self._byte_to_block(byte_offset)

        return self.dt[file_id]['p'] + block_count - 1

    def extend(self, file_id, extension):

        if file_id not in self.dt.keys():
            print("File doesn't exit!")
            return False

        if extension < 1:
            print("Extension value must be positive integer!")
            return False

        if self.capacity < extension:
            print("Not enough space!")
            return False

        file_block_size = self._byte_to_block(self.dt[file_id]['s'])

        # find end point for file
        end_point = self.dt[file_id]['p'] + file_block_size - 1

        while not self._all_empty(end_point, extension):
            # remove empty spaces
            self._compact()

            # replace file to end of memory
            self._defragment(file_id)

            # after compaction and defragmentation new pointer
            end_point = self.dt[file_id]['p'] + file_block_size - 1

        for i in range(end_point, extension):
            self.blocks[i] = file_id

        # set dt
        self.dt[file_id]['s'] = extension * self.block_size
        self.capacity -= extension
        self.size += extension












    def shrink(self, file_id, shrinking):
        """
        Shrinks file with given file_id.

        :param file_id: int
        :param shrinking: int -> block
        :return:
        """

        if file_id not in self.dt.keys():
            print("File doesn't exit!")
            return False

        if shrinking < 1:
            print("Shrinking value must be positive integer!")
            return False

        # bytes to blocks
        file_block_size = self._byte_to_block(self.dt[file_id]['s'])

        if file_block_size - shrinking <= 1:
            print("Shrink value too large!")
            return False

        # find end point for file
        end_point = self.dt[file_id]['p'] + file_block_size - 1

        # set blocks
        for i in range(shrinking):
            self.uniques.append(self.blocks[end_point - i])
            self.blocks[end_point - i] = 0

        # set file id with new length in dt.
        if self.dt[file_id]['s'] % self.block_size == 0:
            self.dt[file_id]['s'] -= shrinking * self.block_size
        else:
            self.dt[file_id]['s'] -= shrinking * (self.block_size - 1) + self.dt[file_id]['s'] % self.block_size

        self.capacity += shrinking
        self.size -= shrinking

    """ Utils """

    def _find_start(self, file_block_count):
        """
        Finds a start point for contiguous allocation.

        :param file_block_count: int -> blocks
        :return: int
        """

        start = -1
        i = 0

        while i < self.block_count:

            if self.blocks[i] == 0:
                empty, zeros = self._all_empty(i, file_block_count)
                if empty:
                    start = i
                    break
                else:
                    i += zeros
            else:
                i += 1

        return start

    def _all_empty(self, start, length):
        """
        Checks whether self.blocks[start:start+length] are all zeros.

        :param start: int
        :param length: int -> blocks
        :return: True -> success, False -> failure, start -> number of zeros
        """
        zeros = 0

        while length:
            if start == self.block_count:
                return False, zeros

            if self.blocks[start] != 0:
                return False, zeros

            start += 1
            length -= 1
            zeros += 1

        return True, zeros

    def _compact(self):
        """
        Compacts if not contiguous space found.
        It is similar algorithm to insertion sort.
        It is basically shifts all value bigger 0 to left.

        It has O(n^2) complexity. I may change it.

        :return: None
        """

        for file in self.dt.keys():

            start = self.dt[file]['p']
            end = start + self._byte_to_block(self.dt[file]['s'])

            for i in range(start, end):

                key = self.blocks[i]
                zeros = 0

                j = i - 1

                while j >= 0 and self.blocks[j] == 0:
                    self.blocks[j + 1] = 0
                    zeros += 1
                    j -= 1

                self.blocks[j + 1] = key

            self.dt[file]['p'] -= zeros


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


dt = DT(30, 5)

dt.create_file(1, 20)
dt.create_file(2, 30)
dt.create_file(3, 30)
dt.shrink(2, 4)
dt.create_file(4, 90)
