# 第六课 A：调度评分与历史服务

## 课前回顾

第五课通过。RR 给用户轮流提供机会，但用户容量不同，传输量不一定相同。回顾：什么时候跳过用户？服务后到达的规则能否因更换策略而改变？答案应是策略只决定服务谁，队列规则一致。

本课分 A/B：A 实现并验收独立策略模块；A 的代码和理解通过后，再准备 B，把策略接入你已有的共同队列推进器和 Python 接口。完成 A 不代表完成整场多算法仿真。

## 所需知识

记 c_i 为当前容量，q_i 为旧队列量，T_i 为历史实际服务平均量。只考虑 q_i>0 且 c_i>0 的用户，选择分数最大者，并列取最小编号。

| 策略 | 本项目评分 | 关注点 |
| --- | --- | --- |
| Max Rate | min(q_i,c_i) | 本时隙实际能发多少 |
| PF | c_i/max(T_i,1e-9) | 当前信道相对过去服务机会的优势 |
| MaxWeight | q_i*c_i | 兼顾积压和信道容量 |

本项目的 Max Rate 使用实际可服务量；PF 使用容量而不截断为队列量，文献中的定义可能不同，需要在模型报告明确。不要据此预设哪种算法总是最好。

PF 每时隙服务后、下一次评分前更新：T_i(new)=(1-alpha)*T_i(old)+alpha*x_i。x_i 为该用户实际发送量，未选用户为0。初始 T_i=1。alpha 越大，近期结果权重越高；空闲时所有历史值也更新。分母下限防止除零和极端小分母。不只更新被选用户，否则未服务用户的历史值不能正确衰减。

C 浮点检查用 isfinite：NaN 和无穷不能作为有效参数。MaxWeight 的整数乘积可能超过 uint64_t；评分可先把操作数转换为 double 再乘，不能先做整数乘法后转换。double 在极大整数范围无法区分所有相邻值，本课并列规则以计算后的 double 分数为准，这个数值局限须记录。

## 手算作业

c=[8,5,2]，q=[10,3,4]，T=[8,2,0.5]。分别写出三种分数及选择。假设选用户2，实际发送2，alpha=0.2，写出更新后所有 T。再设用户0空队列，说明评分时如何处理。

## 作业接口与验收

只编辑 student.c 和 reflection.md，完整契约在 student.h。choose_user 只选择，不能改输入；update_average 必须先验证全部输入，再修改。用户数为0非法；字节尺寸溢出返回2，非法参数返回1。非PF时 average 可为NULL。策略函数不推进队列、不处理到达。

在项目根目录运行：

```powershell
$env:ZIG_GLOBAL_CACHE_DIR = "$PWD\tools\zig-global-cache"
$env:ZIG_LOCAL_CACHE_DIR = "$PWD\tools\zig-local-cache"
& .\tools\ziglang\zig.exe cc -std=c11 -Wall -Wextra -Wconversion -g lessons/06_policies/student.c lessons/06_policies/test_acceptance.c -o lessons/06_policies/test_acceptance.exe
& .\lessons\06_policies\test_acceptance.exe
```

测试涵盖评分、队列截断、并列、空队列/零容量、极大乘积、历史更新、空闲衰减、alpha边界、NaN/无穷、输入不变和校验失败不修改历史。空框架预期失败。

## 内容验收

解释PF分母含义、为什么不是绝对公平保证、为什么所有用户都更新、MaxWeight为何不能直接用整数相乘。学生提交手算、代码和测试记录。这里适合 fork 到内容消化线：PF、指数滑动平均及调度取舍。
