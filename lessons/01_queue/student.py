"""第一课学生作业。仅由学生填写实现主体。"""


def advance_queue(queue: int, capacity: int, arrivals: int) -> tuple[int, int]:
    """返回 (本时隙实际发送量, 时隙结束后的队列量)。

    契约：先服务已有队列，再加入本时隙末新到达的数据。
    三项输入必须为非负 Python int；bool 不接受。
    类型不符抛出 TypeError；负数抛出 ValueError。
    不设缓冲区上限。以数据单位为单位，不追踪包时延。
    """
    if type(queue) != int or type(capacity) != int or type(arrivals) != int:
        raise TypeError(f"输入类型错误，必须为整型")
        
    if queue < 0 or capacity < 0 or arrivals < 0:
        raise ValueError(f"输入值必须为非负数")

    #服务旧队列#
    send = min(queue, capacity)
    queue -= send
    #接受新数据
    new_queue = queue + arrivals
    return (send, new_queue)
  
