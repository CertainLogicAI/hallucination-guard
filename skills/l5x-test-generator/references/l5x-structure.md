---
summary: "\"L5X File Structure Reference\""
read_when: ["["skill"]"]
---
# L5X File Structure Reference

## Overview
L5X is Allen-Bradley's XML export format for ControlLogix/CompactLogix controllers. Exported from Studio 5000 via File → Save As → L5X.

## Root Element
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="34.00" 
  TargetName="ControllerName" TargetType="Controller" 
  ContainsContext="true" ExportDate="Tue Mar 25 14:00:00 2026"
  ExportOptions="References NoRawData L5KData DecoratedData Context Dependencies ForceProtectedEncoding AllProjDocTrans">
```

## Controller
```xml
<Controller Use="Target" Name="My_Controller" ProcessorType="1756-L83E" MajorRev="34" MinorRev="11">
```

### Common Processor Types
| Catalog | Description |
|---------|-------------|
| 1756-L83E | ControlLogix L8 |
| 1756-L83ES | GuardLogix (safety) |
| 1756-L73 | ControlLogix L7 |
| 1769-L30ERM | CompactLogix |
| 1769-L33ER | CompactLogix |
| 5069-L306ER | CompactLogix 5380 |

## Tags with Data Values
Tags can include live values when exported while online. Two formats:

### Simple BOOL
```xml
<Tag Name="Motor_Run" TagType="Base" DataType="BOOL" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
  <Description><![CDATA[Motor run command]]></Description>
  <Data Format="L5K"><![CDATA[1]]></Data>
  <Data Format="Decorated"><DataValue DataType="BOOL" Radix="Decimal" Value="1"/></Data>
</Tag>
```

### Simple DINT
```xml
<Tag Name="Counter_Val" TagType="Base" DataType="DINT" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
  <Data Format="L5K"><![CDATA[42]]></Data>
  <Data Format="Decorated"><DataValue DataType="DINT" Radix="Decimal" Value="42"/></Data>
</Tag>
```

### Simple REAL
```xml
<Tag Name="Temperature" TagType="Base" DataType="REAL" Radix="Float" Constant="false" ExternalAccess="Read/Write">
  <Data Format="L5K"><![CDATA[72.5]]></Data>
  <Data Format="Decorated"><DataValue DataType="REAL" Radix="Float" Value="72.5"/></Data>
</Tag>
```

### Structure (UDT or built-in)
```xml
<Tag Name="Timer1" TagType="Base" DataType="TIMER" Constant="false" ExternalAccess="Read/Write">
  <Data Format="Decorated">
    <Structure DataType="TIMER">
      <DataValueMember Name="PRE" DataType="DINT" Radix="Decimal" Value="5000"/>
      <DataValueMember Name="ACC" DataType="DINT" Radix="Decimal" Value="3200"/>
      <DataValueMember Name="EN" DataType="BOOL" Value="1"/>
      <DataValueMember Name="TT" DataType="BOOL" Value="1"/>
      <DataValueMember Name="DN" DataType="BOOL" Value="0"/>
    </Structure>
  </Data>
</Tag>
```

### COUNTER structure
```xml
<Tag Name="Counter1" TagType="Base" DataType="COUNTER" Constant="false" ExternalAccess="Read/Write">
  <Data Format="Decorated">
    <Structure DataType="COUNTER">
      <DataValueMember Name="PRE" DataType="DINT" Radix="Decimal" Value="10"/>
      <DataValueMember Name="ACC" DataType="DINT" Radix="Decimal" Value="7"/>
      <DataValueMember Name="CU" DataType="BOOL" Value="1"/>
      <DataValueMember Name="CD" DataType="BOOL" Value="0"/>
      <DataValueMember Name="DN" DataType="BOOL" Value="0"/>
      <DataValueMember Name="OV" DataType="BOOL" Value="0"/>
      <DataValueMember Name="UN" DataType="BOOL" Value="0"/>
    </Structure>
  </Data>
</Tag>
```

## Modules (I/O)
```xml
<Module Name="DI_Card" CatalogNumber="1756-IB16" Vendor="1" ProductType="7" Major="3" Minor="1" ParentModule="Local" ParentModPortId="1">
  <Ports><Port Id="1" Address="1" Type="ICP"/></Ports>
