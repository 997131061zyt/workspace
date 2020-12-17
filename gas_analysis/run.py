# -*-coding=utf-8-*-

import pandas as pd
from openpyxl import load_workbook
import copy
import _sqlite3
from os import path, getcwd

supply_dict = None
demand_dict = None
arcs_list = None

class Node(object):
    def __init__(self, code, name, node_type, volume=0, province=''):
        self.code = code
        self.name = name
        self.type = node_type
        self.volume = volume
        self.province = province
        self.tra_cost = 0
        self.outlines = []
        self.in_degree = 0
        self.deepth = 0
        self.up_arcs = []
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


# def get_node_dict(file_path, sheet_name, node_type):
#     node_dict = {}
#     df = pd.read_excel(file_path, sheet_name=sheet_name)
#     for index, row in df.iterrows():
#         node = Node(row['code'], row['name'], node_type, row['volume'] if node_type == 'supply' else 0)
#         node_dict[row['code']] = node
#     return (df, node_dict) if node_type == 'demand' else node_dict
#
#
# def get_arcs_list(file_path, sheet_name, node_dict):
#     arcs_list = []
#     df = pd.read_excel(file_path, sheet_name=sheet_name)
#     for index, row in df.iterrows():
#         if row['volume'] == 0:
#             continue
#         up_code = row['point_code_up']
#         down_code = row['point_code_down']
#         line = Line(row['code'], row['name'], node_dict[up_code], node_dict[down_code],
#                     row['price'], row['mileage'], row['volume'])
#         arcs_list.append(line)
#     return arcs_list


def process():
    global supply_dict, arcs_list
    # # 初始化各节点的入度值
    # for arc in arcs_list:
    #     arc.up_node.outlines.append(arc)
    #     arc.down_node.in_degree += 1

    # 将气源节点添加到链表中
    linklist = []
    for supply in supply_dict.values():
        linklist.append(supply)

    while len(linklist):
        node = linklist.pop(0)
        for arc in node.outlines:
            down_node = arc.down_node
            down_node.volume += arc.volume
            down_node.tra_cost += arc.volume / node.volume * node.tra_cost if node.volume != 0 else 0
            down_node.tra_cost += arc.volume * arc.fee
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


# 交换反输管段的起终点坐标
# def ex_loc(arc):
#     arc.up_node, arc.down_node = arc.down_node, arc.up_node
#     arc.volume = - arc.volume
#     return arc


def output(file_path):
    global demand_dict
    pd.set_option('max_colwidth', 200)
    result_df = pd.DataFrame(columns=('code', 'name', 'volume', 'tra_cost', 'sup_ratio', 'sup_vol'))
    for index, node in enumerate(demand_dict.values()):
        result_df.loc[index] = [node.code, node.name, node.volume, node.tra_cost, percentage_trans(node.sup_rat_dict),
                                node.sup_vol_dict]
    result_df.to_excel(file_path, sheet_name='result_cus')
    return result_df


def demand_group(file_path):
    global demand_dict
    pd.set_option('max_colwidth', 200)
    result_df = pd.DataFrame(columns=('province', 'supply', 'volume'))
    for node in demand_dict.values():
        if node.province == '': continue
        for supply, volume in node.sup_vol_dict.items():
            result_df.loc[result_df.shape[0]] = [node.province, supply, volume]

    result_df1 = result_df.groupby(['province', 'supply']).sum()
    sub_df = result_df1.groupby('province').sum()
    result_df1['ratio'] = result_df1.div(sub_df, axis=0)['volume']
    result_df1 = result_df1.sort_values(by=['province', 'ratio'], ascending=[True, False])
    result_df1['ratio'] = result_df1['ratio'].apply(lambda x: '%.2f%%' % (x * 100))
    book = load_workbook(file_path)
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    result_df1.to_excel(writer, sheet_name='result_prov')
    writer.save()
    # print(result_df1)

    result_df2 = result_df.groupby(['supply', 'province']).sum()
    sub_df = result_df2.groupby('supply').sum()
    result_df2['ratio'] = result_df2.div(sub_df, axis=0)
    result_df2 = result_df2.sort_values(by=['supply', 'ratio'], ascending=[True, False])
    result_df2['ratio'] = result_df2['ratio'].apply(lambda x: '%.2f%%' % (x * 100))
    book = load_workbook(file_path)
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    result_df2.to_excel(writer, sheet_name='result_supp')
    writer.save()
    # print(result_df2)


