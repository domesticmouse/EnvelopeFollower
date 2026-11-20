from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

skidl_REPL = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_SMD:R_0603_1608Metric', 'keywords':'R res resistor', 'description':'Resistor', 'datasheet':'', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TestPoint', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TestPoint'}), 'ref_prefix':'TP', 'fplist':[''], 'footprint':'TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm', 'keywords':'test point tp', 'description':'test point', 'datasheet':'', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fiducial', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fiducial'}), 'ref_prefix':'FID', 'fplist':[''], 'footprint':'Fiducial:Fiducial_1mm_Mask2mm', 'keywords':'fiducial marker', 'description':'Fiducial Marker', 'datasheet':'' })])