"""第七课：由学生实现可复现的突发业务输入。"""
import math
import random


def generate_arrivals(*, users: int, normal_slots: int, burst_slots: int,
                      recovery_slots: int, normal_p: float, burst_p: float,
                      packet_size: int, seed: int) -> list[list[int]]:
    """返回按[时隙][用户]排列的包大小矩阵。

    users、packet_size为正精确int，packet_size<=2**32-1。
    三段长度为非负精确int，总长度必须大于0；seed为任意精确int。
    normal_p、burst_p为精确int/float，非bool，有限且在[0,1]。
    各用户每时隙独立地以本阶段概率到达一个固定大小包，无到达记0。
    恢复段使用normal_p；不要求burst_p>=normal_p，由场景配置表达。
    使用局部random.Random(seed)，按时隙优先、用户其次的顺序，
    每个单元恰好一次random()抽样，即使概率为0或1也如此。
    不读取/改变全局随机状态；同参数同seed得到相同轨迹。
    类型错误抛TypeError；范围或总长度错误抛ValueError。
    """
    #完整参数校验、局部随机数源、阶段与到达轨迹生成。
    if type(users) != int or type(packet_size) != int or type(normal_slots) != int \
        or type(burst_slots) != int or type(recovery_slots) != int or (type(normal_p) != int and type(normal_p) != float) \
        or (type(burst_p) != int and type(burst_p) != float) or type(seed) != int:
        raise TypeError(f"输入类型错误")

    if users <= 0 or packet_size <= 0 or packet_size > 2**32 - 1 or normal_slots < 0 or \
        burst_slots < 0 or recovery_slots < 0 or (normal_slots + burst_slots + recovery_slots) <= 0\
        or normal_p < 0 or normal_p > 1 or not math.isfinite(normal_p) or burst_p < 0 or burst_p > 1\
        or not math.isfinite(burst_p):
        raise ValueError(f"输入超出范围")

    packet_matrix = []
    rng = random.Random(seed)
    slots_situations = normal_slots * [0] + burst_slots * [1] + recovery_slots * [0]

    for slot, slot_situation in enumerate(slots_situations):
        cur_packets = []
        if slot_situation == 0:                     #正常和恢复
            for user in range(users):
                if rng.random() < normal_p:
                    cur_packets.append(packet_size)
                else:
                    cur_packets.append(0)
        elif slot_situation == 1:                   #突发
            for user in range(users):
                if rng.random() < burst_p:
                    cur_packets.append(packet_size)
                else:
                    cur_packets.append(0)

        packet_matrix.append(cur_packets)

    return packet_matrix