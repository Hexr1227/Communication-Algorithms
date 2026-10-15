import copy
import ctypes as ct
import math
import unittest
from unittest.mock import patch
import student

C = [[2,1]] * 4
A = [[1,1],[1,0],[0,1],[0,0]]

class IntegrationAcceptance(unittest.TestCase):
    def test_known_paths_and_history(self):
        rr = student.run_simulation(C,A,'rr',0.5)
        self.assertEqual(rr, dict(selected=[None,0,1,0], served=[0,1,1,1],
            backlog=[[1,1],[1,1],[1,1],[0,1]], total_served=[2,1],
            completed=3, remaining=1, average=[0.6875,0.3125]))
        pf = student.run_simulation(C,A,'pf',0.5)
        self.assertEqual(pf, rr)
        for p in ('max_rate','max_weight'):
            with self.subTest(policy=p):
                r = student.run_simulation(C,A,p,0.5)
                self.assertEqual(r['selected'],[None,0,0,1])
                self.assertEqual(r['backlog'],[[1,1],[1,1],[0,2],[0,1]])
                self.assertEqual(r['average'],[0.4375,0.5625])
                self.assertEqual(r['completed'],3)

    def test_all_idle_decay(self):
        for p in ('rr','max_rate','pf','max_weight'):
            r = student.run_simulation([[0,0]]*3,[[1,2],[0,0],[0,0]],p,0.5)
            self.assertEqual(r['selected'],[None]*3)
            self.assertEqual(r['served'],[0]*3)
            self.assertEqual(r['remaining'],3)
            self.assertEqual(r['average'],[0.125,0.125])

    def test_policy_distinction(self):
        c=[[1,1],[2,1],[2,1]]
        a=[[2,10],[0,0],[0,0]]
        self.assertEqual(student.run_simulation(c,a,'max_rate')['selected'][1],0)
        self.assertEqual(student.run_simulation(c,a,'max_weight')['selected'][1],1)

    def test_validation(self):
        for c,a in [(None,[]),([1],[[1]]),([[True]],[[0]]),([[0]],[[1.0]]),([[0]],[(1,)])]:
            with self.subTest(c=c,a=a):
                with self.assertRaises(TypeError): student.run_simulation(c,a)
        for c,a in [([],[]),([[]],[[]]),([[1]],[]),([[1],[1,2]],[[0],[0]]),([[-1]],[[0]]),([[0]],[[2**32]])]:
            with self.subTest(c=c,a=a):
                with self.assertRaises(ValueError): student.run_simulation(c,a)
        with self.assertRaises(TypeError): student.run_simulation(C,A,policy=1)
        with self.assertRaises(ValueError): student.run_simulation(C,A,policy='unknown')
        for alpha in (True,'0.2',None):
            with self.subTest(alpha=alpha):
                with self.assertRaises(TypeError): student.run_simulation(C,A,alpha=alpha)
        for alpha in (0,-1,1.1,math.nan,math.inf):
            with self.subTest(alpha=alpha):
                with self.assertRaises(ValueError): student.run_simulation(C,A,alpha=alpha)

    def test_repeat_input_and_conservation(self):
        c=[[0,1],[4,1],[2,3],[0,0],[4,2]]
        a=[[3,2],[0,1],[2,0],[1,1],[0,3]]
        saved=copy.deepcopy((c,a))
        for policy in ('rr','max_rate','pf','max_weight'):
            r=student.run_simulation(c,a,policy)
            self.assertEqual(r,student.run_simulation(c,a,policy))
            self.assertEqual((c,a),saved)
            self.assertEqual(sum(r['total_served']),sum(r['served']))
            for u in range(2):
                self.assertEqual(sum(row[u] for row in a),r['total_served'][u]+r['backlog'][-1][u])
            self.assertEqual(r['remaining'],sum(r['backlog'][-1]))
            for t,pick in enumerate(r['selected']):
                if pick is None: self.assertEqual(r['served'][t],0)
                else:
                    self.assertIn(pick,(0,1))
                    self.assertLessEqual(r['served'][t],c[t][pick])

    def test_actual_c_call_and_errors(self):
        original=student.ct.CDLL
        loads=[]
        class CountedFunction:
            def __init__(self,fn): object.__setattr__(self,'fn',fn);object.__setattr__(self,'calls',0)
            def __setattr__(self,name,value): setattr(self.fn,name,value)
            def __getattr__(self,name): return getattr(self.fn,name)
            def __call__(self,*args):
                object.__setattr__(self,'calls',self.calls+1)
                return self.fn(*args)
        class Loaded:
            def __init__(self,lib): self.simulate_policy=CountedFunction(lib.simulate_policy)
        def load(*args,**kwargs):
            obj=Loaded(original(*args,**kwargs));loads.append(obj);return obj
        with patch.object(student.ct,'CDLL',side_effect=load):
            student.run_simulation(C,A)
        self.assertEqual(sum(obj.simulate_policy.calls for obj in loads),1)
        class FailedFunction:
            def __call__(self,*args): return 2
        class FailedLibrary:
            simulate_policy=FailedFunction()
        with patch.object(student.ct,'CDLL',return_value=FailedLibrary()):
            with self.assertRaises(RuntimeError): student.run_simulation(C,A)

if __name__=='__main__': unittest.main(verbosity=2)

