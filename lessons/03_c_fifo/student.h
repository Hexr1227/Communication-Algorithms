#ifndef STUDENT_FIFO_H
#define STUDENT_FIFO_H
#include <stddef.h>
#include <stdint.h>

/* 输入：每个时隙最多到达一个包；大小为 0 表示没有新包。
   所有数组由调用者分配和管理，函数只借用，不负责释放。
   served 和 backlog 各有 slots 个元素；delays 也有 slots 个元素，
   但只有前 *completed_count 个时延有效。
   scratch 保存各包的到达时隙，scratch_remaining 保存各包的剩余大小；
   两者都是调用者提供的可写工作数组，各有 slots 个元素。
   所有数组缓冲区必须互不重叠。
   返回值：0 表示成功，1 表示参数无效，2 表示算术溢出。
   空仿真允许数组指针为 NULL，但两个标量输出指针仍须有效。
   失败时，输出数组和工作数组的内容不作保证。 */
int simulate_fifo_c(size_t slots,
    const uint32_t *capacities, const uint32_t *arrivals,
    uint32_t *served, uint64_t *backlog, size_t *delays,
    size_t *completed_count, uint64_t *remaining,
    size_t *scratch, uint32_t *scratch_remaining);
#endif

