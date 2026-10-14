# 第四课学生记录

1. C 头文件每个参数与 argtypes 的对应关系。
    slots, c_size_t
    *capacities, c_uint32
    *arrivals, c_uint32
    *served, c_uint32
    *backlog, c_unit64
    *delays, c_size_t
    *completed_count, c_size_t
    *remaining, c_uint64
    *scratch, c_size_t
    *scratch_remaining, c_uint32
2. 为什么 size_t 不能随意写成 c_uint32？
   这样类型就对不上了，要写成c_size_t
3. Python list 与 ctypes 数组的区别、内存所有权与生命周期。
   list是python本身数组，内存也是属于python文件本身，周期为运行python文件的过程；ctypes数组是用于调用c函数的接口数组，内存仍然是属于调用者，生命周期到c函数返回后释放
4. 为什么 delays 只能读取有效长度？
   读取长度依据的是completed_count
5. DLL 构建、测试结果及自己修复的问题。
   没有问题
6. 未理解的概念和 fork 主题。
   暂无
