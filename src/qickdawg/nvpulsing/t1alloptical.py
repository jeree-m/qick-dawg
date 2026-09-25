from .nvaverageprogram import NVAveragerProgram
from .nvqicksweep import NVQickSweep


class T1AllOptical(NVAveragerProgram):
    '''
    All-optical T1: laser polarize -> dark delay -> laser readout, no mw
    '''
    required_cfg = [
        "adc_channel",
        "readout_integration_treg",
        "mw_channel",       # only used to host the delay register, never pulsed
        "mw_nqz",
        "scaling_mode",
        "delay_start_treg",
        "delay_end_treg",
        "nsweep_points",
        "pre_init",
        "laser_gate_pmod",
        "laser_on_treg",
        "relax_delay_treg",
        "reps",
        "readout_reference_start_treg",
        "laser_readout_offset_treg",
        "mw_readout_delay_treg"]

    def initialize(self):
        self.check_cfg()
        self.setup_readout()
        self.cfg.adcs = [self.cfg.adc_channel]

        self.declare_gen(ch=self.cfg.mw_channel, nqz=self.cfg.mw_nqz)  # needed for delay register

        self.delay_register = self.new_gen_reg(self.cfg.mw_channel,
                                               name='delay',
                                               init_val=self.cfg.delay_start_treg)

        if self.cfg.scaling_mode == 'exponential':
            self.add_sweep(NVQickSweep(
                self,
                self.delay_register,
                self.cfg.delay_start_treg,
                self.cfg.delay_end_treg,
                expts=self.cfg.nsweep_points,
                scaling_mode=self.cfg.scaling_mode,
                scaling_factor=self.cfg.scaling_factor))
        elif self.cfg.scaling_mode == 'linear':
            self.add_sweep(NVQickSweep(
                self,
                self.delay_register,
                self.cfg.delay_start_treg,
                self.cfg.delay_end_treg,
                self.cfg.nsweep_points))

        self.synci(100)
        if (self.cfg.ddr4 is True) or (self.cfg.mr is True):
            self.trigger(ddr4=self.cfg.ddr4, mr=self.cfg.mr, adc_trig_offset=0)
        self.synci(100)

        if self.cfg.pre_init:  # polarize before the first shot
            self.trigger(pins=[self.cfg.laser_gate_pmod],
                         width=self.cfg.laser_on_treg,
                         adc_trig_offset=0)
            self.sync_all(self.cfg.laser_on_treg + self.cfg.relax_delay_treg)

    def body(self):
        # sequence 1: dark delay -> readout (readout laser also re-polarizes)
        self.sync(self.delay_register.page, self.delay_register.addr)
        self.sync_all(self.cfg.mw_readout_delay_treg)
        self.ttl_readout()

        # sequence 2: identical copy, keeps 4 readouts/experiment
        self.sync(self.delay_register.page, self.delay_register.addr)
        self.sync_all(self.cfg.mw_readout_delay_treg)
        self.ttl_readout()

    def acquire(self, raw_data=False, *arg, **kwarg):
        data = super().acquire(readouts_per_experiment=4, *arg, **kwarg)
        if raw_data is False:
            data = self.analyze_pulse_sequence(data)
        return data