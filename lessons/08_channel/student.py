"""第八课：由学生实现两状态时变容量轨迹。"""
import math
import random


def generate_capacities(*, users: int, slots: int, good_capacity: int,
                        bad_capacity: int, p_good_to_bad: float,
                        p_bad_to_good: float, initial_good: list[bool],
                        seed: int) -> list[list[int]]:
    """返回[时隙][用户]容量矩阵，单位为数据单位/时隙。

    users、slots 为正精确 int；seed 为任意精确 int，不接受 bool。
    两种容量为精确 int，0 <= bad_capacity <= good_capacity <= 2**32-1。
    两种转移概率为精确 int/float，非 bool、有限、在[0,1]内。
    initial_good 为精确 list，长度等于 users，每项为精确 bool；True表示G。
    不修改 initial_good，每次调用独立初始化状态。
    首行直接由初始状态生成，随后每个相邻时隙之间转移一次。
    使用局部 random.Random(seed)，先按转移时隙、再按用户抽样。
    每次转移每用户恰好抽一次，即使概率为0或1；一共(slots-1)*users次。
    根据转移前状态选阈值，随机数严格小于阈值才切换；一次只切换一次。
    返回独立的行列表，不读取或改变全局随机状态。
    类型错误抛 TypeError；范围和初始状态长度错误抛 ValueError。
    """
    # 校验所有参数，区分类型错误与范围错误。
    if type(users) != int or type(slots) != int or type(seed) != int or type(good_capacity) != int \
        or type(bad_capacity) != int or (type(p_bad_to_good) != int and type(p_bad_to_good) != float)\
        or (type(p_good_to_bad) != int and type(p_good_to_bad) != float) or type(initial_good) != list:
        raise TypeError(f"输入类型错误")

    if users <= 0 or slots <= 0 or bad_capacity < 0 or bad_capacity > good_capacity or good_capacity > 2**32 - 1 \
        or p_bad_to_good < 0 or p_bad_to_good > 1 or not math.isfinite(p_bad_to_good) or \
        p_good_to_bad <0 or p_good_to_bad > 1 or not math.isfinite(p_good_to_bad) or len(initial_good) != users:
        raise ValueError(f"输入超出范围")

    for initial_status in initial_good:
        if type(initial_status) != bool:
            raise TypeError(f"初始状态类型错误")

    # 创建局部随机数源和独立的用户状态副本。
    rng = random.Random(seed)
    status_good = [True] * users
    capacities = []

    # 按契约生成容量矩阵，保留跨时隙的状态。
    for slot in range(slots):
        cur_slot_capacities = []
        if slot == 0:
            status_good[:] = initial_good
        else:
            for user, cur_status in enumerate(status_good):
                if cur_status:      # 好状态
                    if rng.random() < p_good_to_bad:
                        status_good[user] = False  # 向坏状态转移
                    else:
                        status_good[user] = True   # 保持好状态
                else:               # 坏状态
                    if rng.random() < p_bad_to_good:
                        status_good[user] = True   # 向好状态转移
                    else:
                        status_good[user] = False  # 保持坏状态

        for status in status_good:
            if status:
                cur_slot_capacities.append(good_capacity)
            else:
                cur_slot_capacities.append(bad_capacity)

        capacities.append(cur_slot_capacities)

    return capacities