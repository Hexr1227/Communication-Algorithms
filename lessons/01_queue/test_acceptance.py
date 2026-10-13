"""Public acceptance tests. No reference implementation is included."""
import unittest
from student import advance_queue


class QueueAcceptance(unittest.TestCase):
    def test_hand_calculated_cases(self):
        cases = [
            ((3, 2, 4), (2, 5)),
            ((0, 10, 4), (0, 4)),
            ((5, 0, 2), (0, 7)),
            ((2, 10, 3), (2, 3)),
            ((4, 4, 0), (4, 0)),
            ((0, 0, 0), (0, 0)),
            ((1, 10, 0), (1, 0)),
        ]
        for inputs, expected in cases:
            with self.subTest(inputs=inputs):
                self.assertEqual(advance_queue(*inputs), expected)

    def test_input_types(self):
        for position in range(3):
            for invalid in (True, False, 1.0, '1', None, [], {}):
                args = [1, 1, 1]
                args[position] = invalid
                with self.subTest(position=position, invalid=repr(invalid)):
                    with self.assertRaises(TypeError):
                        advance_queue(*args)

    def test_negative_values(self):
        for position in range(3):
            args = [1, 1, 1]
            args[position] = -1
            with self.subTest(position=position):
                with self.assertRaises(ValueError):
                    advance_queue(*args)

    def test_large_python_integers(self):
        value = 10**50
        self.assertEqual(advance_queue(value, value - 1, value), (value - 1, value + 1))

    def test_small_domain_physical_properties(self):
        for q in range(7):
            for c in range(7):
                for a in range(5):
                    with self.subTest(q=q, c=c, a=a):
                        result = advance_queue(q, c, a)
                        self.assertIs(type(result), tuple)
                        self.assertEqual(len(result), 2)
                        sent, after = result
                        self.assertIs(type(sent), int)
                        self.assertIs(type(after), int)
                        self.assertGreaterEqual(sent, 0)
                        self.assertLessEqual(sent, q)
                        self.assertLessEqual(sent, c)
                        self.assertGreaterEqual(after, 0)
                        self.assertEqual(q + a, sent + after)
                        # Work-conserving: service leaves either no old data
                        # or no unused capacity. New arrivals are excluded.
                        self.assertTrue(sent == q or sent == c)

    def test_new_arrivals_cannot_change_current_service(self):
        results = [advance_queue(3, 2, a) for a in (0, 1, 10)]
        self.assertEqual([r[0] for r in results], [2, 2, 2])


if __name__ == '__main__':
    unittest.main(verbosity=2)
