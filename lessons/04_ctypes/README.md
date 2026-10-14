# 第四课：Python 调用 C DLL

## 课前回顾

第三课已通过。回答：C 如何知道数组长度？completed_count 的值与指针有什么区别？调用者提供的缓冲区由谁管理？

## 本课知识

DLL 是供其他程序加载和调用的编译产物。ctypes.CDLL 加载采用本课 C 调用约定的共享库；argtypes 声明函数参数类型，restype 声明返回类型。必须与你的 C 头文件逐项一致。错误的类型或长度可能造成进程崩溃，而不只是 Python 异常。

| C 类型 | ctypes 类型 |
| --- | --- |
| uint32_t | c_uint32 |
| uint64_t | c_uint64 |
| size_t | c_size_t |
| int 返回码 | c_int |
| T* | POINTER(T 的 ctypes 类型) |

ctypes 数组是连续的 C 可访问内存，普通 Python list 不能直接当作 C 数组地址。标量对象的地址可用 byref 传给输出指针，调用后读取其 value。数组和标量在 C 调用结束前必须仍有 Python 对象引用；C 只借用，不能释放 Python 管理的缓冲区。ctypes 的整数转换可能截断超范围数据，所以调用前先验证 Python 值。

Path(__file__).resolve() 以脚本位置定位 DLL，避免当前工作目录改变后加载失败。本课 C 函数一次执行整场仿真；Python 负责输入校验、内存准备和结果转换。禁止在绑定中重写队列算法。

## 作业与契约

只编辑 student.py、reflection.md。复用第三课 student.c，不改其接口。arrivals[t] 是一个包的大小，0 表示无包；本课仍不支持每时隙多个新包。输入要求与结果格式见空框架。delays 仅取 completed_count 指定的有效部分，不能把未使用的缓冲区元素当作零时延包。

示例 capacities=[0,2,2,3]、arrivals=[3,0,2,0]，应返回 served=[0,2,1,2]、backlog=[3,1,2,0]、delays=[2,1]、remaining=0。结果必须来自第三课的 C 实现。

## 构建 DLL

在项目根目录运行，链接参数导出 C 函数，避免为了本课修改第三课实现：

```powershell
$env:ZIG_GLOBAL_CACHE_DIR = "$PWD\tools\zig-global-cache"
$env:ZIG_LOCAL_CACHE_DIR = "$PWD\tools\zig-local-cache"
& .\tools\ziglang\zig.exe cc -std=c11 -Wall -Wextra -O2 -shared lessons/03_c_fifo/student.c '-Wl,--export-all-symbols' -o lessons/04_ctypes/fifo_core.dll
python lessons/04_ctypes/test_acceptance.py
```

DLL 是生成文件，不作为手写源码提交。测试覆盖实际 C 调用、类型声明、DLL 路径、手算、空输入、整数极值、非法输入、重复运行与输入不变。测试不通过时先分清编译错误、DLL 加载错误、接口声明错误与模型结果错误。

## 交付和理解验收

提交 student.py 与 reflection.md，解释你的每个 argtypes 项如何对应头文件，为什么用 c_size_t，谁拥有缓冲区，以及为什么只读取有效 delays。从另一工作目录运行测试应仍可加载 DLL。

这里适合 fork 到内容消化线：DLL、ctypes 数组、输出指针和对象生命周期。先讲清接口再写绑定，不靠试错猜参数类型。

