"""第二课：主体仅由学生实现。"""


def simulate_fifo(capacities: list[int], arrivals: list[list[int]]) -> dict:
    """模拟单用户 FIFO，返回结果见讲义。

    capacities[t] 是时隙 t 的数据单位容量。
    arrivals[t] 是时隙 t 末到达的各包大小，按列表顺序入队。
    两个输入必须是等长 list；每个到达项必须是 list。
    容量为非负精确 int，包大小为正精确 int；不接受 bool。
    类型不合法抛 TypeError，值/长度不合法抛 ValueError。
    空输入返回空记录。不得修改输入，不得使用真实时间等待。
    """

    if type(capacities) != list or type(arrivals) != list:
        raise TypeError(f"输入类型错误，必须为列表")
    if len(capacities) != len(arrivals):
        raise ValueError(f"两个输入必须是等长列表")
    for x in capacities:
        if type(x) != int:
            raise TypeError(f"capacities内元素类型错误，必须为整型")
        if x < 0:
            raise ValueError(f"capacities内元素必须非负")
    for arrival in arrivals:
        if type(arrival) != list:
            raise TypeError(f"arrivals下元素必须为列表")
        for x in arrival:
            if type(x) != int:
                raise TypeError(f"arrivals内每一个时隙下每一包必须为整型")
            if x <= 0:
                raise ValueError(f"包的值不合法，必须为正")

    #进行处理前的准备
    t = len(capacities)
    cur_data = []
    size_slot = []
    head = 0
    served = []
    backlog = []
    completed = []
    pending = []
    now_sum = 0

    #开始处理
    for ti in range(t):
        #先进行发送
        capacities_i = capacities[ti]
        while capacities_i != 0 and head < len(cur_data):
            deducted = min(cur_data[head], capacities_i)
            cur_data[head] -= deducted
            capacities_i -= deducted
            if cur_data[head] == 0:
                completed.append((head, size_slot[head][1], ti, ti - size_slot[head][1]))
                head += 1
        served.append(capacities[ti] - capacities_i)
        now_sum -= capacities[ti] - capacities_i

        #处理新到达的包
        arrival_i = arrivals[ti]
        for packet in arrival_i:
            cur_data.append(packet)
            size_slot.append((packet, ti))
            now_sum += packet
        backlog.append(now_sum)

    #处理完毕，统计
    while head < len(cur_data):
        pending.append((head, size_slot[head][1], size_slot[head][0], cur_data[head]))
        head += 1

    #返回
    log = {
        "served": served,
        "backlog": backlog,
        "completed": completed,
        "pending": pending
    }
    return log