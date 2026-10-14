# 第五课：多用户 FIFO 与轮询 RR

## 课前回顾

前四课通过。每个用户保留自己的 FIFO，旧包先服务、新包后到达。回顾：部分发送如何更新包状态？为什么指针长度需要显式传入？调用期间工作数组由谁拥有？本课先在 C 中验证，下一课再统一 Python 多算法接口。

## 本课知识与模型

共享资源意味着每时隙最多选一位用户，不能同时把所有用户的容量都用于发送。每用户每时隙至多到达一个包，包大小是数据单位，允许部分发送。各用户队列独立，用户内 FIFO；不同用户的包没有全局 FIFO 要求。

RR 的起始候选为用户 0。按用户编号环形寻找有旧数据且本时隙容量大于 0 的用户；选中后，下次搜索从该用户的下一位开始。若无用户可服务，该时隙空闲，搜索起点保持不变。新到达包在本时隙末才入队。RR 按服务机会轮转，未必均衡每人传输的数据量。

输入矩阵用连续数组表达。用户数 U、时隙数 T；[时隙 t][用户 u] 对应 t*U+u。工作数组按用户分区：[用户 u][包序号 p] 对应 u*T+p。同一用户最多到达 T 个包，工作区每用户 T 个位置足够。访问前保证用户、时隙和包下标有效；乘法也可能溢出。head/tail/queued 是每用户独立状态，不要用一组索引混在一起。

## 接口与范围

student.h 是完整契约，只编辑 student.c 和 reflection.md。所有内存由调用者提供。selected[t] 为空闲时写 RR_IDLE；否则是用户编号。served[t] 是该时隙实际发送量，backlog 是所有用户在服务及到达后的积压矩阵；total_served 是每用户累计服务量。completed 是全局完成包数，remaining 是全局最终剩余数据量。本课保存包到达时刻但不导出时延；后续评价课补充输出，避免一次扩展太多。

users=0 返回 1；users*slots 或所需缓冲区字节计算溢出返回 2，不能先访问数组。slots=0 可使用 NULL 数组，completed/remaining 清零；否则所有数组必需。调用者保证实际分配长度与互不重叠，函数无法由裸指针获知长度。不得修改输入，不动态分配，不保存指针。

## 手算作业

U=2，T=4。capacities 每行都是 [2,1]；arrivals 为 [[1,1],[1,0],[0,1],[0,0]]。请写 selected、served、每步 backlog、每用户 total_served、completed 和 remaining。这个模型与你此前的两用户练习一致，但现在由你亲手实现。

再预测：用户 0 有旧包但容量是 0，用户 1 有包且容量是 1，RR 是否必须等待用户 0？

## 编译与测试

在项目根目录运行：

```powershell
$env:ZIG_GLOBAL_CACHE_DIR = "$PWD\tools\zig-global-cache"
$env:ZIG_LOCAL_CACHE_DIR = "$PWD\tools\zig-local-cache"
& .\tools\ziglang\zig.exe cc -std=c11 -Wall -Wextra -g lessons/05_multi_rr/student.c lessons/05_multi_rr/test_acceptance.c -o lessons/05_multi_rr/test_acceptance.exe
& .\lessons\05_multi_rr\test_acceptance.exe
```

测试覆盖手算、环形推进、跳过空队列/零容量、全空、多个包的部分完成、逐用户/全局守恒、大整数、重复运行、输入不变、非法指针及乘法溢出、末尾哨兵。助手还会读源码检查未被样例暴露的边界风险。空框架应失败。

## 理解验收

解释矩阵布局、各用户独立队首/队尾、RR 机会公平与吞吐公平的区别，以及为什么实际总服务能力不能直接把所有用户容量相加。

这里适合 fork 到内容消化线：二维数组的连续布局、共享资源和轮询规则。实现主体必须由你完成。
