"""第九课A：公开的小场景与性质验收，不包含参考仿真器。"""
import unittest
from student import run_simulation

POLICIES = ('rr', 'max_rate', 'pf', 'max_weight')


class DelayAcceptance(unittest.TestCase):
    def check_result(self, result, arrivals):
        self.assertEqual(len(result['delays']), result['completed'])
        self.assertEqual(len(result['delay_users']), result['completed'])
        self.assertTrue(all(type(d) is int and d >= 1 for d in result['delays']))
        self.assertTrue(all(type(u) is int and 0 <= u < len(arrivals[0])
                            for u in result['delay_users']))
        self.assertEqual(sum(map(sum, arrivals)),
                         sum(result['total_served']) + result['remaining'])

    def test_hand_example(self):
        arrivals = [[2], [4], [0], [0]]
        for policy in POLICIES:
            with self.subTest(policy=policy):
                r = run_simulation([[3]] * 4, arrivals, policy)
                self.assertEqual(r['delays'], [1, 2])
                self.assertEqual(r['delay_users'], [0, 0])
                self.assertEqual(r['served'], [0, 2, 3, 1])
                self.assertEqual(r['backlog'], [[2], [4], [1], [0]])
                self.check_result(r, arrivals)

    def test_multiple_completions_in_one_slot(self):
        r = run_simulation([[0], [0], [10]], [[2], [3], [0]])
        self.assertEqual(r['delays'], [2, 1])
        self.assertEqual(r['delay_users'], [0, 0])
        self.assertEqual(r['completed'], 2)
        self.assertEqual(r['served'], [0, 0, 5])

    def test_four_policy_events(self):
        a = [[1, 1], [1, 0], [0, 1], [0, 0]]
        for policy in POLICIES:
            with self.subTest(policy=policy):
                r = run_simulation([[2, 1]] * 4, a, policy, 0.5)
                if policy in ('rr', 'pf'):
                    self.assertEqual(r['delays'], [1, 2, 2])
                    self.assertEqual(r['delay_users'], [0, 1, 0])
                else:
                    self.assertEqual(r['delays'], [1, 1, 3])
                    self.assertEqual(r['delay_users'], [0, 0, 1])
                self.assertEqual(r['completed'], 3)
                self.assertEqual(r['remaining'], 1)
                self.check_result(r, a)

    def test_no_completion_and_last_arrival(self):
        for c, a in (([[0], [0]], [[1], [1]]),
                     ([[1], [1]], [[3], [0]]),
                     ([[10]], [[2]])):
            with self.subTest(capacities=c, arrivals=a):
                r = run_simulation(c, a)
                self.assertEqual(r['delays'], [])
                self.assertEqual(r['delay_users'], [])
                self.assertEqual(r['completed'], 0)
                self.check_result(r, a)
        r = run_simulation([[2], [2]], [[0], [0]])
        self.assertEqual(r['delays'], [])
        self.assertEqual(r['remaining'], 0)

    def test_repeat_and_input_unchanged(self):
        c, a = [[3], [3], [3]], [[2], [1], [0]]
        first = run_simulation(c, a)
        self.assertEqual(first, run_simulation(c, a))
        self.assertEqual(c, [[3], [3], [3]])
        self.assertEqual(a, [[2], [1], [0]])

    def test_preserved_validation(self):
        with self.assertRaises(ValueError):
            run_simulation([], [])
        with self.assertRaises(TypeError):
            run_simulation([[True]], [[0]])
        with self.assertRaises(ValueError):
            run_simulation([[1]], [[0]], alpha=float('nan'))
        with self.assertRaises(ValueError):
            run_simulation([[1]], [[0]], policy='unknown')


if __name__ == '__main__':
    unittest.main(verbosity=2)
