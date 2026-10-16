#ifndef LESSON09_DELAYS_H
#define LESSON09_DELAYS_H
#include "../06_policies/student.h"
#define POLICY_RR 0
/* 保留第六课B全部布局、检查、错误码与事件顺序。
 * 新增 delays、delay_users，均由调用者分配 users*slots 个 size_t。
 * 仅前 *completed 个元素有效，按完成事件顺序紧密排列。
 * delays记录完成时隙减到达时隙；delay_users记录对应用户编号。
 * 同一时隙多个完成包按该用户FIFO顺序输出。
 * 非空场景新增指针不得NULL；slots=0时可NULL。
 * 不写未使用的样本区域；未完成包不输出伪时延。
 * 数组字节尺寸检查沿用cells*sizeof(size_t)检查。
 */
int simulate_policy_delays(size_t users, size_t slots, unsigned policy, double alpha,
    const uint32_t *capacities, const uint32_t *arrivals,
    size_t *selected, uint32_t *served, uint64_t *backlog,
    uint64_t *total_served, size_t *completed, uint64_t *remaining,
    size_t *packet_time, uint32_t *packet_left,
    size_t *head, size_t *tail, uint64_t *queued, double *average,
    size_t *delays, size_t *delay_users);
#endif
