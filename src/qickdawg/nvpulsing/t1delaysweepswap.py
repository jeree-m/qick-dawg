"""
T1DelaySweepSwap
=======================================================================
Subclass of T1DelaySweep that swaps which pulse sequence runs first
within each rep: MW pulse is measured FIRST, no-MW is measured SECOND
(opposite of T1DelaySweep's normal order). Used to test whether the
signal1/signal2 crossing at long delay is tied to the MW pulse itself,
or just to being measured second within a rep.

IMPORTANT: because signal1/signal2 are assigned by readout ORDER (not
by whether MW was involved), the labels flip meaning in this class:
    signal1 = WITH MW (measured first)
    signal2 = NO MW (measured second)
This is the opposite of T1DelaySweep, where signal1 = no MW, signal2 = MW.

Only body() is overridden -- initialize() (the delay sweep setup) is
inherited unchanged, so this class uses the normal forward delay sweep.
"""

from .t1delaysweep import T1DelaySweep


class T1DelaySweepSwap(T1DelaySweep):

    def body(self):
        ## First pulse sequence (swapped: MW first)
        ## pi(x) - delay - readout
        self.pulse(ch=self.cfg.mw_channel)
        self.pulse(ch=self.cfg.mw_channel)
        self.sync_all()
        # delay
        self.sync(self.delay_register.page, self.delay_register.addr)
        # readout
        self.sync_all(self.cfg.mw_readout_delay_treg)
        self.ttl_readout()

        ## Second pulse sequence (swapped: no MW second)
        ## Nothing - delay - readout
        self.synci(self.cfg.mw_pi2_treg * 2)
        # delay
        self.sync(self.delay_register.page, self.delay_register.addr)
        # readout
        self.sync_all(self.cfg.mw_readout_delay_treg)
        self.ttl_readout()