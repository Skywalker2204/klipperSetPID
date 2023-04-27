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
The old Marlin Gcode M301 and M304 can be implementet via a GCode macro:
```
[gcode_macro M301]
description: Set Extruder PID values
gcode:
  {% set ki = params.I|float %}
  {% set kp = params.P|float %}
  {% set kd = params.D|float %}
  {% set ext_index = params.E|default(0)|flaot %}
  
  {% if ext_index == 1 %}
    {% set ext = extruder1 %}
  {% else %}
    {% set ext = extruder %}
  {% endif %}
  
  SET_PID HEATER={ext} KI={ki} KP={kp} KD={kd}
  
[gcode_macro M304]
description: Set bed PID values
gcode:
  {% set ki = params.I|float %}
  {% set kp = params.P|float %}
  {% set kd = params.D|float %}
  
  SET_PID HEATER=heater_bed KI={ki} KP={kp} KD={kd}
```
