---
summary: "\"Common Industrial Scenarios\""
read_when: ["["skill"]"]
---
# Common Industrial Scenarios

## Fault Scenarios

### VFD Fault
- VFD_Faulted = TRUE, VFD_Ready = FALSE
- Overload may trip (Overload_OK = FALSE)
- Fault latches, system stops, needs manual reset
- Common on conveyors, pumps, fans

### E-Stop
- EStop_OK = FALSE (NC circuit opens)
- Everything downstream drops: Safety_OK → System_Ready → outputs
- All VFDs stop, all solenoids de-energize

### Overload Trip
- Motor_Overload_OK = FALSE
- Usually latches a fault
- Motor stops, downstream logic drops

### Sensor Failure
- Proximity/photoelectric reads stuck TRUE or stuck FALSE
- Can cause: jam detection false alarm, product miscount, diverter malfunction
- May not trigger a fault — just wrong behavior

### Communication Loss
- Produced/Consumed tag data goes stale
- Module fault bit may set
- Downstream logic sees last known values (dangerous)

### Safety Guard Open
- Guard_Door_Closed = FALSE
- Safety relay drops
- Zone or whole system stops depending on safety zone design

### Air Pressure Loss
- Air_Pressure_OK = FALSE
- Pneumatic solenoids can't actuate
- Cylinders may drift to unpowered position

### Timer Expired / Not Starting
- Timer.EN = FALSE (not enabled — upstream condition not met)
- Timer.TT = TRUE but Timer.DN = FALSE (still timing)
- Timer.DN = TRUE (done — downstream should react)

## System Architectures

### Simple Conveyor Line
- 2-4 conveyors in series
- Each has: VFD, overload, entry/exit proxes
- Master start/stop from HMI
- Stack light (green/red/amber)

### Palletizer
- Infeed conveyor → layer forming → layer pick → stack → outfeed
- Multiple interlocks between zones
- Heavy use of timers and sequencing
- Safety zones around robot

### Packaging Machine
- Product detect → fill → seal → label → reject
- High-speed timing critical
- Encoder-based tracking
- Reject gate solenoid

### Material Handling / Sortation
- Main conveyor → multiple divert points
- Barcode scanner triggers divert
- Each divert has confirm sensor
- Jam detection on each lane

### Pump Station
- Multiple pumps (lead/lag)
- Level sensors (analog)
- Pressure switches
- VFDs with speed feedback
- Auto-start on level, auto-stop on level

## Tag Naming Conventions (common patterns)
- `{Equipment}_{Function}` — e.g., Conv1_VFD_Run, Pump2_Start
- `{Area}_{Equipment}_{Signal}` — e.g., Zone3_Motor1_Overload_OK
- HMI tags often prefixed: `HMI_Start_PB`, `HMI_Speed_SP`
- Status/feedback: `_Sts`, `_Fbk`, `_Ready`, `_Faulted`, `_OK`
- Commands: `_Cmd`, `_Run`, `_Start`, `_Stop`, `_Reset`
- Faults: `_Fault`, `_Faulted`, `_Alarm`, `_Trip`

## Realistic Tag Value Patterns

### Running Normally
- Safety_OK = TRUE, System_Ready = TRUE, System_Running = TRUE
- VFD_Run = TRUE, VFD_Ready = TRUE, VFD_Faulted = FALSE
- Overload_OK = TRUE
- Stack_Light_Green = TRUE, Stack_Light_Red = FALSE

### Faulted State
- System_Faulted = TRUE, System_Running = FALSE
- Fault_Latch = TRUE
- The specific fault source is TRUE (e.g., VFD2_Faulted = TRUE)
- Everything downstream from fault is FALSE
- Stack_Light_Red = TRUE, Alarm_Horn = TRUE

### Idle / Stopped
- System_Ready = TRUE but System_Running = FALSE
- All outputs FALSE
- All permissives TRUE
- HMI_Start_PB = FALSE (no one pressed start)

### Partial Fault
- One zone faulted, others running
- Zone_Fault = TRUE only for affected zone
- Other zones may continue depending on design
