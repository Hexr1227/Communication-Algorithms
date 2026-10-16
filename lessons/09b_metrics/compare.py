"""第九课B接入练习：由学生组织四策略对照。"""
from pathlib import Path
import importlib.util
from student import throughput, jain_index, delay_summary

# 导入设施：为前课同名student.py分配独立模块名。
_binding_path = Path(__file__).resolve().parent.parent / '09a_delays' / 'student.py'
_spec = importlib.util.spec_from_file_location('lesson09_delay_binding', _binding_path)
_binding = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_binding)
run_simulation = _binding.run_simulation


def compare_policies(capacities: list[list[int]], arrivals: list[list[int]]) -> list[dict]:
    """对同一合法非空输入运行rr/max_rate/pf/max_weight，固定alpha=0.2。

    本练习假定两矩阵满足09A输入契约，无需重复编写校验。
    按上述策略顺序返回4个字典。每个字典恰含：
    policy、throughput、jain、remaining、completed、pending、
    completion_ratio、mean、p95、max。
    后六项来自delay_summary，remaining沿用C输出数据量。
    到达包数为arrivals中正数单元格数量，不是到达数据量。
    每策略调用一次run_simulation及三个统计函数，不改输入，不重新抽轨迹。
    """
    # 统计到达包数，准备结果列表。
    arrivals_packets = 0
    for arrival in arrivals:
        for packet in arrival:
            if packet > 0:
                arrivals_packets += 1
    slots = len(capacities)
    res = []

    # 逐一运行四种策略，并调用三个指标函数。
    #RR
    rr_simulation_dict = run_simulation(capacities, arrivals, "rr", 0.2)
    rr_remaining = rr_simulation_dict["remaining"]
    rr_total_served = rr_simulation_dict["total_served"]
    rr_delays = rr_simulation_dict["delays"]
    rr_throughput = throughput(rr_total_served, slots)
    rr_jain = jain_index(rr_total_served)
    rr_delay_summary = delay_summary(rr_delays, arrivals_packets)

    #Max_rate
    max_rate_simulation_dict = run_simulation(capacities, arrivals, "max_rate", 0.2)
    max_rate_remaining = max_rate_simulation_dict["remaining"]
    max_rate_total_served = max_rate_simulation_dict["total_served"]
    max_rate_delays = max_rate_simulation_dict["delays"]
    max_rate_throughput = throughput(max_rate_total_served, slots)
    max_rate_jain = jain_index(max_rate_total_served)
    max_rate_delay_summary = delay_summary(max_rate_delays, arrivals_packets)

    #PF
    pf_simulation_dict = run_simulation(capacities, arrivals, "pf", 0.2)
    pf_remaining = pf_simulation_dict["remaining"]
    pf_total_served = pf_simulation_dict["total_served"]
    pf_delays = pf_simulation_dict["delays"]
    pf_throughput = throughput(pf_total_served, slots)
    pf_jain = jain_index(pf_total_served)
    pf_delay_summary = delay_summary(pf_delays, arrivals_packets)

    #Max_weight
    max_weight_simulation_dict = run_simulation(capacities, arrivals, "max_weight", 0.2)
    max_weight_remaining = max_weight_simulation_dict["remaining"]
    max_weight_total_served = max_weight_simulation_dict["total_served"]
    max_weight_delays = max_weight_simulation_dict["delays"]
    max_weight_throughput = throughput(max_weight_total_served, slots)
    max_weight_jain = jain_index(max_weight_total_served)
    max_weight_delay_summary = delay_summary(max_weight_delays, arrivals_packets)


    # 组织每策略结果字典，返回4条结果。
    rr_res = {
        "policy": "rr",
        "throughput": rr_throughput,
        "jain": rr_jain,
        "remaining": rr_remaining
    }
    rr_res |= rr_delay_summary
    res.append(rr_res)

    max_rate_res = {
        "policy": "max_rate",
        "throughput": max_rate_throughput,
        "jain": max_rate_jain,
        "remaining": max_rate_remaining
    }
    max_rate_res |= max_rate_delay_summary
    res.append(max_rate_res)

    pf_res = {
        "policy": "pf",
        "throughput": pf_throughput,
        "jain": pf_jain,
        "remaining": pf_remaining
    }
    pf_res |= pf_delay_summary
    res.append(pf_res)

    max_weight_res = {
        "policy": "max_weight",
        "throughput": max_weight_throughput,
        "jain": max_weight_jain,
        "remaining": max_weight_remaining
    }
    max_weight_res |= max_weight_delay_summary
    res.append(max_weight_res)

    return res