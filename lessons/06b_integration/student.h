#ifndef SIMULATION_H
#define SIMULATION_H
#include "../06_policies/student.h"
#define POLICY_RR 0
/* 保留第五课的矩阵布局、工作区、错误码和内存契约。
 * policy 为0/1/2/3。alpha 对全部策略均须有限且0<alpha<=1。
 * average 长度users，调用者提供；每次调用初始化为1，
 * 所有策略均在每时隙服务之后更新历史，空闲也更新。
 * slots=0 时数组可NULL，仅completed/remaining必须有效，清零返回。
 * users=0非法；非空场景所有数组必需。失败输出不作保证。
 * 三种评分策略必须调用第六课A的choose_user；历史更新必须
 * 调用update_average。仅选择逻辑不同，队列推进代码共用。
 */
int simulate_policy(size_t users, size_t slots, unsigned policy, double alpha,
    const uint32_t *capacities, const uint32_t *arrivals,
    size_t *selected, uint32_t *served, uint64_t *backlog,
    uint64_t *total_served, size_t *completed, uint64_t *remaining,
    size_t *packet_time, uint32_t *packet_left,
    size_t *head, size_t *tail, uint64_t *queued, double *average);
#endif
