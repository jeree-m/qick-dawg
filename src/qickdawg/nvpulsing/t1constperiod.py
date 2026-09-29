from .t1delaysweep import T1DelaySweep

class T1ConstPeriod(T1DelaySweep):
    def initialize(self):
        super().initialize()
        self.pad = self.new_gen_reg(self.cfg.mw_channel, name='pad', init_val=0)
        assert self.pad.page == self.delay_register.page  # math needs same page

    def run_pass(self, mw_on):
        # pad = period - delay, so every pass has the same length
        self.regwi(self.pad.page, self.pad.addr, self.cfg.period_treg)
        self.math(self.pad.page, self.pad.addr, self.pad.addr, '-', self.delay_register.addr)
        self.sync(self.pad.page, self.pad.addr)

        # re-polarize after the pad
        self.trigger(pins=[self.cfg.laser_gate_pmod], width=self.cfg.laser_on_treg, adc_trig_offset=0)
        self.sync_all(self.cfg.laser_on_treg + self.cfg.relax_delay_treg)

        # MW slot (same as T1DelaySweep)
        if mw_on:
            self.pulse(ch=self.cfg.mw_channel)
            self.pulse(ch=self.cfg.mw_channel)
            self.sync_all()
        else:
            self.synci(self.cfg.mw_pi2_treg * 2)

        # delay + readout (same as T1DelaySweep)
        self.sync(self.delay_register.page, self.delay_register.addr)
        self.sync_all(self.cfg.mw_readout_delay_treg)
        self.ttl_readout()

    def body(self):
        self.run_pass(mw_on=False)  # signal1, reference1
        self.run_pass(mw_on=True)   # signal2, reference2