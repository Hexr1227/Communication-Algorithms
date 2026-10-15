# 第六课 B：共同推进器与 Python 多策略接口

## 课前回顾

第六课 A 通过。先解释：PF评分使用更新前还是更新后的历史？为什么空闲时也要衰减？更换策略时服务/到达顺序能否改变？

## 所需知识

现在将你已完成的第五课队列内核和第六课 A 策略模块组合。模块化意味着复用公开函数接口，不将评分公式复制进新文件。评分函数只决定用户，公共推进器负责真正发送及队列更新，所有策略采用同一时隙顺序。历史初始为1，每时隙评分读取旧历史，实际服务后更新一次，供下一时隙使用。空闲也调用更新。新到达仍在时隙末入队，不能参与当前评分或发送。

C 链接器把两个 .c 文件一起编译；新头文件包含第六课 A 的声明和策略编号。输入矩阵按 [时隙][用户] 展平，工作数组按 [用户][包序号] 分区，延续第五课。Python读取SIZE_MAX空闲标记后转为None。ABI的参数顺序必须与新头文件一致，新增unsigned策略编号对应c_uint，double对应c_double。

## 本课任务与契约

只编辑本目录student.c、student.py和reflection.md，复用先前由你写的代码，不修改旧课文件或测试。先完成C再完成Python；C层直接验收命令也可用来隔离绑定问题。所有策略共用一段发送/到达代码，禁止四份复制的队列循环。RR沿用第五课规则，其他策略调用choose_user；每时隙调用update_average一次并处理错误码。历史初始化不依赖缓冲区旧值。

接口细节见两个框架与student.h。C所有数组由调用者分配，非空仿真必须完整校验尺寸和指针。Python输入校验必须完整覆盖矩阵和参数，避免负数、bool或超范围数被ctypes悄悄转换。不得在Python重写队列或策略，结果来自C。

## 手算

capacities=[[2,1],[2,1],[2,1],[2,1]]
arrivals=[[1,1],[1,0],[0,1],[0,0]]，alpha=0.5。
先预测各策略的selected、served、backlog，再逐时隙计算PF的历史：第0时隙全空，历史仍要衰减。比较RR和PF时，哪些输入相同、哪些内部状态不同？

## 构建和验收

在项目根目录运行（参数引号必须保留）：

```powershell
$env:ZIG_GLOBAL_CACHE_DIR = "$PWD\tools\zig-global-cache"
$env:ZIG_LOCAL_CACHE_DIR = "$PWD\tools\zig-local-cache"
& .\tools\ziglang\zig.exe cc -std=c11 -Wall -Wextra -Wconversion -O2 -shared lessons/06b_integration/student.c lessons/06_policies/student.c '-Wl,--export-all-symbols' -o lessons/06b_integration/scheduler.dll
python lessons/06b_integration/test_acceptance.py
```

只测C层时：

```powershell
& .\tools\ziglang\zig.exe cc -std=c11 -Wall -Wextra -Wconversion -g lessons/06b_integration/student.c lessons/06_policies/student.c lessons/06b_integration/test_core.c -o lessons/06b_integration/test_core.exe
& .\lessons\06b_integration\test_core.exe
```

公开测试覆盖不同策略产生不同选择、PF空闲衰减、初始历史重置、共同队列守恒、零容量与输入校验、C指针与尺寸边界、Python类型/错误码。测试不会提供参考推进器；源代码评审确认模块复用。未实现状态预期失败。

## 内容消化验收

解释选择、实际服务、历史更新和到达四件事的先后关系；说明为什么PF初始值、alpha、分母下限属于实验参数或模型约定；说明如何保证只比较策略而非两套仿真器。

这里适合 fork 到内容消化线：C模块链接、共同推进器和PF状态更新。提交代码、手算与测试记录后评审。
