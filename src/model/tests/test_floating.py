from model.floating import *

class TestFloatSeqDict:

    def test(self):
        d: FloatSeqDict[tuple[float, float], int] = FloatSeqDict(1e-7)
        d[(1.0, 1.0)] = 1
        assert d[(1.0, 1.0)] == 1
        d.setdefault((2.0, 2.0), 2)
        assert d[(2.0, 2.0)] == 2
        d.setdefault((1.0, 1.0), 2)
        assert d[(1.0, 1.0)] == 1