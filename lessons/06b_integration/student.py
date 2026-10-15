"""第六课B：由学生编写多用户绑定，不在Python实现调度循环。"""
from pathlib import Path
import ctypes as ct
import math
DLL_PATH = Path(__file__).resolve().with_name('scheduler.dll')


def run_simulation(capacities: list[list[int]], arrivals: list[list[int]],
                   policy: str = 'rr', alpha: float = 0.2) -> dict:
    """两矩阵为非空等形list，每行是非空list，行宽一致。

    元素为精确int，范围0..2**32-1。类型错误TypeError，值/尺寸错误ValueError。
    policy精确str，允许rr/max_rate/pf/max_weight；未知值ValueError。
    alpha为精确int或float（非bool），有限且0<alpha<=1。
    空场景在本Python接口拒绝，C接口仍支持slots=0。
    返回selected（空闲为None）、served、backlog（二维列表）、
    total_served、completed、remaining、average（最终历史列表）。
    整场仿真调用一次C；错误码RuntimeError，DLL加载错误保留OSError。
    不修改输入。不得重写C队列、评分或历史更新逻辑。
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
    c_simulate = dll_library.simulate_policy
    c_simulate.argtypes = [
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
        ct.POINTER(ct.c_double)     #average
    ]
    c_simulate.restype = ct.c_int

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

    #调用C内核并处理返回码
    status = c_simulate(users, slots, policy_code, alpha, c_capacities, c_arrivals, 
                        selected, served, backlog, total_served, ct.byref(completed),
                        ct.byref(remaining), packet_time, packet_left, head, tail,
                        queued, average)
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
        "average": list(average)
    }
    return res_dict