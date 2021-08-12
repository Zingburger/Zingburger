import random

text = []

with open('danmu.txt','r')as f:
    for i in f.readlines():
        text.append(i.strip())


print(random.sample(text,3))


def radtext(cout):
    try:
        return '     '.join(random.sample(text,cout))
    except:
        return '     '.join(random.sample(text,len(text)))



