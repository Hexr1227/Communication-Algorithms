#ifndef POLICIES_H
#define POLICIES_H
#include <stddef.h>
#include <stdint.h>
#define POLICY_IDLE SIZE_MAX
#define POLICY_MAX_RATE 1
#define POLICY_PF 2
#define POLICY_MAX_WEIGHT 3
/* 所有数组长为 users，调用者管理，禁止修改输入。
 * eligible 条件：queued>0 且 capacity>0；并列时选编号小者。
 * average 仅 PF 必需，所有值须有限且非负；PF 使用分母下限1e-9。
 * 返回0成功，1非法参数，2不可表示的数组尺寸。
 * 无可服务用户时 *selected=POLICY_IDLE。
 */
int choose_user(size_t users, unsigned policy, const uint32_t *capacity,
                const uint64_t *queued, const double *average, size_t *selected);
/* 每用户 average=(1-alpha)*旧值+alpha*本时隙实际服务量。
 * serviced 是编号或 POLICY_IDLE，只有被选者获得 served 数据单位。
 * alpha 须有限且 0<alpha<=1；空闲时 served 必须为0。
 * 校验完整输入后才能修改 average；错误时数组保持原样。
 * 返回码同上；average 长度为users、值有限非负。 */
int update_average(size_t users, double alpha, size_t serviced,
                   uint32_t served, double *average);
#endif
