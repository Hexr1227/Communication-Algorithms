"""第九课B公开验收，固定样本与边界，不提供指标实现。"""
import unittest
from student import throughput, jain_index, delay_summary


class MetricsAcceptance(unittest.TestCase):
    def test_throughput(self):
        self.assertEqual(throughput([6, 2], 4), 2.0)
        self.assertEqual(throughput([0, 0], 4), 0.0)
        self.assertEqual(throughput([3], 2), 1.5)
        self.assertEqual(throughput([2**64-1], 1), float(2**64-1))

    def test_throughput_validation(self):
        for values in (None, (1, 2), [True], [1.0], ['1']):
            with self.subTest(values=values):
                with self.assertRaises(TypeError): throughput(values, 1)
        for values in ([], [-1], [2**64]):
            with self.subTest(values=values):
                with self.assertRaises(ValueError): throughput(values, 1)
        for slots in (True, 1.0, None):
            with self.assertRaises(TypeError): throughput([1], slots)
        for slots in (0, -1):
            with self.assertRaises(ValueError): throughput([1], slots)

    def test_jain(self):
        self.assertAlmostEqual(jain_index([6, 2]), 0.8)
        self.assertEqual(jain_index([4, 4]), 1.0)
        self.assertEqual(jain_index([8, 0]), 0.5)
        self.assertEqual(jain_index([9]), 1.0)
        self.assertIsNone(jain_index([0, 0]))
        self.assertAlmostEqual(jain_index([60, 20]), jain_index([6, 2]))
        self.assertEqual(jain_index([2**64-1, 2**64-1]), 1.0)

    def test_jain_validation(self):
        for values in (None, (1, 2), [True], [1.0]):
            with self.assertRaises(TypeError): jain_index(values)
        for values in ([], [-1], [2**64]):
            with self.assertRaises(ValueError): jain_index(values)

    def test_delay_hand_sample(self):
        self.assertEqual(delay_summary([1, 2, 2, 5], 6),
                         dict(completed=4, pending=2, completion_ratio=4/6,
                              mean=2.5, p95=5, max=5))
        self.assertEqual(delay_summary([3], 1),
                         dict(completed=1, pending=0, completion_ratio=1.0,
                              mean=3.0, p95=3, max=3))

    def test_nearest_rank_and_input_unchanged(self):
        values = list(range(20, 0, -1))
        result = delay_summary(values, 20)
        self.assertEqual(result['p95'], 19)
        self.assertEqual(values, list(range(20, 0, -1)))
        self.assertEqual(delay_summary(list(range(1, 22)), 21)['p95'], 20)
        served = [6, 2]
        throughput(served, 4)
        jain_index(served)
        self.assertEqual(served, [6, 2])

    def test_empty_samples(self):
        self.assertEqual(delay_summary([], 3),
                         dict(completed=0, pending=3, completion_ratio=0.0,
                              mean=None, p95=None, max=None))
        self.assertEqual(delay_summary([], 0),
                         dict(completed=0, pending=0, completion_ratio=None,
                              mean=None, p95=None, max=None))

    def test_delay_validation(self):
        for values in (None, (1,), [True], [1.0]):
            with self.assertRaises(TypeError): delay_summary(values, 1)
        for values in ([0], [-1]):
            with self.assertRaises(ValueError): delay_summary(values, 1)
        for count in (True, 1.0, None):
            with self.assertRaises(TypeError): delay_summary([], count)
        for values, count in (([], -1), ([1, 2], 1)):
            with self.assertRaises(ValueError): delay_summary(values, count)


if __name__ == '__main__':
    unittest.main(verbosity=2)
