from .t1delaysweep import T1DelaySweep
from .nvqicksweep_reverse import NVQickSweepReverse, int_exp_scale_reverse


class T1DelaySweepReverse(T1DelaySweep):

    def initialize(self):

        self.check_cfg()
        self.setup_readout()
        self.cfg.adcs = [self.cfg.adc_channel]

        if self.cfg.test:
            self.declare_readout(ch=self.cfg.mw_readout_channel,
                                 freq=self.cfg.mw_fMHz,
                                 length=self.cfg.readout_integration_treg)
            self.cfg.adcs.append(self.cfg.mw_readout_channel)

        self.declare_gen(ch=self.cfg.mw_channel, nqz=self.cfg.mw_nqz)

        self.default_pulse_registers(
            ch=self.cfg.mw_channel,
            style='const',
            freq=self.cfg.mw_freg,
            length=self.cfg.mw_pi2_treg,
            gain=self.cfg.mw_gain)

        self.set_pulse_registers(ch=self.cfg.mw_channel, phase=0)

        self.delay_register = self.new_gen_reg(self.cfg.mw_channel,
                                               name='delay',
                                               init_val=self.cfg.delay_end_treg)

        # expts must match the REVERSE generator's actual point count, not cfg.nsweep_points
        n_points = len(int_exp_scale_reverse(self.cfg.delay_end_treg, self.cfg.delay_start_treg, self.cfg.scaling_factor))

        self.add_sweep(NVQickSweepReverse(
            self,
            self.delay_register,
            self.cfg.delay_end_treg,
            self.cfg.delay_start_treg,
            expts=n_points,
            scaling_factor=self.cfg.scaling_factor))

        self.synci(100)
        if (self.cfg.ddr4 is True) or (self.cfg.mr is True):
            self.trigger(ddr4=self.cfg.ddr4, mr=self.cfg.mr, adc_trig_offset=0)
        self.synci(100)

        if self.cfg.pre_init:
            self.trigger(
                pins=[self.cfg.laser_gate_pmod],
                width=self.cfg.laser_on_treg,
                adc_trig_offset=0
            )
            self.sync_all(self.cfg.laser_on_treg + self.cfg.relax_delay_treg)