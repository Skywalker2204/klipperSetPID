# klipperSetPID
Especially for huge beds or partially heatable beds the PID settings may change with temperature.
The changing of the PID Values via the GCode is not yet implemented , hence a
small module to include in klipper extras was written. Just copy the pid_set.py file in your klippy/extras folder and change your printer.cfg file.
```
[pid_set]
```

With the enabled module you can use following command:

```
SET_PID HEATER=heater KI=100, KP=0.5, KD= 2000
```
Therefore, the control of your selected heater is changed