def percentage_trans(ratio_dict):
    for key, ratio in ratio_dict.items():
        ratio_dict[key] = '%.2f%%' % (ratio * 100)
    return ratio_dict


def read_sqlite3(file_path, year_id):
    global supply_dict, demand_dict, arcs_list
    year_id = str(year_id)
    pd.set_option('max_colwidth', 200)
    with _sqlite3.connect(file_path) as con:
        # 获取场站节点信息
        select_sql = 'SELECT NodeID id, Caption name FROM tbl_Input_Node_Static'
        station_df = pd.read_sql_query(select_sql, con)
        station_dict = {}
        for row in station_df.itertuples():
            node = Node(row.id, row.name, 'station')
            station_dict[node.code] = node

        # 获取管段信息
        select_sql = 'SELECT a.PipeID id, a.Caption name, a.UpNodeID up_node_id, a.DownNodeID down_node_id, ' \
                     'b.YearUnitAlterableCost price, b.YearUpFlowRate volume ' \
                     'FROM tbl_Input_Pipe_Static a INNER JOIN tbl_Output_Pipe_Year b ' \
                     'ON a.PipeID = b.PipeID ' \
                     'WHERE b.CaseID = 1 AND b.YearID = ' + year_id
        arcs_df = pd.read_sql_query(select_sql, con)
        arcs_list = []
        for row in arcs_df.itertuples():
            if row.volume == 0:
                continue
            elif row.volume > 0:
                line = Line('P' + str(len(arcs_list)), row.name, station_dict[row.up_node_id],
                            station_dict[row.down_node_id], row.price, 1, row.volume)
            else:
                line = Line('P' + str(len(arcs_list)), row.name, station_dict[row.down_node_id],
                            station_dict[row.up_node_id], row.price, 1, -row.volume)
            arcs_list.append(line)

        # 获取气源节点信息
        select_sql = 'SELECT a.SourceID id, a.Caption name, a.NodeID node_id, b.YearFlowRate volume ' \
                     'FROM tbl_Input_Source_Static a INNER JOIN tbl_Output_Source_Year b ' \
                     'ON a.SourceID = b.GasSourceID ' \
                     'WHERE b.CaseID = 1 AND b.YearID = ' + year_id
        supply_df = pd.read_sql_query(select_sql, con)
        supply_dict = {}
        for row in supply_df.itertuples():
            if row.volume == 0: continue
            node = Node('S' + str(len(supply_dict)), row.name, 'supply', row.volume)
            supply_dict[node.code] = node
            line = Line('P' + str(len(arcs_list)), row.name, node, station_dict[row.node_id], 0, 1, row.volume)
            arcs_list.append(line)

        # 获取用户节点信息
        select_sql = 'SELECT a.ClientID id, a.Caption name, a.NodeID node_id, b.YearFlowRate volume, ' \
                     'a.Province province ' \
                     'FROM tbl_Input_Client_Static a INNER JOIN tbl_Output_Client_Year b ' \
                     'ON a.ClientID = b.GasClientID ' \
                     'WHERE b.CaseID = 1 AND b.YearID = ' + year_id
        demand_df = pd.read_sql_query(select_sql, con)
        demand_dict = {}
        for row in demand_df.itertuples():
            if row.volume == 0: continue
            node = Node('L' + str(len(demand_dict)), row.name, 'demand', province=row.province)
            demand_dict[node.code] = node
            line = Line('P' + str(len(arcs_list)), row.name, station_dict[row.node_id], node, 0, 1, row.volume)
            arcs_list.append(line)

        # 获取储气库信息
        select_sql = 'SELECT a.StorageID id, a.Caption name, a.NodeID node_id, b.YearFlowRate volume ' \
                     'FROM tbl_Input_Storage_Static a INNER JOIN tbl_Output_Storage_Year b ' \
                     'ON a.StorageID = b.GasStorageID ' \
                     'WHERE b.CaseID = 1 AND b.YearID = ' + year_id
        other_df = pd.read_sql_query(select_sql, con)
        for row in other_df.itertuples():
            if row.volume == 0: continue
            elif row.volume > 0:
                node = Node('L' + str(len(demand_dict)), row.name, 'demand')
                demand_dict[node.code] = node
                line = Line('P' + str(len(arcs_list)), row.name, station_dict[row.node_id], node, 0, 1, row.volume)
                arcs_list.append(line)
            else:
                node = Node('S' + str(len(supply_dict)), row.name, 'supply', -row.volume)
                supply_dict[node.code] = node
                line = Line('P' + str(len(arcs_list)), row.name, node, station_dict[row.node_id], 0, 1, -row.volume)
                arcs_list.append(line)

        # 获取接收站信息
        select_sql = 'SELECT a.TankID id, a.Caption name, a.UpNodeID up_node_id, a.DownNodeID down_node_id, ' \
                     'b.YearUpFlowRate volume ' \
                     'FROM tbl_Input_Tank_Static a INNER JOIN tbl_Output_Tank_Year b ' \
                     'ON a.TankID = b.TankID ' \
                     'WHERE b.CaseID = 1 AND b.YearID = ' + year_id
        other_df = pd.read_sql_query(select_sql, con)
        for row in other_df.itertuples():
            if row.volume == 0: continue
            node = Node('T' + str(row.Index), row.name, 'Tank')
            line = Line('P' + str(len(arcs_list)), row.name, station_dict[row.up_node_id], node, 0, 1, row.volume)
            arcs_list.append(line)
            line = Line('P' + str(len(arcs_list)), row.name, node, station_dict[row.down_node_id], 0, 1, row.volume)
            arcs_list.append(line)

        # 获取损耗信息
        select_sql = 'SELECT a.FixedWastingGasID id, a.Caption name, a.NodeID node_id, b.YearFlowRate volume ' \
                     'FROM tbl_Input_FixedWastingGas_Static a INNER JOIN tbl_Output_FixedWastingGas_Year b ' \
                     'ON a.FixedWastingGasID = b.FixedWastingGasID ' \
                     'WHERE b.CaseID = 1 AND b.YearID = ' + year_id
        other_df = pd.read_sql_query(select_sql, con)
        for row in other_df.itertuples():
            if row.volume == 0: continue
            node = Node('L' + str(len(demand_dict)), row.name, 'demand')
            demand_dict[node.code] = node
            line = Line('P' + str(len(arcs_list)), row.name, station_dict[row.node_id], node, 0, 1, row.volume)
            arcs_list.append(line)

    return supply_dict, demand_dict, arcs_list


