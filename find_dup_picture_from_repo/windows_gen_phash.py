# -*- coding: utf-8 -*-

import os
import imagehash
from PIL import Image
import argparse
import sys
import numpy as np
import multiprocessing as mp

def map(samples):
    a = []
    counter = mp.Value('i', 0)
    for sample in samples:
        c_hash = imagehash.phash(Image.open(sample))
        a.append([c_hash, sample])
        with counter.get_lock():
            counter.value += 1
            if counter.value % 10 == 0:
                print(counter.value)
    return a

def main():
    parser = argparse.ArgumentParser(description='This script generates phash of all the images.')
    parser.add_argument('--img_dir', default='../original_picture_repo', help='The director path stores all the images')
    parser.add_argument('--n_thread', default=1, help='The number of threads')
    parser.add_argument('--out_path',default='../phash/phash.txt', help='The path stores the pHashs of these images')
    FLAGS = parser.parse_args()

    img_data_path = FLAGS.img_dir
    image_names = os.listdir(img_data_path)
    image_names = np.sort(image_names)
    all_img_paths = [os.path.join(img_data_path, x) for x in image_names]

    FLAGS.n_thread = 1 if FLAGS.n_thread < 1 else FLAGS.n_thread

    if FLAGS.n_thread == 1:
        split_names = [all_img_paths]
    else:
        n = len(all_img_paths)
        jiange = int(n / FLAGS.n_thread)
        split_point = []
        for i in range(1, FLAGS.n_thread):
            split_point.append(i*jiange)
        split_names = np.split(all_img_paths, split_point)

    processS = mp.Pool(processes=len(split_names))
    c_results = [[] for i in range(len(split_names))]

    for i, block in enumerate(split_names):
        c_results[i] = processS.apply_async(func=map, args=(block, ))
    processS.close()
    processS.join()

    s = ['pHash imageName']

    for i, values in enumerate(c_results):
        values = values.get()
        for value in values:
            s.append('\n{} {}'.format(value[0], value[1]))

    with open(FLAGS.out_path, 'w') as f:
        f.writelines(s)

if __name__ == '__main__':
    main()