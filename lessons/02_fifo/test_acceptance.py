"""公开验收；不提供参考仿真实现。"""
import copy
import unittest
from student import simulate_fifo


class FifoAcceptance(unittest.TestCase):
    def test_partial_service_and_multiple_completions(self):
        r = simulate_fifo([0, 2, 2, 3], [[3, 1], [], [2], []])
        self.assertEqual(r, dict(served=[0, 2, 2, 2], backlog=[4, 2, 2, 0],
            completed=[(0, 0, 2, 2), (1, 0, 2, 2), (2, 2, 3, 1)], pending=[]))

    def test_fifo_does_not_overtake_large_packet(self):
        r = simulate_fifo([10, 1, 1], [[5, 1], [], []])
        self.assertEqual(r, dict(served=[0, 1, 1], backlog=[6, 5, 4],
            completed=[], pending=[(0, 0, 5, 3), (1, 0, 1, 1)]))

    def test_idle_and_last_slot_arrival(self):
        self.assertEqual(simulate_fifo([9], [[2, 3]]),
            dict(served=[0], backlog=[5], completed=[], pending=[(0, 0, 2, 2), (1, 0, 3, 3)]))
        self.assertEqual(simulate_fifo([0, 0], [[1], []]),
            dict(served=[0, 0], backlog=[1, 1], completed=[], pending=[(0, 0, 1, 1)]))
        self.assertEqual(simulate_fifo([4, 4], [[], []]),
            dict(served=[0, 0], backlog=[0, 0], completed=[], pending=[]))

    def test_empty(self):
        self.assertEqual(simulate_fifo([], []),
                         dict(served=[], backlog=[], completed=[], pending=[]))

    def test_validation(self):
        type_cases = [(None, []), ([], ()), ([True], [[]]),
                      ([1.0], [[]]), ([1], [None]), ([1], [[False]]),
                      ([1], [[1.5]]), ([1], [['2']])]
        for c, a in type_cases:
            with self.subTest(c=c, a=a):
                with self.assertRaises(TypeError): simulate_fifo(c, a)
        for c, a in [([1], []), ([-1], [[]]), ([1], [[0]]), ([1], [[-2]])]:
            with self.subTest(c=c, a=a):
                with self.assertRaises(ValueError): simulate_fifo(c, a)

    def test_inputs_unchanged_and_repeatable(self):
        c, a = [0, 3, 1, 2], [[2, 4], [1], [], [2]]
        saved = copy.deepcopy((c, a))
        first = simulate_fifo(c, a)
        self.assertEqual((c, a), saved)
        self.assertEqual(first, simulate_fifo(c, a))

    def test_conservation_and_capacity_across_prefixes(self):
        c, a = [0, 1, 3, 0, 7], [[3, 2], [1], [], [4], [2]]
        for end in range(1, len(c) + 1):
            with self.subTest(end=end):
                r = simulate_fifo(c[:end], a[:end])
                self.assertEqual(len(r['served']), end)
                self.assertEqual(len(r['backlog']), end)
                arrived = sum(sum(row) for row in a[:end])
                self.assertEqual(arrived, sum(r['served']) + r['backlog'][-1])
                self.assertEqual(sum(p[3] for p in r['pending']), r['backlog'][-1])
                for t, sent in enumerate(r['served']):
                    self.assertIs(type(sent), int)
                    self.assertGreaterEqual(sent, 0)
                    self.assertLessEqual(sent, c[t])
                    before = 0 if t == 0 else r['backlog'][t-1]
                    self.assertLessEqual(sent, before)
                    self.assertTrue(sent == c[t] or sent == before)
                ids = [p[0] for p in r['completed']] + [p[0] for p in r['pending']]
                self.assertEqual(ids, list(range(sum(len(row) for row in a[:end]))))
                for _, arrived_at, completed_at, delay in r['completed']:
                    self.assertGreater(completed_at, arrived_at)
                    self.assertEqual(delay, completed_at - arrived_at)


if __name__ == '__main__':
    unittest.main(verbosity=2)
