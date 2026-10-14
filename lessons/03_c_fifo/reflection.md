# 第三课学生记录

1. 手算讲义例子的 served、backlog、delays。
   served = [0, 2, 1, 2], backlog = [3, 1, 2, 0]
   delays = [2, 1]
2. 我的 FIFO 状态和索引范围。
   与python版类似，先处理发送，用队首索引检查该处的scratch_remaining，根据capacities处理数据发送量，若发送完则记录该处的scratch并根据此时的时隙计算时延并储存到delays，同时记录served，队首索引向后移位，接着处理到达的包。索引范围小于slots
3. 每块数组由谁拥有？为什么不能在函数中 free？
   由函数的调用者拥有，故而不能在函数内部进行释放
4. uint32_t、uint64_t、size_t 的用途与溢出风险。
    用于固定32位、64位整数，size_t则用于索引或大小，与平台相关。uint64_t最大，故而uint32_t存在溢出风险时应改用uint64_t
5. 编译警告、测试结果与自己修复的问题。
   通过，但是我还是觉得C这一块相较于python要欠缺一点，记得多帮帮我的C
6. 需要 fork 学习的知识点。
    暂无