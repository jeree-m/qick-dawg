'''
GateSweep
=======================================================================
An NVAveragerProgram class that characterizes how sharp the laser's
turn-ON or turn-OFF edge actually is, by sweeping a narrow acquisition
gate's delay across that edge and recording counts vs. delay.
'''

from .nvaverageprogram import NVAveragerProgram
from .nvqicksweep import NVQickSweep

import matplotlib.pyplot as plt


class GateSweep(NVAveragerProgram):
    '''
    Sweeps a narrow acquisition gate's delay across one edge of a fixed
    laser pulse, to measure that edge's sharpness.
    '''

    required_cfg = [
        "adc_channel",
        "mw_channel",
        "mw_nqz",
        "laser_gate_pmod",
        "laser_on_treg",
        "pre_offset_treg",
        "readout_integration_treg",
        "delay_start_treg",
        "delay_end_treg",
        "nsweep_points",
        "relax_delay_treg",
        "reps"]

    def initialize(self):
        self.check_cfg()

        self.setup_readout()
        self.cfg.adcs = [self.cfg.adc_channel]

        self.declare_gen(ch=self.cfg.mw_channel, nqz=self.cfg.mw_nqz)

        self.delay_register = self.new_gen_reg(
            self.cfg.mw_channel,
            name='delay',
            init_val=self.cfg.delay_start_treg)

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

    def body(self):
        self.trigger(
            pins=[self.cfg.laser_gate_pmod],
            width=self.cfg.laser_on_treg,
            adc_trig_offset=0,
            t=self.cfg.pre_offset_treg)

        self.sync(self.delay_register.page, self.delay_register.addr)

        self.trigger(
            adcs=self.cfg.adcs,
            width=self.cfg.readout_integration_treg,
            adc_trig_offset=0)

        self.wait_all()
        self.sync_all(self.cfg.relax_delay_treg)

    def acquire(self, raw_data=False, *arg, **kwarg):
        data = super().acquire(readouts_per_experiment=1, *arg, **kwarg)
        return data

    def plot_sequence(cfg=None):
        if cfg is None:
            plt.figure(figsize=(10, 4))
            plt.axis('off')
            plt.text(0.05, 0.6, "Laser on for config.laser_on_t#, starting at t=config.pre_offset_t#", fontsize=12)
            plt.text(0.05, 0.4,
                      "Gate (width config.readout_integration_t#) swept from "
                      "config.delay_start_t# to config.delay_end_t#", fontsize=12)
            plt.title("GateSweep Pulse Sequence", fontsize=16)
        else:
            plt.figure(figsize=(10, 4))
            plt.axis('off')
            plt.text(0.05, 0.6, "Laser on for {} us, starting at t={} ns".format(cfg.laser_on_tus, cfg.pre_offset_tns), fontsize=12)
            plt.text(0.05, 0.4,
                      "Gate (width {} us) swept from {} us to {} us in {} steps".format(
                          str(cfg.readout_integration_tus)[:5], str(cfg.delay_start_tus)[:5],
                          str(cfg.delay_end_tus)[:5], cfg.nsweep_points), fontsize=12)
            plt.title("GateSweep Pulse Sequence", fontsize=16)