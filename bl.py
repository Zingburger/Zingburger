import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(8)


def get_whb(width, height):
    if int(width) > int(height):
        width_new = width
        height_new = int(height) * 2.5
        bl = (height_new - height) / 2
    else:
        height_new = height
        width_new = int(width) * 2.5
        bl = (width_new - width) / 2
    return width_new, height_new, int(bl)


def tr(i):
    fileanme, houzhui = os.path.splitext(i)
    width = \
    os.popen("ffprobe -v error -show_entries stream=width -of csv=p=0 {}/{}".format(sys.argv[1], i)).read().split()[
        0].strip()
    height = \
    os.popen("ffprobe -v error -show_entries stream=height -of csv=p=0 {}/{}".format(sys.argv[1], i)).read().split()[
        0].strip()
    # width_new = (int(width) - (int(sys.argv[4]) * 2))
    # height_new = (int(height) - (int(sys.argv[5]) * 2))
    if (int(width) or int(height) <= 960):
        width_new, height_new, bl = get_whb(int(width), int(height))
        # res = os.popen(f'ffmpeg -loglevel warning -i {sys.argv[1]}/{i} -vf "scale={width_new}:{height_new},pad={width}:{height}:{sys.argv[4]}:{sys.argv[5]}:black" {sys.argv[2]}/bl-{i}').read().strip()
        print(i)
        res = os.popen(
            'ffmpeg -loglevel warning -i {}/{} -vf "scale={}:{},pad={}:{}:{}:{}:black" {}/bl-{}.ts'.format(sys.argv[1],
                                                                                                           i, width,
                                                                                                           height,
                                                                                                           width_new,
                                                                                                           height_new, (
                                                                                                               10 if width_new < height_new else bl),
                                                                                                           (
                                                                                                               bl if width_new < height_new else 10),
                                                                                                           sys.argv[2],
                                                                                                           fileanme)).read().strip()


if __name__ == '__main__':
    list_in = os.listdir(sys.argv[1])
    try:
        num = sys.argv[3]
        list_in = random.sample(list_in, int(num))
    except:
        pass

    for i in list_in:
        pool.submit(tr, i)