</Module>
```

### Common Module Catalog Numbers
| Catalog | Type |
|---------|------|
| 1756-IB16 | 16-pt Digital Input |
| 1756-IB32 | 32-pt Digital Input |
| 1756-OB16E | 16-pt Digital Output |
| 1756-OB32 | 32-pt Digital Output |
| 1756-IF8 | 8-ch Analog Input |
| 1756-OF8 | 8-ch Analog Output |
| 22-COMM-E | PowerFlex VFD Comms |
| 1756-EN2T | EtherNet/IP Bridge |
| 1756-ENBT | EtherNet/IP Bridge (older) |
| 1756-DNB | DeviceNet Bridge |

## Programs and Routines
```xml
<Program Name="MainProgram" MainRoutineName="Main" FaultRoutineName="">
  <Tags><!-- program-scope tags --></Tags>
  <Routines>
    <Routine Name="Main" Type="RLL">
      <RLLContent>
        <Rung Number="0" Type="N">
          <Comment><![CDATA[Rung comment here]]></Comment>
          <Text><![CDATA[XIC(Tag1)OTE(Tag2);]]></Text>
        </Rung>
      </RLLContent>
    </Routine>
  </Routines>
</Program>
```

## Rung Instruction Syntax
Instructions are written inline: `INSTR(arg1,arg2,...)`

### Common Instructions
| Instruction | Type | Description |
|-------------|------|-------------|
| XIC(tag) | Input | Examine if Closed (NO contact) |
| XIO(tag) | Input | Examine if Open (NC contact) |
| OTE(tag) | Output | Output Energize (non-latching) |
| OTL(tag) | Output | Output Latch |
| OTU(tag) | Output | Output Unlatch |
| ONS(tag) | Input | One-Shot |
| TON(timer,?,?) | Timer | Timer On-Delay |
| TOF(timer,?,?) | Timer | Timer Off-Delay |
| RTO(timer,?,?) | Timer | Retentive Timer |
| CTU(counter,?,?) | Counter | Count Up |
| CTD(counter,?,?) | Counter | Count Down |
| RES(tag) | Reset | Reset timer/counter |
| MOV(src,dest) | Move | Move value |
| EQU(a,b) | Compare | Equal |
| NEQ(a,b) | Compare | Not Equal |
| GRT(a,b) | Compare | Greater Than |
| GEQ(a,b) | Compare | Greater Than or Equal |
| LES(a,b) | Compare | Less Than |
| LEQ(a,b) | Compare | Less Than or Equal |
| ADD(a,b,dest) | Math | Add |
| SUB(a,b,dest) | Math | Subtract |
| MUL(a,b,dest) | Math | Multiply |
| DIV(a,b,dest) | Math | Divide |
| JSR(routine,?) | Program | Jump to Subroutine |
| GRT(a,b) | Compare | Greater Than |
| AFI() | Debug | Always False Instruction |
| NOP() | Debug | No Operation |

### Branch Syntax
Parallel branches use `[` and `]` with `,` separating branches:
```
[XIC(Tag1),XIC(Tag2)]OTE(Tag3);
```
This means Tag1 OR Tag2 energizes Tag3.

Nested: `[XIC(A)XIC(B),XIC(C)]OTE(D);` = (A AND B) OR C → D

## Produced/Consumed Tags
```xml
<Tag Name="Shared_Data" TagType="Produced" DataType="DINT" ProduceCount="1" ExternalAccess="Read/Write">
</Tag>
<Tag Name="Remote_Data" TagType="Consumed" DataType="DINT" ExternalAccess="Read/Write">
  <ConsumeInfo Producer="Other_PLC" RemoteTag="Shared_Data" RPI="20000"/>
</Tag>
```

## AOI (Add-On Instructions)
```xml
<AddOnInstructionDefinition Name="MyAOI">
  <Parameters>
    <Parameter Name="EnableIn" Usage="Input" DataType="BOOL"/>
    <Parameter Name="EnableOut" Usage="Output" DataType="BOOL"/>
    <Parameter Name="InputVal" Usage="Input" DataType="DINT"/>
    <Parameter Name="Result" Usage="Output" DataType="BOOL"/>
  </Parameters>
  <LocalTags>
    <LocalTag Name="Internal" DataType="DINT"/>
  </LocalTags>
  <Routines>
    <Routine Name="Logic" Type="RLL">
      <RLLContent>
        <Rung Number="0" Type="N">
          <Text><![CDATA[GRT(InputVal,100)OTE(Result);]]></Text>
        </Rung>
      </RLLContent>
    </Routine>
  </Routines>
</AddOnInstructionDefinition>
```
