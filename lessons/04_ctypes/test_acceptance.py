import copy
import ctypes as ct
from pathlib import Path
import unittest
from unittest.mock import patch
import student


class BindingAcceptance(unittest.TestCase):
    def test_real_c_call_and_signature(self):
        original = student.ct.CDLL
        loads = []
        def tracked(*args, **kwargs):
            lib = original(*args, **kwargs)
            loads.append(lib)
            return lib
        with patch.object(student.ct, 'CDLL', side_effect=tracked):
            r = student.run_fifo([0, 2, 2, 3], [3, 0, 2, 0])
        self.assertTrue(loads, '必须加载并调用 C 内核')
        self.assertEqual(r, dict(served=[0,2,1,2], backlog=[3,1,2,0], delays=[2,1], remaining=0))
        u32, u64, sz = ct.c_uint32, ct.c_uint64, ct.c_size_t
        expected = [sz, ct.POINTER(u32), ct.POINTER(u32), ct.POINTER(u32),
                    ct.POINTER(u64), ct.POINTER(sz), ct.POINTER(sz),
                    ct.POINTER(u64), ct.POINTER(sz), ct.POINTER(u32)]
        fn = loads[-1].simulate_fifo_c
        self.assertEqual(list(fn.argtypes), expected)
        self.assertIs(fn.restype, ct.c_int)

    def test_partial_and_pending(self):
        self.assertEqual(student.run_fifo([9,1,1], [5,1,0]),
            dict(served=[0,1,1], backlog=[5,5,4], delays=[], remaining=4))

    def test_zero_and_empty(self):
        self.assertEqual(student.run_fifo([], []), dict(served=[], backlog=[], delays=[], remaining=0))
        self.assertEqual(student.run_fifo([0,0], [1,0]),
            dict(served=[0,0], backlog=[1,1], delays=[], remaining=1))

    def test_uint32_limit_and_uint64_total(self):
        m = 2**32 - 1
        self.assertEqual(student.run_fifo([0,0,0], [m,m,1]),
            dict(served=[0,0,0], backlog=[m,2*m,2*m+1], delays=[], remaining=2*m+1))
        self.assertEqual(student.run_fifo([0,m], [m,0])['delays'], [1])

    def test_validation(self):
        for c,a in [(None,[]), ([],()), ([True],[0]), ([0],[False]), ([1.0],[0]), ([0],['1'])]:
            with self.subTest(c=c,a=a):
                with self.assertRaises(TypeError): student.run_fifo(c,a)
        for c,a in [([1],[]), ([-1],[0]), ([0],[-1]), ([2**32],[0]), ([0],[2**32])]:
            with self.subTest(c=c,a=a):
                with self.assertRaises(ValueError): student.run_fifo(c,a)

    def test_repeatability_inputs_and_path(self):
        self.assertEqual(Path(student.DLL_PATH), Path(student.__file__).resolve().with_name('fifo_core.dll'))
        c,a = [0,2,1], [3,2,0]
        saved = copy.deepcopy((c,a))
        first = student.run_fifo(c,a)
        self.assertEqual(first, student.run_fifo(c,a))
        self.assertEqual((c,a), saved)
        self.assertEqual(sum(a), sum(first['served']) + first['remaining'])

    def test_nonzero_c_status_raises(self):
        class FailedFunction:
            def __call__(self, *args): return 2
        class FakeLibrary:
            simulate_fifo_c = FailedFunction()
        with patch.object(student.ct, 'CDLL', return_value=FakeLibrary()):
            with self.assertRaises(RuntimeError): student.run_fifo([0], [1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
