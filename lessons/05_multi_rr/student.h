#ifndef MULTI_RR_H
#define MULTI_RR_H
#include <stddef.h>
#include <stdint.h>
#define RR_IDLE SIZE_MAX
/* 所有缓冲区由调用者管理，彼此不得重叠。
 * 输入 capacities、arrivals 及输出 backlog 按 [时隙][用户] 连续排列，
 * 一维下标为 t*users+u。每用户每时隙最多到达一个包，0 表示没有到达。
 * selected、served 各有 slots 个元素；total_served 有 users 个元素。
 * 工作数组 packet_time、packet_left 各有 users*slots 个元素，
 * 按 [用户][包序号] 排列，下标为 u*slots+p。
 * head、tail、queued 各有 users 个元素，每次调用都须初始化。
 * users 必须大于 0；slots 可以为 0。标量输出 completed、remaining
 * 的指针始终必须有效。slots>0 时所有指针都必须有效。
 * 返回 0 表示成功，1 表示参数无效，2 表示溢出（包括 users*slots）。
 * 失败时输出不作保证。不得分配或释放内存，也不得保留传入的地址。
 * completed 统计完成包数，remaining 统计剩余数据单位数。 */
int simulate_rr(size_t users, size_t slots,
    const uint32_t *capacities, const uint32_t *arrivals,
    size_t *selected, uint32_t *served, uint64_t *backlog,
    uint64_t *total_served, size_t *completed, uint64_t *remaining,
    size_t *packet_time, uint32_t *packet_left,
    size_t *head, size_t *tail, uint64_t *queued);
#endif

