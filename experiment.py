#!/usr/bin/env python3

"""
The objective of this project is to understand, implement,
and empirically measure the performance of two space allocation methods
used in file systems, namely contiguous and linked allocation, against various inputs.
"""

__author__ = "Firat Tamur"
__email__ = "ftamur16@ku.edu.tr"


from dt import DT
from fat import FAT
import time
import pandas as pd


def experiment_(files, method_type, times=5):

    time_ = {}
    file_ = {'Create': [], 'Extend': [], 'Shrink': [], 'Access': [],
             'Create Rejected': [], 'Extend Rejected': [], 'Shrink Rejected': [],
             'Access Rejected': []}

    for file in files:

        times_list = []

        create, extend, shrink, access = [0] * 4
        create_rej, extend_rej, shrink_rej, access_rej = [0] * 4

        # file block size.
        block_size = int(file.split('_')[1])

        # for each file
        for i in range(times):

            print(f"File: {file} - Method: {method_type} - Times: {i + 1}")

            if method_type == 'fat':
                method = FAT(block_size)
            else:
                method = DT(block_size)

            file_id = 1

            with open(file, 'r') as FileObj:

                start = time.time()

                for line in FileObj:
                    line = line.strip().split(':')

                    operation = line[0]

                    if operation == 'c':

                        length = int(line[1])

                        if not method.create_file(file_id, length):
                            create_rej += 1
                        else:
                            file_id += 1

                        create += 1

                    else:

                        f_id = int(line[1])
                        length = int(line[2])

                        if operation == 'e':

                            if not method.extend(f_id, length):
                                extend_rej += 1

                            extend += 1

                        elif operation == 'a':

                            if not method.access(f_id, length):
                                access_rej += 1

                            access += 1

                        elif operation == "sh":

                            if not method.shrink(f_id, length):
                                shrink_rej += 1

                            shrink += 1

                end = time.time()
                times_list.append((end - start) * 1000)

            time_[file] = sum(times_list) / times

        file_['Create'].append(create // 5)
        file_['Access'].append(access // 5)
        file_['Extend'].append(extend // 5)
        file_['Shrink'].append(shrink // 5)

        file_['Create Rejected'].append(create_rej // 5)
        file_['Access Rejected'].append(access_rej // 5)
        file_['Extend Rejected'].append(extend_rej // 5)
        file_['Shrink Rejected'].append(shrink_rej // 5)

    time_df = pd.DataFrame()
    time_df['File'] = list(time_.keys())
    time_df['Time'] = list(time_.values())

    file_df = pd.DataFrame()
    file_df['File'] = list(time_.keys())

    for key in file_.keys():
        file_df[key] = file_[key]

    return time_df, file_df


if __name__ == '__main__':

    io = ['io/input_8_600_5_5_0.txt', 'io/input_1024_200_5_9_9.txt', 'io/input_1024_200_9_0_0.txt',
          'io/input_1024_200_9_0_9.txt', 'io/input_2048_600_5_5_0.txt']

    fat_time, fat_operations = experiment_(io, 'fat')
    # dt_time, dt_operations = experiment_(io, 'dt')

    # print(fat_time)
    # print(fat_operations)

    fat_time.to_csv('output/fat_time.csv', index=False)
    fat_operations.to_csv('output/fat_operations.csv', index=False)

    # print(dt_time)
    # print(dt_operations)
    #
    # dt_time.to_csv('output/dt_time.csv', index=False)
    # dt_operations.to_csv('output/dt_operations.csv', index=False)
    #
























