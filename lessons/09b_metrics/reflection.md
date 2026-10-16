# 第九课B学生记录

1. 4时隙、两用户累计发送[6,2]，系统平均吞吐量是多少？单位是什么？
   4 数据单位/时隙
2. [6,2]、[4,4]、[8,0]的Jain指数分别是多少？全零为什么返回None？
   0.8 1 0.5
3. delays=[1,2,2,5]，到达6包：完整手算六个统计字段。
   completed = 4, pending = 2, completion_ratio = 2/3, mean = 2.5, p95 = None, max = None 
4. pending和remaining有什么区别？到达包数应如何从arrivals计算？
   pendinf是剩下包数，remaining是剩下数据量，达包数是arrivals中正数单元格的数量
5. 完成时延p95较小，是否足以说明服务好？
   否。p95较小说明用户服务分配不均
6. 测试结果、独立修正的问题和待理解事项。
