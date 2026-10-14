"""第四课：学生独立实现 ctypes 绑定，不在 Python 重写仿真。"""
from pathlib import Path
import ctypes as ct

DLL_PATH = Path(__file__).resolve().with_name('fifo_core.dll')


def run_fifo(capacities: list[int], arrivals: list[int]) -> dict:
    """整场仿真只调用一次第三课 C 内核。

    两输入为等长 list，元素为精确 int（不接受 bool），范围
    0..2**32-1。类型错误 TypeError，范围/长度错误 ValueError。
    返回 served、backlog、delays 三个 Python list 及 remaining 整数。
    非零 C 返回码抛 RuntimeError；DLL 加载失败保留 OSError。
    空输入返回空列表及 remaining=0。不得修改输入。
    """
    #校验 Python 输入。
    if type(capacities) != list or type(arrivals) != list:
        raise TypeError(f"输入错误，必须输入两个等长列表")
    if len(capacities) != len(arrivals):
        raise ValueError(f"输入数组不等长")
    for x in capacities:
        if type(x) != int:
            raise TypeError(f"capacities元素类型错误，必须为整型")
        if x < 0 or x > 2**32 - 1:
            raise ValueError(f"capacities元素超过范围")
    for x in arrivals:
        if type(x) != int:
            raise TypeError(f"arrivals元素类型错误，必须为整型")
        if x < 0 or x > 2**32 - 1:
            raise ValueError(f"arrivals元素超过范围")
    
    #加载 DLL，依据 student.h 声明参数与返回类型。
    dll_library = ct.CDLL(str(DLL_PATH))
    c_function = dll_library.simulate_fifo_c
    c_function.argtypes = [
        ct.c_size_t,    #slots
        ct.POINTER(ct.c_uint32),    #*capacities
        ct.POINTER(ct.c_uint32),    #*arrivals
        ct.POINTER(ct.c_uint32),    #*served
        ct.POINTER(ct.c_uint64),    #*backlog
        ct.POINTER(ct.c_size_t),    #*delays
        ct.POINTER(ct.c_size_t),    #completed_count
        ct.POINTER(ct.c_uint64),    #*remaining
        ct.POINTER(ct.c_size_t),    #*scratch
        ct.POINTER(ct.c_uint32)     #*scratch_remaining
    ]
    c_function.restype = ct.c_int

    #分配并保留输入、输出、工作数组和标量对象。
    slots = len(capacities)
    c_capacities = (ct.c_uint32 * slots)(*capacities)
    c_arrivals = (ct.c_uint32 * slots)(*arrivals)
    served = (ct.c_uint32 * slots)()
    backlog = (ct.c_uint64 * slots)()
    delays = (ct.c_size_t * slots)()
    completed_count = ct.c_size_t(0)
    remaining = ct.c_uint64(0)
    scratch = (ct.c_size_t * slots)()
    scratch_remaining = (ct.c_uint32 * slots)()

    #调用 C 内核，处理返回码并转换有效结果。
    status = c_function(slots, c_capacities, c_arrivals, served, backlog, 
                        delays, ct.byref(completed_count), ct.byref(remaining), 
                        scratch, scratch_remaining)

    if status != 0:
        raise RuntimeError(f"C函数返回错误")

    res_dict = {
        "served": list(served),
        "backlog": list(backlog),
        "delays": list(delays)[:completed_count.value],
        "remaining": int(remaining.value)
    }
    return res_dict