def accul(db_file_path, year_id):
    supply_dict, demand_dict, arcs_list = read_sqlite3(db_file_path, year_id)
    process(supply_dict, arcs_list)


# 初始化各节点的下游路径集合
def ini_outlines():
    global supply_dict, arcs_list
    # 初始化各节点的下游路径集合和入度值
    for arc in arcs_list:
        arc.up_node.outlines.append(arc)
        arc.down_node.in_degree += 1


# 计算气源点supply_node就近销售的用户
def sales_nearby(supply_node):
    global supply_dict, arcs_list
    demandlist = []
    linklist = [supply_node]
    print(supply_node.code, supply_node.name, supply_node.volume)
    while len(linklist):
        node = linklist.pop(0)
        print('🔺🔺', node.code, node.name)
        for arc in node.outlines:
            print('🔺', arc.code, arc.name)
        for arc in node.outlines:
            print('⭐', arc.code, arc.name, arc.up_node.name, arc.down_node.name, arc.volume)
            down_node = arc.down_node
            down_node.deepth = node.deepth + arc.mileage
            down_node.up_arcs = node.up_arcs[:]
            down_node.up_arcs.append(arc)
            if down_node.type == 'demand':
                demandlist.append(down_node)
                down_node.volume = arc.volume
                if down_node.volume < supply_node.volume:
                    down_node.sup_vol_dict[supply_node.name] = down_node.volume
                    down_node.sup_rat_dict[supply_node.name] = 1
                    supply_node.volume -= down_node.volume
                    for arc in down_node.up_arcs:  # 流过的路径减去相应的流量
                        arc.volume -= down_node.volume
                    print(supply_node.code, supply_node.name, supply_node.volume, down_node.code, down_node.name,
                          down_node.volume, down_node.sup_vol_dict.values(), down_node.province)
                else:  # down_node.volume >= supply_node.volume
                    down_node.sup_vol_dict[supply_node.name] = supply_node.volume
                    for arc in down_node.up_arcs:  # 流过的路径减去相应的流量
                        arc.volume -= supply_node.volume
                    supply_node.volume = 0
                    print(supply_node.code, supply_node.name, supply_node.volume, down_node.code, down_node.name,
                          down_node.volume, down_node.sup_vol_dict.values(), down_node.province)
                    break

            else:  # 按深度大小排序，小的排在前面
                linklist.append(down_node)
                index = len(linklist) - 1
                while index > 0:
                    if linklist[index].deepth < linklist[index-1].deepth:
                        linklist[index], linklist[index-1] = linklist[index-1], linklist[index]
                        index -= 1
                    else: break
                for a in linklist:
                    print('※※※※', a.code, a.name, a.deepth)
        if supply_node.volume == 0:
            break
    print(supply_node.code, supply_node.name, supply_node.volume)


