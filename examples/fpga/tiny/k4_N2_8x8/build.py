from prga.compatible import *
from prga.core.common import *
from prga.passes.translation import *
from prga.passes.vpr import *
from prga.passes.rtl import *
from prga.passes.yosys import *
from prga.cfg.scanchain.lib import ScanchainSwitchDatabase, Scanchain
from prga.netlist.module.util import ModuleUtils
from prga.netlist.net.util import NetUtils

from itertools import product
from pympler.asizeof import asizeof as size

ctx = Scanchain.new_context(1)
gbl_clk = ctx.create_global("clk", is_clock = True)
gbl_clk.bind((0, 1), 0)
l1 = ctx.create_segment('L1', 12, 1)
l2 = ctx.create_segment('L4', 3, 4)

builder = ctx.create_cluster("cluster")
clk = builder.create_clock("clk")
i = builder.create_input("i", 4)
o = builder.create_output("o", 1)
lut = builder.instantiate(ctx.primitives["lut4"], "lut")
ff = builder.instantiate(ctx.primitives["flipflop"], "ff")
builder.connect(clk, ff.pins['clk'])
builder.connect(i, lut.pins['in'])
builder.connect(lut.pins['out'], o)
builder.connect(lut.pins['out'], ff.pins['D'], pack_patterns = ('lut_dff', ))
builder.connect(ff.pins['Q'], o)
cluster = builder.commit()

builder = ctx.create_io_block("iob", 2)
o = builder.create_input("outpad", 1)
i = builder.create_output("inpad", 1)
builder.connect(builder.instances['io'].pins['inpad'], i)
builder.connect(o, builder.instances['io'].pins['outpad'])
iob = builder.commit()

iotiles = {}
for ori in Orientation:
    if ori.is_auto:
        continue
    builder = ctx.create_array('iotile_{}'.format(ori.name), 1, 1,
            set_as_top = False, edge = OrientationTuple(False, **{ori.name: True}))
    builder.instantiate(iob, (0, 0))
    builder.fill( (0.5, 0.5) )
    iotiles[ori] = builder.commit()

builder = ctx.create_logic_block("clb")
clk = builder.create_global(gbl_clk, Orientation.south)
for i in range(2):
    inst = builder.instantiate(cluster, "cluster{}".format(i))
    builder.connect(clk, inst.pins['clk'])
    builder.connect(builder.create_input("i{}".format(i), 4, Orientation.west), inst.pins['i'])
    builder.connect(inst.pins['o'], builder.create_output("o{}".format(i), 1, Orientation.east))
clb = builder.commit()

builder = ctx.create_array('subarray', 4, 4, set_as_top = False)
for pos in product(range(4), range(4)):
    builder.instantiate(clb, pos)
builder.fill( (0.4, 0.25), sbox_pattern = SwitchBoxPattern.span_limited)
# builder.auto_connect()
subarray = builder.commit()

builder = ctx.create_array('top', 10, 10, hierarchical = True, set_as_top = True)
for x, y in product(range(10), range(10)):
    if (x in (0, 9) and 0 < y < 9) or (y in (0, 9) and 0 < x < 9):
        builder.instantiate(iotiles[Orientation.west if x == 0 else
            Orientation.east if x == 9 else Orientation.south if y == 0 else Orientation.north], (x, y))
    elif x < 9 and y < 9 and x % 4 == 1 and y % 4 == 1:
        builder.instantiate(subarray, (x, y))
# builder.fill( (0.15, 0.1), channel_on_edge = OrientationTuple(False) )
builder.auto_connect()
top = builder.commit()

TranslationPass().run(ctx)

Scanchain.complete_scanchain(ctx, ctx.database[ModuleView.logical, top.key])

VPRInputsGeneration('vpr').run(ctx)

r = Scanchain.new_renderer()

VerilogCollection(r, 'rtl').run(ctx)

YosysScriptsCollection(r, "syn").run(ctx)

r.render()

ctx.pickle("ctx.pickled")
