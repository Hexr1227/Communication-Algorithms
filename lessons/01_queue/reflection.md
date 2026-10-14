# 第一课学生记录

请由学生填写：

1. 三个自己手算的输入与预期结果。
   一般情况：queue = 3, capacity = 2, arrivals = 4 -> send = 2, new_queue = 5 -> return (2, 5)
   空队列: queue = 0 -> send = 0 -> new_queue = queue + arrivals -> return(0, new_queue)
   零容量: capacity = 0 -> send = 0  - > new_queue = queue+arrivals（一直不发送，队列不断累积） -> return(0, new_queue)
2. 我如何保证先发送旧队列、再接收新数据？
   先处理旧队列，发送值为旧队列和容量的最小值，然后再对处理后的旧队列加入新数据
3. 为什么容量增加不一定增加发送量？
   因为如果旧队列数据量不够也无法增加发送量
4. 测试发现了什么错误？我怎样修正？
   测试很顺利，一遍通过所有
5. 哪个概念还不确定？
   暂时没有
6. 类型检查理解：
   bool是int的子类，用type检查会严格判断是不是int，而isinstance检查时若检测到bool也会归于int的大类下