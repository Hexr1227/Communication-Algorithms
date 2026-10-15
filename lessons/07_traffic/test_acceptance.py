import random
import unittest
from student import generate_arrivals

BASE=dict(users=2,normal_slots=2,burst_slots=3,recovery_slots=2,
          normal_p=0,burst_p=1,packet_size=3,seed=7)

class TrafficAcceptance(unittest.TestCase):
    def make(self,**changes):
        return generate_arrivals(**(BASE|changes))

    def test_phase_edges(self):
        self.assertEqual(self.make(),[[0,0],[0,0],[3,3],[3,3],[3,3],[0,0],[0,0]])
        self.assertEqual(self.make(normal_slots=0,burst_slots=1,recovery_slots=0),[[3,3]])
        self.assertEqual(self.make(normal_slots=1,burst_slots=0,recovery_slots=0),[[0,0]])
        self.assertEqual(self.make(normal_p=1,burst_p=0),[[3,3],[3,3],[0,0],[0,0],[0,0],[3,3],[3,3]])

    def test_seed_and_draw_order(self):
        # seed=1的前六次标准random()抽样，在p=0.5时的固定预期。
        args=dict(users=2,normal_slots=3,burst_slots=0,recovery_slots=0,
                  normal_p=0.5,burst_p=0.5,packet_size=2,seed=1)
        self.assertEqual(generate_arrivals(**args),[[2,0],[0,2],[2,2]])
        self.assertEqual(generate_arrivals(**args),generate_arrivals(**args))
        # 概率端点仍消耗一次抽样，第三与第四次抽样决定突发段。
        self.assertEqual(self.make(normal_slots=1,burst_slots=1,recovery_slots=0,
                                   burst_p=0.5,packet_size=2,seed=1),[[0,0],[0,2]])

    def test_global_rng_untouched(self):
        before=random.getstate()
        self.make(normal_p=0.3,burst_p=0.7)
        self.assertEqual(random.getstate(),before)

    def test_independent_rows_and_bounds(self):
        rows=self.make(normal_p=1,burst_p=1,packet_size=2**32-1)
        self.assertEqual(len(rows),7)
        self.assertTrue(all(len(row)==2 for row in rows))
        rows[0][0]=0
        self.assertEqual(rows[1][0],2**32-1)
        rows=self.make(normal_p=0.4,burst_p=0.7)
        self.assertTrue(all(type(x) is int and x in (0,3) for row in rows for x in row))

    def test_bad_types(self):
        for name in ('users','normal_slots','burst_slots','recovery_slots','packet_size','seed'):
            for value in (True,1.5,'1',None):
                with self.subTest(name=name,value=value):
                    with self.assertRaises(TypeError): self.make(**{name:value})
        for name in ('normal_p','burst_p'):
            for value in (True,'0.5',None):
                with self.subTest(name=name,value=value):
                    with self.assertRaises(TypeError): self.make(**{name:value})

    def test_bad_values(self):
        cases=[dict(users=0),dict(users=-1),dict(normal_slots=-1),dict(burst_slots=-1),
               dict(recovery_slots=-1),dict(packet_size=0),dict(packet_size=2**32),
               dict(normal_slots=0,burst_slots=0,recovery_slots=0)]
        for name in ('normal_p','burst_p'):
            for value in (-0.1,1.1,float('nan'),float('inf'),-float('inf')):
                cases.append({name:value})
        for change in cases:
            with self.subTest(change=change):
                with self.assertRaises(ValueError): self.make(**change)
        self.make(seed=-8)

if __name__=='__main__': unittest.main(verbosity=2)
