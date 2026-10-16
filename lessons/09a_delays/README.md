# 第九课A：逐包完成时延

## 课前回顾

01–08课已通过。回顾：完成包平均时延为什么可能低估拥塞？packet_time保存什么？C输出数组为什么由Python分配？

## 本课目标与口径

第六课B只有完成包计数，无法计算时延分布。本课保留四策略语义，只扩展逐包完成事件输出，下一部分再计算指标。

完成时延D=完成时隙编号-到达时隙编号，单位为时隙。新包在时隙末尾到达，因此完成包D>=1。它包含排队及传输至完成的时间，不应称为仅等待首次服务的纯排队时延；也不等于程序运行秒数。

新增delays与delay_users两个调用者拥有的size_t数组，各容量users*slots，仅前completed项有效。每用户每时隙至多到达一个包，因此总包数不超过该容量。按完成事件顺序排列；某用户一次发送可能完成多个包，分别输出。未完成包没有完成时延，不补0，仍需后续结合未完成数量和积压判断拥塞。用户编号支持后续检查是否牺牲部分用户。

先保留第六课成果，学生手动复制自己的实现到本课空框架，再做接口扩展。助手不复制或补全主体。函数新名simulate_policy_delays，独立DLL，避免旧二进制与新ABI混用。C头文件已固定接口，需让C定义、ctypes声明、传入实参三者一致。

## 手算（先做，不急着写代码）

单用户，四个时隙：capacities=[[3],[3],[3],[3]]，arrivals=[[2],[4],[0],[0]]。

按先发送、后到达，逐时隙记录发送量、剩余量、完成事件。计算两个包的完成时隙、完成时延，以及最终delays、delay_users与completed。

## 实现步骤

A1 手算及接口理解；A2 学生迁移和扩展C；A3 学生迁移和扩展Python；A4 公开验收与理解。允许编辑本课student.c、student.py、reflection.md，不改前课成果。新增参数具体要求见student.h。

## 构建与验收

在E:\hw\wireless-scheduler运行：

```powershell
$env:ZIG_GLOBAL_CACHE_DIR='E:\hw\wireless-scheduler\tools\zig-global-cache'
$env:ZIG_LOCAL_CACHE_DIR='E:\hw\wireless-scheduler\tools\zig-local-cache'
& .\tools\ziglang\zig.exe cc -std=c11 -Wall -Wextra -Wconversion -O2 -shared lessons/09a_delays/student.c lessons/06_policies/student.c '-Wl,--export-all-symbols' -o lessons/09a_delays/scheduler_delays.dll
python -B lessons/09a_delays/test_acceptance.py
```

空框架未实现，不算通过。测试覆盖手算、同隙多包完成、事件顺序、多用户四策略、未完成样本排除、重复调用及守恒；接口边界沿用第六课B要求，源码仍须审查，不能仅凭样例通过。

## 理解验收与后续

解释时延口径、为什么不补0、为何只读completed项、数组容量上限、记录时使用哪一个包的到达时间。第09课B再准备吞吐量/Jain/分位数定义与测试，不提前实现。

这里适合 fork 到内容消化线：完成时延、纯排队时延及未完成样本的统计偏差。
