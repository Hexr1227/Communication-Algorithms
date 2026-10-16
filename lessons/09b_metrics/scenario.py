"""第九课B：由学生连接业务、信道和四策略比较。"""
from pathlib import Path
import importlib.util
from compare import compare_policies

# 教师提供模块导入设施，不含场景生成与实验主体。
def _load_previous(module_name, directory):
    source = Path(__file__).resolve().parent.parent / directory / 'student.py'
    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generate_arrivals = _load_previous('lesson07_traffic', '07_traffic').generate_arrivals
generate_capacities = _load_previous('lesson08_channel', '08_channel').generate_capacities


def run_demo(*, traffic_seed: int = 7, channel_seed: int = 11) -> dict:
    """生成一次固定配置场景并返回输入与指标，不在此函数中打印。

    业务：users=4，normal_slots=20、burst_slots=30、recovery_slots=50，
    normal_p=0.1、burst_p=0.8、packet_size=2、seed=traffic_seed。
    信道：users与业务相同，slots取实际到达矩阵行数，good_capacity=4、
    bad_capacity=1、p_good_to_bad=0.1、p_bad_to_good=0.3，
    initial_good=[True,True,False,False]、seed=channel_seed。
    两个生成器各调用一次，compare_policies调用一次。
    返回恰好三个字段：arrivals、capacities、results，保留生成的输入。
    种子要求沿用生成器契约；本节参数是演示值，未做真实网络校准。
    """
    # 调用业务生成器，保存到达矩阵。
    arrivals = generate_arrivals(users = 4, normal_slots = 20, burst_slots = 30,
                                      recovery_slots = 50, normal_p = 0.1, burst_p = 0.8,
                                      packet_size = 2, seed = traffic_seed)

    # 调用信道生成器，确保用户数及总时隙数一致。
    capacities = generate_capacities(users = 4, slots = len(arrivals), good_capacity = 4,
                                     bad_capacity = 1, p_good_to_bad = 0.1, p_bad_to_good = 0.3,
                                     initial_good = [True,True,False,False], seed = channel_seed)

    # 将两张表交给compare_policies，组织返回字典。
    results = compare_policies(capacities, arrivals)
    return {
        "arrivals": arrivals,
        "capacities": capacities,
        "results": results
    }

if __name__ == '__main__':
    # 调用run_demo，并逐条输出results中的四个策略结果。
    final_results = run_demo(traffic_seed=7, channel_seed=11)
    for result in final_results["results"]:
        print(result)