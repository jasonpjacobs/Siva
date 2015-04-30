import unittest
import numpy as np

from jase.wave.wave import Wave

import pdb

epsilon =  np.finfo(float).eps

class TestWave(unittest.TestCase):

    def setUp(self):
        x = np.arange(10)

        self.a = Wave(x=x, y=np.arange(0,10), name="A")
        self.b = Wave(x=x, y=np.arange(-10,10), name="B")

        self.r = Wave(x=x, y=np.random.rand(10), name="Random")
        self.c = Wave(x=x, y=x+1, name="B")
        self.d = Wave(y=np.arange(-10, 11))
        self.ones = Wave(x=x, y=np.ones(10), name="Ones")
        self.zeros = Wave(x=x, y=np.zeros(10), name="Zeros")

    def test_creation(self):
        vals = np.random.rand(10)
        x = range(len(vals))
        y = vals
        name = "Test Wave"

        for w in [Wave(x,y, name="x,y"), Wave(x=x, y=y,name=["x=x,y=y"]), Wave([x,y],name="[x,y]")]:
            self.assertTrue( (x == w.x).all(), w.name)
            self.assertTrue( (y == w.y).all(), w.name)

    def test_eq(self):
        a=self.a
        self.assertEqual(a, a)
        self.assertTrue( (a == a).y.all())

        w = a*1
        self.assertTrue(  (a == a).y.all())
        self.assertFalse(a is w)

    def test_numpy_ops(self):

        # True/False
        self.assertTrue(self.ones.all())
        self.assertFalse(self.zeros.all())

        self.assertFalse(self.zeros.any())
        self.assertTrue(self.ones.any())

        # peak to peak
        self.assertEqual(self.ones.ptp(), 0)
        self.assertEqual(self.c.ptp(), 9)

        self.assertEqual(self.ones.sum(), 10)
        self.assertEqual(self.zeros.sum(), 0)

        import math
        self.assertEqual(self.a.cumsum()[9].y, 45)
        self.assertFalse(self.zeros.cumsum().all())

        r=self.a.clip(2,5)
        self.assertEqual(r.ptp(),3)

        self.assertEqual(self.d.min(), -10)
        self.assertEqual(self.d.max(), 10)
        self.assertEqual(self.d.mean(), 0)

        self.assertEqual(self.ones.std(), 0)
        self.assertEqual(self.ones.var(), 0)



    def test_math_ops(self):
        from operator import mul, truediv, abs
        a, b = self.c, self.c
        for op in (mul, truediv, ):
            result = op(a,b)
            self.assertTrue( (result.y == op(a.y, b.y)).all())

        for op in (abs,):
            result = op(a)

    def test_unary_ops(self):
        c=self.c
        d = self.d
        e = abs(d)
        #self.assertEqual(e[0],  -1*d[0][0])

    def test_indexing(self):
        c = self.c

        result = c[:4]
        self.assertTrue((result.y == np.arange(5)[1:]).all())

        result = c[4:]
        self.assertTrue((result.y == np.arange(5,11)).all())


    def test_equality_ops(self):

        self.assertTrue((self.ones == self.ones).all())
        self.assertTrue((self.zeros == self.zeros).all())
        self.assertTrue((self.a == self.a).all())

        self.assertFalse((self.ones != self.ones).all())
        self.assertTrue((self.zeros != self.ones).all())
        self.assertFalse((self.a != self.a).all())

        self.assertTrue((self.ones > self.zeros).y.all())
        self.assertFalse((self.ones < self.zeros).y.all())

        self.assertTrue((self.ones >= self.zeros).y.all())
        self.assertFalse((self.ones <= self.zeros).y.all())

        self.assertTrue((self.ones > 0.5).y.all())
        self.assertTrue((self.zeros < 0.5).y.all())

        self.assertTrue((self.ones >= 0.5).y.all())
        self.assertTrue((self.zeros <= 0.5).y.all())

        self.assertTrue((self.ones >= self.ones).y.all())
        self.assertTrue((self.zeros <= self.zeros).y.all())


    def test_interpolation(self):
        import scipy
        w = Wave([0,1])
        n = w(0.5)
        self.assertEqual(n[0].y, 0.5)

        n = w([0.2, 0.7])
        self.assertEqual(n[0].y, 0.2)
        self.assertEqual(n[1].y, 0.7)

        w = Wave([0,1,0], interp='step')
        self.assertEqual(w(0.2)[0].y, 0.0)
        self.assertEqual(w(1.8)[0].y, 1.0)


    def test_sample(self):

        w = Wave([0,1])
        n = w.sample(0.1)

        self.assertEqual(len(n), 11)
        self.assertEqual(n.x[1] - n.x[0], 0.1)

        for i in range(1,13):
            v = 1/i
            self.assertTrue( n(v).y - w(v).y < epsilon)


    def test_minmax(self):
        a = self.a
        self.assertEqual(a.xmin(), 0)
        self.assertEqual(a.xmax(), 9)

        d=self.d
        self.assertEqual(d.xmin(), 0)
        self.assertEqual(d.xmax(), 20)

    def test_fft(self):
        epsilon =  np.finfo(float).eps

        for w in (self.d,):
            f = w.fft()
            t = f.ifft()
            self.assertTrue( ((w.x - t.x) < epsilon).all())

    def test_cross(self):
        w = Wave(y=[0,1,1,1,0,0,1,0], interp="linear")

        x = w.cross(0.5, edge="rising")
        self.assertTrue(  (x == [ 0.5, 5.5]).all())

        x = w.cross(0.5, edge="falling")
        self.assertTrue(  (x == [ 3.5, 6.5]).all())

        x = w.cross(0.5, edge="both")
        self.assertTrue(  (x == [ 0.5, 3.5, 5.5, 6.5]).all())

        x = w.cross(0.5, edge="either")
        self.assertTrue(  (x == [ 0.5, 3.5, 5.5, 6.5]).all())

        x = w.cross(10.5, edge="both")
        self.assertTrue(  (x == [ ]).all())

        x = w.cross(1, edge="both")
        self.assertTrue(  (x == [ 1., 3.,  6.,  6.]).all())

    def test_diff_cumsum(self):
        t = np.linspace(-np.pi/2,np.pi/2,2000)
        y = np.sin(2*np.pi*1*t)
        sin = Wave(t,y,name="sin")
        b  = sin.difference()
        c = b.cumsum()
        dy = (sin[0].y - c[0].y)
        d = sin-dy
        self.assertTrue( (d.x[:-1] == b.x).all())






