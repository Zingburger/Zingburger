
ogt = []

with open('dvd_gt.txt','r')as f:
    for i in f.readlines():
        ogt.append(i.strip())

with open('dvd_gt_dm.txt','w')as f:
    for i in ogt:
        i = i.split()
        i[0] = 'dm-'+i[0]

        i = ' '.join(i)
        f.write(i+'\n')
