"""第八课公开验收：只调用学生公开接口。"""
import random
import unittest
from unittest.mock import patch
import student
from student import generate_capacities

BASE = dict(users=2, slots=3, good_capacity=4, bad_capacity=1,
            p_good_to_bad=0.2, p_bad_to_good=0.3,
            initial_good=[True, False], seed=1)


class ChannelAcceptance(unittest.TestCase):
    def make(self, **changes):
        return generate_capacities(**(BASE | changes))

    def test_initial_and_frozen(self):
        self.assertEqual(self.make(slots=1), [[4, 1]])
        self.assertEqual(self.make(p_good_to_bad=0, p_bad_to_good=0),
                         [[4, 1], [4, 1], [4, 1]])
        self.assertEqual(self.make(users=1, initial_good=[False], slots=1), [[1]])

    def test_alternation(self):
        self.assertEqual(self.make(slots=4, p_good_to_bad=1, p_bad_to_good=1),
                         [[4, 1], [1, 4], [4, 1], [1, 4]])

    def test_single_transition_and_threshold(self):
        # 第一次两个用户各切换一次；不能在切换后重复判断。
        with patch.object(student.random, 'Random') as factory:
            factory.return_value.random.side_effect = [0.1, 0.2, 0.5, 0.9]
            self.assertEqual(self.make(), [[4, 1], [1, 4], [1, 4]])
            self.assertEqual(factory.return_value.random.call_count, 4)
        # 正好等于阈值时不切换，包括随机数为0且概率为0。
        with patch.object(student.random, 'Random') as factory:
            factory.return_value.random.side_effect = [0.2, 0.3]
            self.assertEqual(self.make(slots=2), [[4, 1], [4, 1]])
        with patch.object(student.random, 'Random') as factory:
            factory.return_value.random.return_value = 0.0
            self.assertEqual(self.make(p_good_to_bad=0, p_bad_to_good=0),
                             [[4, 1], [4, 1], [4, 1]])
            self.assertEqual(factory.return_value.random.call_count, 4)

    def test_endpoint_draw_count(self):
        with patch.object(student.random, 'Random') as factory:
            factory.return_value.random.return_value = 0.5
            self.assertEqual(self.make(slots=1), [[4, 1]])
            self.assertEqual(factory.return_value.random.call_count, 0)
        with patch.object(student.random, 'Random') as factory:
            factory.return_value.random.return_value = 0.5
            self.make(slots=4, p_good_to_bad=0, p_bad_to_good=1)
            factory.assert_called_once_with(1)
            self.assertEqual(factory.return_value.random.call_count, 6)

    def test_seed_draw_order_and_global_state(self):
        before = random.getstate()
        self.assertEqual(self.make(), [[4, 1], [1, 1], [1, 4]])
        self.assertEqual(self.make(), self.make())
        self.assertEqual(random.getstate(), before)
        self.make(seed=-8)

    def test_input_and_output_independence(self):
        initial = [True, False]
        rows = self.make(initial_good=initial, p_good_to_bad=1, p_bad_to_good=1)
        self.assertEqual(initial, [True, False])
        rows[0][0] = 99
        self.assertEqual(rows[2], [4, 1])
        self.assertTrue(all(len(row) == 2 for row in rows))
        self.assertEqual(self.make(good_capacity=0, bad_capacity=0), [[0, 0]] * 3)
        self.assertEqual(self.make(good_capacity=2**32-1, bad_capacity=2**32-1),
                         [[2**32-1, 2**32-1]] * 3)

    def test_bad_types(self):
        for name in ('users', 'slots', 'good_capacity', 'bad_capacity', 'seed'):
            for value in (True, 1.5, '1', None):
                with self.subTest(name=name, value=value):
                    with self.assertRaises(TypeError):
                        self.make(**{name: value})
        for name in ('p_good_to_bad', 'p_bad_to_good'):
            for value in (True, '0.5', None):
                with self.subTest(name=name, value=value):
                    with self.assertRaises(TypeError):
                        self.make(**{name: value})
        for initial in ((True, False), None, [1, False], [True, 'B']):
            with self.subTest(initial=initial):
                with self.assertRaises(TypeError):
                    self.make(initial_good=initial)

    def test_bad_values(self):
        cases = [dict(users=0), dict(users=-1), dict(slots=0), dict(slots=-1),
                 dict(good_capacity=-1), dict(bad_capacity=-1),
                 dict(good_capacity=2**32), dict(bad_capacity=5),
                 dict(initial_good=[]), dict(initial_good=[True])]
        for name in ('p_good_to_bad', 'p_bad_to_good'):
            for value in (-0.1, 1.1, float('nan'), float('inf'), -float('inf')):
                cases.append({name: value})
        for change in cases:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    self.make(**change)


if __name__ == '__main__':
    unittest.main(verbosity=2)
