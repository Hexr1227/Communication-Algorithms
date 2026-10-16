"""随机场景接入验收：校验配置、调用次数和真实结果。"""
import unittest
from unittest.mock import patch
import scenario


class ScenarioAcceptance(unittest.TestCase):
    def test_real_scene(self):
        before = scenario.run_demo()
        self.assertEqual(set(before), {'arrivals','capacities','results'})
        a, c, rows = before['arrivals'], before['capacities'], before['results']
        self.assertEqual(len(a), 100)
        self.assertEqual(len(c), 100)
        self.assertTrue(all(len(row)==4 for row in a+c))
        self.assertTrue(all(x in (0,2) for row in a for x in row))
        self.assertTrue(all(x in (1,4) for row in c for x in row))
        self.assertEqual(c[0], [4,4,1,1])
        self.assertEqual([r['policy'] for r in rows], ['rr','max_rate','pf','max_weight'])
        packets = sum(x > 0 for row in a for x in row)
        data = sum(map(sum, a))
        for r in rows:
            self.assertEqual(r['completed']+r['pending'], packets)
            self.assertAlmostEqual(r['throughput']*100+r['remaining'], data)
            if r['completed']:
                self.assertGreaterEqual(r['p95'], 1)
                self.assertGreaterEqual(r['max'], r['p95'])
        self.assertEqual(before, scenario.run_demo())

    def test_configuration_and_single_generation(self):
        with patch.object(scenario, 'generate_arrivals', wraps=scenario.generate_arrivals) as ga, \
             patch.object(scenario, 'generate_capacities', wraps=scenario.generate_capacities) as gc, \
             patch.object(scenario, 'compare_policies', wraps=scenario.compare_policies) as cp:
            result = scenario.run_demo(traffic_seed=21, channel_seed=32)
            ga.assert_called_once_with(users=4, normal_slots=20, burst_slots=30,
                recovery_slots=50, normal_p=0.1, burst_p=0.8, packet_size=2, seed=21)
            gc.assert_called_once_with(users=4, slots=100, good_capacity=4, bad_capacity=1,
                p_good_to_bad=0.1, p_bad_to_good=0.3,
                initial_good=[True,True,False,False], seed=32)
            self.assertEqual(cp.call_count, 1)
            args, kwargs = cp.call_args
            self.assertEqual(args[0] if args else kwargs['capacities'], result['capacities'])
            self.assertEqual(args[1] if len(args)>1 else kwargs['arrivals'], result['arrivals'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
