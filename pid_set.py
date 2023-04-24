import math, logging
from . import heaters

KELVIN_TO_CELSIUS = -273.15
MAX_HEAT_TIME = 5.0
AMBIENT_TEMP = 25.
PID_PARAM_BASE = 255.

class PIDSet:
    def __init__(self, config):
        self.printer = config.get_printer()
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('PID_SET', self.cmd_PID_SET,
                               desc=self.cmd_PID_SET_help)
    cmd_PID_SET_help = "Set PID values on heater via GCode"
    def cmd_PID_SET(self, gcmd):
        heater_name = gcmd.get('HEATER')
        Kp = gcmd.get_float('KP')
        Ki = gcmd.get_float('KI')
        Kd = gcmd.get_float('KD')
        pheaters = self.printer.lookup_object('heaters')
        try:
            heater = pheaters.lookup_heater(heater_name)
        except self.printer.config_error as e:
            raise gcmd.error(str(e))
        self.printer.lookup_object('toolhead').get_last_move_time()
        
        new_control = ControlPID(heater, Kp, Ki, Kd)
        old_control = heater.set_control(new_control)
        


######################################################################
# Proportional Integral Derivative (PID) control algo
######################################################################

PID_SETTLE_DELTA = 1.
PID_SETTLE_SLOPE = .1

class ControlPID:
    def __init__(self, heater, Kp, Ki, Kd):
        self.heater = heater
        self.heater_max_power = heater.get_max_power()
        self.Kp = Kp / PID_PARAM_BASE
        self.Ki = Ki / PID_PARAM_BASE
        self.Kd = Kd / PID_PARAM_BASE
        self.min_deriv_time = heater.get_smooth_time()
        self.temp_integ_max = 0.
        if self.Ki:
            self.temp_integ_max = self.heater_max_power / self.Ki
        self.prev_temp = AMBIENT_TEMP
        self.prev_temp_time = 0.
        self.prev_temp_deriv = 0.
        self.prev_temp_integ = 0.
    def temperature_update(self, read_time, temp, target_temp):
        time_diff = read_time - self.prev_temp_time
        # Calculate change of temperature
        temp_diff = temp - self.prev_temp
        if time_diff >= self.min_deriv_time:
            temp_deriv = temp_diff / time_diff
        else:
            temp_deriv = (self.prev_temp_deriv * (self.min_deriv_time-time_diff)
                          + temp_diff) / self.min_deriv_time
        # Calculate accumulated temperature "error"
        temp_err = target_temp - temp
        temp_integ = self.prev_temp_integ + temp_err * time_diff
        temp_integ = max(0., min(self.temp_integ_max, temp_integ))
        # Calculate output
        co = self.Kp*temp_err + self.Ki*temp_integ - self.Kd*temp_deriv
        #logging.debug("pid: %f@%.3f -> diff=%f deriv=%f err=%f integ=%f co=%d",
        #    temp, read_time, temp_diff, temp_deriv, temp_err, temp_integ, co)
        bounded_co = max(0., min(self.heater_max_power, co))
        self.heater.set_pwm(read_time, bounded_co)
        # Store state for next measurement
        self.prev_temp = temp
        self.prev_temp_time = read_time
        self.prev_temp_deriv = temp_deriv
        if co == bounded_co:
            self.prev_temp_integ = temp_integ
    def check_busy(self, eventtime, smoothed_temp, target_temp):
        temp_diff = target_temp - smoothed_temp
        return (abs(temp_diff) > PID_SETTLE_DELTA
                or abs(self.prev_temp_deriv) > PID_SETTLE_SLOPE)
    def getControl(self):
        return ('Kp = {}/nKi = {}/nKd = {}'.format(self.Kp* PID_PARAM_BASE,
                                                     self.Ki* PID_PARAM_BASE,
                                                     self.Kd* PID_PARAM_BASE))



def load_config(config):
    return PIDSet(config)
