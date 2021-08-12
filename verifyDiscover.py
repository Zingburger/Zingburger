"""
作者：yj.yue
日期： 2021年7月18日
该要：支持直接使用场景命中日志计算发现准确度
输入：
1. 数据类型：YL/RL/TB
2. GT文件
3. 命中日志
4. Pid_map文件
执行```  python3 verifyDiscover.py YL gtfile logfile mapfile  ``` #
"""

import sys


def parse_ground_truth(gt_path: str) -> dict:
    """
    解析GT文件，构建GT[节目->标签]map
    输入：文件路径
    输出：GT信息map
    """
    gt_file = open(gt_path)
    if gt_file is None:
        print("open {} failed.".format(gt_path))
    lines = gt_file.readlines()
    name_gt_map = {}
    for line in lines:
        fields = line.strip().split()
        if len(fields) != 2:
            print("skip line: {}".format(line))
            continue
        name = fields[0]
        if name not in name_gt_map:
            name_gt_map[name] = set()	
        name_gt_map[name].add(fields[1])
    gt_file.close()
    return name_gt_map


def parse_inference(inference_path: str, match_type: str) -> dict:
    """
    解析命中日志，构建命中[节目->命中标签]map
    输入：文件路径
    输出：命中信息map
    """
    infer_file = open(inference_path)
    if infer_file is None:
        print("open {} failed.".format(inference_path))
    lines = infer_file.readlines()
    id_infer_map = {}
    for line in lines:
        fields = line.strip().strip("|").split("|")
        if match_type != fields[5]:
            continue
        _id = fields[2]
        if _id not in id_infer_map:
            id_infer_map[_id] = set()
        id_infer_map[_id].add(fields[-1]) #一个节目多次相同命中结果，只被统计一次。样例计算退化，一个节目只考虑成一个segment
    infer_file.close()
    return id_infer_map


def parse_name_id_map(id_map_path: str) -> dict:
    """
    解析pid_map文件，转化pid格式为命中日志中的格式，构建[name<->pid]map
    输入：文件路径
    输出：节目名和命中日志节目id映射map
    """
    id_map_file = open(id_map_path)
    if id_map_file is None:
        print("open {} failed.".format(id_map_path))
    lines = id_map_file.readlines()
    id_name_map = {}
    for line in lines:
        fields = line.strip().split()
        if "_" not in fields[1]:
            high = int("0x" + fields[1][16:], 16)
            low = int("0x" + fields[1][:16], 16)
            fields[1] = "%lx_%lx" % (high, low)
        id_name_map[fields[0]] = fields[1]
        id_name_map[fields[1]] = fields[0]
    id_map_file.close()
    return id_name_map


def get_score(tp, fp, tn, fn: int) -> (float, float, float):
    """
    计算输出结果
    输入：计数
    输出：计算结果
    """
    try:
        precision = tp * 1.0 / (tp + fp)
        recall = tp * 1.0 / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall)
    except:
        precision, recall, f1 = 0, 0, 0
    return precision, recall, f1


def calculate(gt_map: dict, infer_map: dict, id_name_map: dict):
    """
    对比GT和命中日志，统计结果
    输入：gt信息map，命中信息map,映射关系map
    输出：统计结果
    """
    tp = fp = tn = fn = 0
    fp_adjusted = 0
    for _id in infer_map:
        _tp = _fp = _tn = _fn  = 0
        try:
            name = id_name_map[_id] #限制计算在id_map的节目中，可排除背景流命中的影响
        except:
            continue
        #print(name)
        if name not in gt_map: 
            _fp += len(infer_map[_id])
        else:
            gt_set = gt_map[name]
            infer_set = infer_map[_id] 
            _fn += len(gt_set - infer_set)
            _tp += len(gt_set.intersection(infer_set))
            #print(gt_set.intersection(infer_set))
            _fp += len(infer_set - gt_set)
            print(infer_set - gt_set)
            if len(infer_set & gt_set) == 0:
                fp_adjusted += len(infer_set)           #对于没有命中GT同时命中其他标签的正样本，统计为特殊fp
               #print(name)
        #print(_fn, _tp, _fp)
        tp += _tp
        fp += _fp
        tn += _tn
        fn += _fn
         
    for name in gt_map:
        if id_name_map[name] not in infer_map:  #未命中GT
            fn += len(gt_map[name])
            # print(gt_map[name])
    precision, recall, f1 = get_score(tp, fp, tn, fn)
    print("total tp: {} fp: {} tn: {} fn: {} precision: {:.4f} recall: {:.4f} f1: {:.4f}".format(tp, fp, tn, fn, precision, recall, f1))
    precision_adjusted,_,f1_adjusted = get_score(tp, fp_adjusted, tn, fn)
    print("adjusted precision for dvd: {:.4f} f1: {:.4f}".format(precision_adjusted,f1_adjusted))

if __name__ == '__main__':
    model_type = sys.argv[1]
    gt_file_path = sys.argv[2]
    infer_file_path = sys.argv[3]
    id_map_file_path = sys.argv[4]

    gt_map = parse_ground_truth(gt_file_path)
    infer_map = parse_inference(infer_file_path, model_type)
    id_map = parse_name_id_map(id_map_file_path)
    calculate(gt_map, infer_map, id_map)
