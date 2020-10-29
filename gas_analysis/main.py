# -*-coding=utf-8-*-

import pandas as pd
from openpyxl import load_workbook
import copy


class Node(object):
    def __init__(self, code, name, node_type, volume=0):
        self.code = code
        self.name = name
        self.type = node_type
        self.volume = volume
        self.tra_cost = 0
        self.outlines = []
        self.in_degree = 0
        self.sup_vol_dict = {name: volume} if node_type == 'supply' else {}
        self.sup_rat_dict = {name: 1.0} if node_type == 'supply' else {}


class Line(object):
    def __init__(self, code, name, up_node: Node, down_node: Node, fee, mileage, volume):
        self.code = code
        self.name = name
        self.up_node = up_node
        self.down_node = down_node
        self.fee = fee
        self.mileage = mileage
        self.volume = volume


def get_node_dict(file_path, sheet_name, node_type):
    node_dict = {}
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    for index, row in df.iterrows():
        node = Node(row['code'], row['name'], node_type, row['volume'] if node_type == 'supply' else 0)
        node_dict[row['code']] = node
    return node_dict


def get_arcs_list(file_path, sheet_name):
    arcs_list = []
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    for index, row in df.iterrows():
        if row['volume'] == 0:
            continue
        up_code = row['point_code_up']
        down_code = row['point_code_down']
        line = Line(row['code'], row['name'], node_dict[up_code], node_dict[down_code],
                    row['price'], row['mileage'], row['volume'])
        arcs_list.append(line)
    return arcs_list


def process():
    for arc in arcs_list:
        arc.up_node.outlines.append(arc)
        arc.down_node.in_degree += 1

    linklist = []
    for supply in supply_dict.values():
        linklist.append(supply)

    while len(linklist):
        node = linklist.pop(0)
        for arc in node.outlines:
            down_node = arc.down_node
            down_node.volume += arc.volume
            down_node.tra_cost += arc.volume / node.volume * node.tra_cost if node.volume != 0 else 0
            down_node.tra_cost += arc.volume * arc.mileage * arc.fee
            for supply_name, supply_ratio in node.sup_rat_dict.items():
                volume_add = arc.volume * supply_ratio
                volume_update = down_node.sup_vol_dict.get(supply_name, 0) + volume_add
                down_node.sup_vol_dict[supply_name] = volume_update
            down_node.in_degree -= 1
            if down_node.in_degree == 0:
                for supply_name, supply_volume in copy.deepcopy(down_node.sup_vol_dict).items():
                    if supply_volume == 0:
                        del down_node.sup_vol_dict[supply_name]
                        continue
                    ratio = supply_volume / down_node.volume if down_node.volume != 0 else 0
                    down_node.sup_rat_dict[supply_name] = ratio
                linklist.append(down_node)


def ex_loc(arc):
    arc.up_node, arc.down_node = arc.down_node, arc.up_node
    arc.volume = - arc.volume
    return arc


def output():
    pd.set_option('max_colwidth', 200)
    result_df = pd.DataFrame(columns=('code', 'name', 'volume', 'tra_cost', 'sup_vol', 'sup_ratio'))
    for index, node in enumerate(demand_dict.values()):
        result_df.loc[index] = [node.code, node.name, node.volume, node.tra_cost, node.sup_vol_dict,
                                node.sup_rat_dict]
    book = load_workbook(filepath)
    writer = pd.ExcelWriter(filepath, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    result_df.to_excel(writer, sheet_name='result')
    writer.save()
    print(result_df)
    return result_df


if __name__ == '__main__':
    filepath = 'E:/工作/规划院/20201027资源标签化/gas_analysis20200408规划数据版本2.xlsx'
    node_dict = get_node_dict(filepath, 'station', 'station')
    supply_dict = get_node_dict(filepath, 'supply', 'supply')
    demand_dict = get_node_dict(filepath, 'demand', 'demand')
    node_dict.update(supply_dict)
    node_dict.update(demand_dict)
    arcs_list = get_arcs_list(filepath, 'arcs')
    arcs_list = [ex_loc(arc) if arc.volume < 0 else arc for arc in arcs_list]
    process()
    output()

    tra_total = 0
    for key, value in demand_dict.items():
        tra_total += value.tra_cost
    print('tra_total:', tra_total)
    tra_total = 0
    for arc in arcs_list:
        tra_total += arc.volume * arc.mileage * arc.fee
    print('tra_total:', tra_total)
