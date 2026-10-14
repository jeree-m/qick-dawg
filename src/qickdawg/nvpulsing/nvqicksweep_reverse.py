"""
NVQickSweepReverse
===========================
Subclass of NVQickSweep that walks a register DOWN through an
exponentially-decreasing set of values, instead of up. Used to test
whether long-run drift depends on delay time itself, or just on where
a point falls in the sweep order.

Does not modify NVQickSweep or int_exp_scale -- reuses NVQickSweep's
setup code by calling super().__init__ with scaling_mode='exponential',
then overrides get_sweep_pts() and update() to go in reverse.
"""

import numpy as np
from .nvqicksweep import NVQickSweep


def int_exp_scale_reverse(start, end, scaling_factor):
    '''
    Mirror of qickdawg.util.int_exp_scale: generates the same kind of
    exponentially scaled array, but stepping DOWN from 'start' to 'end'
    (subtraction instead of addition at each step). 'start' must be
    larger than 'end'.
    '''
    points = [start]
    numerator, denominator = scaling_factor.split('/')
    denominator = int(denominator)
    shift = int(np.log2(denominator))

    while points[-1] > end:
        x = int(points[-1])
        points.append(x - (x >> shift))

    return np.array(points)


class NVQickSweepReverse(NVQickSweep):
    '''
    Same as NVQickSweep(scaling_mode='exponential') but counts the
    register DOWN from 'start' to 'stop' instead of up.
    Pass the LARGE value as 'start' and the SMALL value as 'stop'.
    '''

    def __init__(self, prog, reg, start, stop, expts, label=None,
                 scaling_factor='', mw_channel=-1):
        super().__init__(prog, reg, start, stop, expts, label=label,
                          scaling_mode='exponential',
                          scaling_factor=scaling_factor, mw_channel=mw_channel)

    def get_sweep_pts(self):
        return int_exp_scale_reverse(self.start, self.stop, self.scaling_factor)

    def update(self):
        self.prog.bitwi(self.reg.page, self.temp_reg.addr, self.reg.addr, '>>', self.nshift)
        self.prog.math(self.reg.page, self.reg.addr, self.reg.addr, '-', self.temp_reg.addr)