if __name__ == '__main__':
    # tra_total = 0
    # for key, value in demand_dict.items():
    #     tra_total += value.tra_cost
    # print('tra_total:', tra_total)
    # tra_total = 0
    # for arc in arcs_list:
    #     tra_total += arc.volume * arc.mileage * arc.fee
    # print('tra_total:', tra_total)
    read_sqlite3('E:/工作/规划院/20201027资源标签化/20200408.db', 2020 - 2012)
    ini_outlines()
    # process()
    # pd.set_option('max_colwidth', 200)
    # result_df = pd.DataFrame(columns=('code', 'name', 'volume', 'tra_cost', 'sup_ratio', 'sup_vol'))
    # for index, node in enumerate(demand_dict.values()):
    #     result_df.loc[index] = [node.code, node.name, node.volume, node.tra_cost, percentage_trans(node.sup_rat_dict),
    #                             node.sup_vol_dict]
    # print(result_df)
    list = list(supply_dict.values())
    for supply in list:
        print(supply.code, supply.name)
    num2020 = [0, 1, 4, 6, 7, 9, 10, 11, 12, 13, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
           43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,
           68, 69, 70, 71, 72, 73, 74, 75]
    num2025 = [0, 1, 4, 6, 7, 9, 10, 11, 12, 13, 26, 27, 28, 29, 30, 32, 33, 34, 35, 36]
    num2030 = [0, 1, 4, 6, 7, 9, 10, 11, 12, 13, 26, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38]
    for index, n in enumerate(num2020):
        sales_nearby(list[n])
    # sales_nearby(list[36])
    process()
    output('E:/工作/规划院/20201027资源标签化/gas_analysis2020  考虑就近销售.xlsx')
    demand_group('E:/工作/规划院/20201027资源标签化/gas_analysis2020  考虑就近销售.xlsx')