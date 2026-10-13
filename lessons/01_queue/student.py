"""第一课学生作业。仅由学生填写实现主体。"""


def advance_queue(queue: int, capacity: int, arrivals: int) -> tuple[int, int]:
    """返回 (本时隙实际发送量, 时隙结束后的队列量)。

    契约：先服务已有队列，再加入本时隙末新到达的数据。
    三项输入必须为非负 Python int；bool 不接受。
    类型不符抛出 TypeError；负数抛出 ValueError。
    不设缓冲区上限。该课以数据单位为单位，不追踪包时延。
    """
    # TODO（学生）：验证输入是否符合契约。
    # TODO（学生）：按时隙顺序计算结果，并返回两个整数。
    raise NotImplementedError("请由学生独立完成第一课实现")
