# klipperSetPID
small module to include in klipper extras to enable PID setting via gCode

include [pid_set] in your config file and the command
SET_PID HEATER=heater KI=, KP=, KD= will work and set a new control mecahnism to your heater.
