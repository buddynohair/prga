# ============================================================================
# -- Set-up ------------------------------------------------------------------
# ============================================================================
FPGA_DIR := $(shell pwd)/../../../fpga/system/pktchain_axilite_32x32N8K6
TOPLEVEL_LANG := verilog
MODULE := test
TESTSUITE ?= system
SIM ?= vcs

BUDDY_DIR := $(shell pwd)/../system_pktchain_axilite_32x32N8K6
BITSTREAM := sha256_axilite_slave.memh

$(BITSTREAM):
	$(MAKE) -C $(BUDDY_DIR) bitgen
	cp $(BUDDY_DIR)/$(BITSTREAM) $@

CUSTOM_SIM_DEPS := $(BITSTREAM)

# -- Select Test-Suite -------------------------------------------------------
ifeq ($(TESTSUITE),system)

TOPLEVEL = prga_system
VERILOG_SOURCES = $(FPGA_DIR)/rtl/*.v
TESTCASE = full_system

else ifeq ($(TESTSUITE),app)

TOPLEVEL = app
VERILOG_SOURCES = $(shell pwd)/src/app.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/pktchain_axilite_intf.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/pktchain_axilite_intf_be_cfg.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/pktchain_axilite_intf_be_uprot.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/pktchain_axilite_intf_fe.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/pktchain_frame_assemble.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/pktchain_frame_disassemble.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_clkdiv.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_async_fifo.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_async_tokenfifo.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_byteaddressable_reg.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_tokenfifo.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_fifo.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_fifo_lookahead_buffer.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_fifo_resizer.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_fifo_adapter.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_ram_1r1w.v
VERILOG_SOURCES += $(FPGA_DIR)/rtl/prga_ram_1r1w_dc.v
VERILOG_SOURCES += $(shell pwd)/../testbench/sha256_axilite_slave.v
VERILOG_SOURCES += $(shell pwd)/../sha256/src/rtl/sha256_core.v
VERILOG_SOURCES += $(shell pwd)/../sha256/src/rtl/sha256_k_constants.v
VERILOG_SOURCES += $(shell pwd)/../sha256/src/rtl/sha256_w_mem.v
TESTCASE = uprot

else

$(error "Unknown testsuite: $(TESTSUITE)")

endif

# -- Select Simulator --------------------------------------------------------
ifeq ($(SIM),vcs)

COMPILE_ARGS = +incdir+$(FPGA_DIR)/rtl/include +lint=all +warn=all
EXTRA_ARGS = +vcs+loopdetect +vcs+loopreport

else

COMPILE_ARGS = -I$(FPGA_DIR)/rtl/include

endif

# ============================================================================
# -- Cocotb ------------------------------------------------------------------
# ============================================================================
COCOTB_SHARE_DIR := $(shell cocotb-config --share)
COCOTB_PY_DIR := $(shell cocotb-config --prefix)

export COCOTB_SHARE_DIR
export COCOTB_PY_DIR

include $(shell cocotb-config --makefiles)/Makefile.inc
include $(shell cocotb-config --makefiles)/Makefile.sim

.DEFAULT_GOAL := sim
