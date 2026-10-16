"""接入练习验收：真实C调用及已有指标函数调用检查。"""
import copy
import unittest
from unittest.mock import patch
import compare


class ComparisonAcceptance(unittest.TestCase):
    def test_small_scene(self):
        c = [[2, 1]] * 4
        a = [[1, 1], [1, 0], [0, 1], [0, 0]]
        before = copy.deepcopy((c, a))
        rows = compare.compare_policies(c, a)
        self.assertEqual([r['policy'] for r in rows], ['rr','max_rate','pf','max_weight'])
        for row in rows:
            self.assertEqual(set(row), {'policy','throughput','jain','remaining',
                'completed','pending','completion_ratio','mean','p95','max'})
            self.assertEqual(row['throughput'], 0.75)
            self.assertAlmostEqual(row['jain'], 0.9)
            self.assertEqual(row['remaining'], 1)
            self.assertEqual(row['completed'], 3)
            self.assertEqual(row['pending'], 1)
            self.assertEqual(row['completion_ratio'], 0.75)
            self.assertAlmostEqual(row['mean'], 5/3)
            # 固定alpha=0.2时PF在时隙2仍选用户0，尾时延为3。
            expected_tail = 2 if row['policy'] == 'rr' else 3
            self.assertEqual(row['p95'], expected_tail)
            self.assertEqual(row['max'], expected_tail)
        self.assertEqual((c, a), before)

    def test_partial_packet_and_no_arrivals(self):
        # 一个大小为10的包，只发出7：pending是1包，remaining是3单位。
        rows = compare.compare_policies([[0],[7]], [[10],[0]])
        for row in rows:
            self.assertEqual(row['throughput'], 3.5)
            self.assertEqual(row['jain'], 1)
            self.assertEqual(row['completed'], 0)
            self.assertEqual(row['pending'], 1)
            self.assertEqual(row['remaining'], 3)
            self.assertEqual(row['completion_ratio'], 0)
            self.assertIsNone(row['p95'])
            self.assertIsNone(row['mean'])
            self.assertIsNone(row['max'])
        for row in compare.compare_policies([[2],[2]], [[0],[0]]):
            self.assertEqual(row['pending'], 0)
            self.assertEqual(row['throughput'], 0)
            self.assertIsNone(row['jain'])
            self.assertIsNone(row['completion_ratio'])

    def test_shared_inputs_and_existing_functions(self):
        c, a = [[0],[7]], [[10],[0]]
        with patch.object(compare, 'run_simulation', wraps=compare.run_simulation) as sim, \
             patch.object(compare, 'throughput', wraps=compare.throughput) as tp, \
             patch.object(compare, 'jain_index', wraps=compare.jain_index) as ji, \
             patch.object(compare, 'delay_summary', wraps=compare.delay_summary) as ds:
            compare.compare_policies(c, a)
            for function in (sim, tp, ji, ds):
                self.assertEqual(function.call_count, 4)
            for call in sim.call_args_list:
                # 可用位置或关键字传参，要求输入取值一致。
                args, kwargs = call
                self.assertEqual(args[0] if args else kwargs['capacities'], c)
                self.assertEqual(args[1] if len(args)>1 else kwargs['arrivals'], a)
            for call in ds.call_args_list:
                args, kwargs = call
                self.assertEqual(args[1] if len(args)>1 else kwargs['arrived_packets'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

