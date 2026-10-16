"""第九课B：学生实现统计函数，不重新模拟队列。"""
import math


def throughput(total_served: list[int], slots: int) -> float:
    """总实际发送数据量/总仿真时隙数，单位数据单位/时隙。

    total_served为非空精确list，元素为非负精确int且<=2**64-1。
    slots为正精确int。所有整数参数均不接受bool。
    类型错误TypeError，范围或空列表错误ValueError；不修改输入。
    """
    # 校验与系统平均吞吐量计算。
    if type(total_served) != list or type(slots) != int:
        raise TypeError(f"输入类型错误")
    if len(total_served) == 0 or slots <= 0:
        raise ValueError("输入超出范围")
    for served in total_served:
        if type(served) != int:
            raise TypeError(f"列表内元素类型错误")
        if served < 0 or served > 2**64 - 1:
            raise ValueError(f"列表内元素超出范围")

    total_val = sum(total_served)
    return total_val / slots
    

def jain_index(total_served: list[int]) -> float | None:
    """Jain指数：(sum(x))**2 / (用户数 * sum(x_i**2))。

    列表与元素契约同throughput。全零返回None，表示本课不定义此时公平性。
    包括零吞吐用户，不丢弃用户；单用户发送量非零时为1。
    同一观察时长内使用累计发送量与平均吞吐量计算等价。
    类型错误TypeError，范围或空列表错误ValueError；不修改输入。
    """
    # 校验、全零边界及公平性计算。
    if type(total_served) != list:
        raise TypeError(f"输入类型错误")
    if len(total_served) == 0:
        raise ValueError("输入超出范围")
    for served in total_served:
        if type(served) != int:
            raise TypeError(f"列表内元素类型错误")
        if served < 0 or served > 2**64 - 1:
            raise ValueError(f"列表内元素超出范围")

    if sum(total_served) == 0:
        return None
    jain = 0
    users = len(total_served)
    square_of_sum = 0
    sum_of_squares = 0
    for served in total_served:
        square_of_sum += served
        sum_of_squares += served ** 2
    square_of_sum = square_of_sum ** 2
    jain = square_of_sum / (users * sum_of_squares)
    return jain


def delay_summary(delays: list[int], arrived_packets: int) -> dict:
    """统计已完成包时延，同时报告未完成数量。

    delays为精确list，可空，元素为正精确int，单位时隙。
    arrived_packets为非负精确int，且不得小于len(delays)。不接受bool。
    返回completed、pending、completion_ratio、mean、p95、max六个字段。
    completed为样本数，pending为到达包数减完成数；不是剩余数据量。
    无到达时completion_ratio为None，否则为完成数/到达数。
    无完成样本时mean、p95、max均为None，不填0。
    p95使用最近秩法：升序后取第ceil(0.95*n)个元素（位置从1计）。
    整数秩可精确计算，避免浮点舍入改变索引。不修改输入顺序。
    类型错误TypeError，范围/完成数超过到达数错误ValueError。
    """
    # 校验、计数与空样本处理、均值和分位数。
    if type(delays) != list or type(arrived_packets) != int:
        raise TypeError(f"输入类型错误")
    if arrived_packets < 0 or arrived_packets < len(delays):
        raise ValueError(f"输入超出范围")
    for delay in delays:
        if type(delay) != int:
            raise TypeError(f"列表内元素类型错误")
        if delay <= 0:
            raise ValueError(f"列表内元素超出范围")

    if not delays:
        completed = 0
        pending = arrived_packets
        if arrived_packets > 0:
            completion_ratio = 0
        else:
            completion_ratio = None
        mean = None
        p95 = None
        res_max = None
    else:
        delays = sorted(delays)
        completed = len(delays)
        pending = arrived_packets - completed
        completion_ratio = completed / arrived_packets
        mean = sum(delays) / completed
        p95_user = ((completed * 95 + 99) // 100) - 1
        p95 = delays[p95_user]
        res_max = delays[-1]

    res_dict = {
        "completed": completed,
        "pending": pending,
        "completion_ratio": completion_ratio,
        "mean": mean,
        "p95": p95,
        "max": res_max
    }
    return res_dict