#!/usr/bin/env python3

"""
The objective of this project is to understand, implement,
and empirically measure the performance of two space allocation methods
used in file systems, namely contiguous and linked allocation, against various inputs.
"""

__author__ = "Firat Tamur"
__email__ = "ftamur16@ku.edu.tr"

import random


class DT:

    def __init__(self, block_size, block_count=32768):
        """
        Initializes Directory Table.

        :param block_count: int -> blocks
        :param block_size: int
        """

        self.block_count = block_count
        self.block_size = block_size

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
            # print("File already exits!")
            return False

        if file_length < 1:
            # print("File length must be positive integer!")
            return False

        # bytes to blocks
        block_count = self._byte_to_block(file_length)

        if self.capacity < block_count:
            # print("Not enough space!")
            return False

        # find a start pointer for file
        start = self._first_fit(block_count)

        # if start point not found compact blocks.
        while start == -1:
            self._compact()
            start = self._first_fit(block_count)

        # set dt
        self.dt[file_id] = {'p': start, 's': file_length}

        # set to blocks
        for i in range(start, start + block_count):
            self.blocks[i] = random.randint(1, 32678)

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
            # print("File doesn't exit!")
            return False

        if byte_offset < 1:
            # print("Byte offset value must be positive integer!")
            return False

        if byte_offset > self.dt[file_id]['s']:
            print("Byte offset must be smaller than file size!")
            return False

        # bytes to blocks
        block_count = self._byte_to_block(byte_offset)

        return self.dt[file_id]['p'] + block_count - 1

    def extend(self, file_id, extension):

        if file_id not in self.dt.keys():
            # print("File doesn't exit!")
            return False

        if extension < 1:
            # print("Extension value must be positive integer!")
            return False

        if self.capacity < extension:
            # print("Not enough space!")
            return False

        file_block_size = self._byte_to_block(self.dt[file_id]['s'])

        # find end point for file
        end_point = self.dt[file_id]['p'] + file_block_size

        if not self._all_empty(end_point, extension)[0]:
            # remove empty spaces
            end_spaces = self._compact()

            # if we have enough spaces end of the memory.
            # Take file to end of memory
            if end_spaces > file_block_size:
                # replace file to end of memory
                self._defragment(file_id)
            # else reject operation
            else:
                # print("Not found enough space at end of memory!")
                return False

            # after compaction and defragmentation new pointer
            end_point = self.dt[file_id]['p'] + file_block_size

        for i in range(end_point, end_point + extension):
            self.blocks[i] = random.randint(1, 32768)

        # set dt
        self.dt[file_id]['s'] = extension * self.block_size
        self.capacity -= extension
        self.size += extension

        return True

    def shrink(self, file_id, shrinking):
        """
        Shrinks file with given file_id.

        :param file_id: int
        :param shrinking: int -> block
        :return:
        """

        if file_id not in self.dt.keys():
            # print("File doesn't exit!")
            return False

        if shrinking < 1:
            # print("Shrinking value must be positive integer!")
            return False

        #
        file_length = self.dt[file_id]['s']

        # bytes to blocks
        file_block_size = self._byte_to_block(file_length)

        if file_block_size - shrinking <= 1:
            # print("Shrink value too large!")
            return False

        # find end point for file
        end_point = self.dt[file_id]['p'] + file_block_size - 1

        # set blocks
        for i in range(shrinking):
            self.blocks[end_point - i] = 0

        # set file id with new length in dt.
        if file_length % self.block_size == 0:
            self.dt[file_id]['s'] -= shrinking * self.block_size
        else:
            self.dt[file_id]['s'] -= shrinking * (self.block_size - 1) + file_length % self.block_size

        self.capacity += shrinking
        self.size -= shrinking

        return True

    """ Utils """

    def _first_fit(self, file_block_count):
        """
        Finds a start point for contiguous allocation.

        :param file_block_count: int -> blocks
        :return: int: -1 -> failure
        """

        start = -1
        zeros = 0

        for i in range(self.block_count):
            if self.blocks[i] == 0:
                zeros += 1
            else:
                zeros = 0

            if zeros == file_block_count:
                start = i + 1 - zeros
                break

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

        :return: int: empty spaces and of self.blocks
        """

        zeros = 0
        i = 0

        for i in range(self.block_count):

            if self.blocks[i] == 0:
                zeros += 1
            else:

                if zeros == 0:
                    continue

                self._update_blocks(i, zeros)

                while self.blocks[i] != 0:
                    self.blocks[i - zeros] = self.blocks[i]
                    self.blocks[i] = 0
                    i += 1

                i -= zeros
                zeros = 0

        return self.block_count - i

    def _update_blocks(self, index, offset):

        for key in self.dt.keys():

            if self.dt[key]['p'] >= index:
                self.dt[key]['p'] -= offset

    def _defragment(self, file_id):

        start = self.dt[file_id]['p']
        end = start + self._byte_to_block(self.dt[file_id]['s'])

        key = self.blocks[start]

        nonzero = self._byte_to_block(self.dt[file_id]['s']) - 1
        j = start + 1

        while self.blocks[j] != 0:
            nonzero += 1
            j += 1

        self.blocks[j] = key
        self.blocks[start] = 0

        for i in range(start + 1, end):
            j += 1
            self.blocks[j] = self.blocks[i]
            self.blocks[i] = 0

        self.dt[file_id]['p'] += nonzero

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




