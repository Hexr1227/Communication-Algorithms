"""第九课A：由学生扩展自己的跨语言绑定。"""
from pathlib import Path
import ctypes as ct
import math

DLL_PATH = Path(__file__).resolve().with_name('scheduler_delays.dll')


def run_simulation(capacities: list[list[int]], arrivals: list[list[int]],
                   policy: str = 'rr', alpha: float = 0.2) -> dict:
    """沿用第六课B参数校验和全部返回字段，新增delays、delay_users列表。

    两个新增列表仅含有效完成样本，长度均为completed。
    不完成的包不填0，不纳入完成时延样本；remaining仍表示未发送数据量。
    整场只调用一次simulate_policy_delays，不在Python重新模拟事件。
    """
# 校验、类型声明、展平、缓冲区和一次C调用。
    if type(capacities) != list or type(arrivals) != list:
        raise TypeError(f"输入类型错误")
    if len(capacities) != len(arrivals) or len(capacities) == 0 or len(arrivals) == 0:
        raise ValueError(f"输入不等长或输入为空")
    row_length = 0
    for capacity in capacities:
        if type(capacity) != list:
            raise TypeError(f"capacities行元素类型错误")
        cur_row_length = len(capacity)
        if row_length == 0:
            row_length = cur_row_length
        if row_length != cur_row_length or row_length == 0:
            raise ValueError(f"capacities尺寸错误")
        for val in capacity:
            if type(val) != int:
                raise TypeError(f"capacities内元素类型错误")
            if val < 0 or val > 2**32 - 1:
                raise ValueError(f"capacities元素超出范围")
    for arrival in arrivals:
        if type(arrival) != list:
            raise TypeError(f"arrivals行元素类型错误")
        cur_row_length = len(arrival)
        if row_length != cur_row_length:
            raise ValueError(f"arrivals尺寸错误")
        for val in arrival:
            if type(val) != int:
                raise TypeError(f"arrivals内元素类型错误")
            if val < 0 or val > 2**32 - 1:
                raise ValueError(f"arrivals元素超出范围")

    if type(policy) != str:
        raise TypeError(f"policy类型错误")
    if policy not in ("rr", "max_rate", "pf", "max_weight"):
        raise ValueError(f"输入了不存在的policy")

    if type(alpha) != int and type(alpha) != float:
        raise TypeError(f"alpha类型错误")
    if alpha <= 0 or alpha > 1 or not math.isfinite(alpha):
        raise ValueError(f"alpha超出范围")

    # 加载DLL，声明参数与返回类型
    dll_library = ct.CDLL(str(DLL_PATH))
    c_simulate_policy_delays = dll_library.simulate_policy_delays
    c_simulate_policy_delays.argtypes = [
        ct.c_size_t,    #users
        ct.c_size_t,    #slots
        ct.c_uint,      #policy
        ct.c_double,    #alpha
        ct.POINTER(ct.c_uint32),    #capacities
        ct.POINTER(ct.c_uint32),    #arrivals
        ct.POINTER(ct.c_size_t),    #selected
        ct.POINTER(ct.c_uint32),    #served
        ct.POINTER(ct.c_uint64),    #backlog
        ct.POINTER(ct.c_uint64),    #total_served
        ct.POINTER(ct.c_size_t),    #completed
        ct.POINTER(ct.c_uint64),    #remaining
        ct.POINTER(ct.c_size_t),    #packet_time
        ct.POINTER(ct.c_uint32),    #packet_left
        ct.POINTER(ct.c_size_t),    #head
        ct.POINTER(ct.c_size_t),    #tail
        ct.POINTER(ct.c_uint64),    #queued
        ct.POINTER(ct.c_double),    #average
        ct.POINTER(ct.c_size_t),    #delays
        ct.POINTER(ct.c_size_t),    #delay_users
    ]
    c_simulate_policy_delays.restype = ct.c_int

    users = len(capacities[0])
    slots = len(capacities)
    policy_code = {"rr": 0, "max_rate": 1, "pf": 2, "max_weight": 3}[policy]

    #二维python列表要先展平
    flat_capacities = []
    flat_arrivals = []
    for i in range(slots):
        for j in range(users):
            flat_capacities.append(capacities[i][j])
            flat_arrivals.append(arrivals[i][j])

    c_capacities = (ct.c_uint32 * (slots * users))(*flat_capacities)
    c_arrivals = (ct.c_uint32 * (slots * users))(*flat_arrivals)
    selected = (ct.c_size_t * slots)()
    served = (ct.c_uint32 * slots)()
    backlog = (ct.c_uint64 * (slots * users))()
    total_served = (ct.c_uint64 * users)()
    completed = ct.c_size_t(0)
    remaining = ct.c_uint64(0)
    packet_time = (ct.c_size_t * (slots * users))()
    packet_left = (ct.c_uint32 * (slots * users))()
    head = (ct.c_size_t * users)()
    tail = (ct.c_size_t * users)()
    queued = (ct.c_uint64 * users)()
    average = (ct.c_double * users)()
    delays = (ct.c_size_t * (slots * users))()
    delay_users = (ct.c_size_t * (slots * users))() 

    #调用C内核并处理返回码
    status = c_simulate_policy_delays(users, slots, policy_code, alpha, c_capacities, c_arrivals, 
                        selected, served, backlog, total_served, ct.byref(completed),
                        ct.byref(remaining), packet_time, packet_left, head, tail,
                        queued, average, delays, delay_users)
    if status != 0:
        raise RuntimeError(f"C函数运行报错")

    res_backlog = []
    backlog = list(backlog)
    for i in range(slots):
        temp = backlog[i * users: (i + 1) * users]
        res_backlog.append(temp)
    res_selected = []
    selected = list(selected)
    for x in selected:
        if x == int(ct.c_size_t(-1).value):
            x = None
        res_selected.append(x)

    res_dict = {
        "selected": res_selected,
        "served": list(served),
        "backlog": res_backlog,
        "total_served": list(total_served),
        "completed": int(completed.value),
        "remaining": int(remaining.value),
        "average": list(average),
        "delays": list(delays)[:completed.value],
        "delay_users": list(delay_users)[:completed.value]
    }
    return res_dict
