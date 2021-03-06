from __future__ import print_function;
from util.byte_util import getDisplayByteString;
import operand;
import register;


TRANSFER_TYPE = 0;
ARITHMETIC_TYPE = 1;
LOGIC_TYPE = 2;
MISC_TYPE = 3;
JUMP_TYPE = 4;
JUMP_UNSIGNED_TYPE = 5;
JUMP_SIGNED_TYPE = 6;


OPCODE_TYPES = [
	"transfer",
	"arithmetic",
	"logic",
	"misc",
	"jump",
	# "jump unsigned",
	# "jump signed"
];


def opcodeTypeToString(opcodeType):
	if ((opcodeType < 0) or (opcodeType >= len(OPCODE_TYPES))):
		return "None";
	else:
		return OPCODE_TYPES[opcodeType];


"""
Fields available:

Field name			Default value		Effect
- name				
- opcodeType
- dataSize			[ do nothing ]		Call rexPrefix.setDataSize()
- opcodeExtension		False
- readModRegRm			False
- rmIsSource			True
- readImmediateBytes		0
- autoInsertRegister		False			E.g. 3d cmp wants ax/eax/rax auto added
- autoOperands			[ ]			Opcode defines its own operands
- autoImmediateOperands		[ ]			Same as above but immediates
- immediateCanBe64WithRexW	False			If true and rexW is true, read a 64 bit immediate instead
"""


opcodeParameterDefaults = {
	"dataSize": 64,
	"opcodeExtension": False,
	"readModRegRm": False,
	"rmIsSource": True,
	"readImmediateBytes": 0,
	"autoInsertRegister": False,
	"autoOperands": [ ],
	"autoImmediateOperands": [ ],
	"immediateCanBe64WithRexW": False
};


def jumpDetails(name, immediateSize = 1):
	return {
		"name": name,
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": immediateSize
	};


def setByteOnConditionDetails(name):
	return {
		"name": name,
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"opcodeExtension": "True",
		"readModRegRm": True
	};


def conditionalMoveDetails(name):
	return {
		"name": name,
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	};



top5BitsOpcodes = {
	# push r16/32/64
	0x50: {
		"name": "push",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 64
	},

	# pop r16/32/64
	0x58: {
		"name": "pop",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 64

	},

	# mov imm8 -> r8
	0xb0: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1
	},

	# mov imm16/32/64 -> r16/32/64
	0xb8: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 32,
		"readImmediateBytes": 4,
		"immediateCanBe64WithRexW": True
	}
};


twoByteTop5BitsOpcodes = {
	# bswap r32
	0xc8: {
		"name": "bswap",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 32
	}
};


oneByteOpcodes = {
	# add r8 to rm8
	0x00: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# add r16/32/64 to rm16/32/64
	0x01: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# add rm8 to r8
	0x02: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# add rm16/32/64 to r16/32/64
	0x03: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# add al and imm8
	0x04: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"	
	},

	# add ax/eax/rax and imm32
	0x05: {
		"name": "add",
		"opcodeType": ARITHMETIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"	
	},

	# or rm8 or r8
	0x08:
	{
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# or rm16/32/64 or r16/32/64
	0x09:
	{
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True
	},

	# or rm8 or r8
	0x0a:
	{
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# or r16/32/64 or rm16/32/64
	0x0b:
	{
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# or al or imm8
	0x0c: {
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"	
	},

	# or ax/eax/rax or imm16/32
	0x0d: {
		"name": "or",
		"opcodeType": LOGIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"	
	},

	# sbb r8 from rm8
	0x18: {
		"name": "sbb",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# sbb r16/32/64 from rm16/32/64
	0x19: {
		"name": "sbb",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# and rm8 and r8
	0x20:
	{
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# and rm16/32/64 and r16/32/64
	0x21:
	{
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True
	},

	# and r8 and rm8
	0x22:
	{
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# and r16/32/64 and rm16/32/64
	0x23:
	{
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# and al and imm8
	0x24: {
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"	
	},

	# and ax/eax/rax and imm16/32
	0x25: {
		"name": "and",
		"opcodeType": LOGIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"	
	},

	# sub r8 from rm8
	0x28: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},


	# sub r16/32/64 from rm16/32/64
	0x29: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# sub rm16/32/64 from r16/32/64
	0x2b: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# sub imm8 from ax
	0x2c: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"
	},

	# sub imm16/32/64 from ax
	0x2d: {
		"name": "sub",
		"opcodeType": ARITHMETIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"
	},

	# xor rm8 xor r8
	0x30: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# xor rm16/32/64 xor r16/32/64
	0x31: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True
	},

	# xor r18 xor rm18
	0x32: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# xor r16/32/64 xor rm16/32/64
	0x33: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},
	
	# xor al xor imm8
	0x34: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"
	},

	# xor ax xor imm32
	0x35: {
		"name": "xor",
		"opcodeType": LOGIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"
	},

	# cmp r16/32/64 with rm16/32/64
	0x39: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# cmp rm8 with r8
	0x3a: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cmp rm16/32/64 with r16/32/64
	0x3b: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cmp imm8 with al
	0x3c: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"
	},

	# cmp imm16/32 with ax/eax/rax
	0x3d: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"
	},

	# cmp r8 with rm8
	0x38: {
		"name": "cmp",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
	},

	# movsxd r64 -> rm32 with rex.w
	0x63: {
		"name": "movsxd",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# imul r16/32/64 <- rm16/32/64 * imm8
	0x6b: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 1
	},

	# imul r16/32/64 <- rm16/32/64 * imm16/32
	0x69: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 4
	},

	# jb rel8
	0x72: jumpDetails("jb"),

	# je rel8
	0x73: jumpDetails("jae"),

	# je rel8
	0x74: jumpDetails("je"),

	# jne rel8
	0x75: jumpDetails("jne"),

	# jbe rel8
	0x76: jumpDetails("jbe"),

	# ja rel8
	0x77: jumpDetails("ja"),

	# js rel8
	0x78: jumpDetails("js"),

	# js rel8
	0x79: jumpDetails("jns"),

	# jp rel8
	0x7a: jumpDetails("jp"),

	# jnp rel8
	0x7b: jumpDetails("jnp"),

	# jl rel8
	0x7c: jumpDetails("jl"),

	# jge rel8 
	0x7d: jumpDetails("jge"),

	# jle rel8 
	0x7e: jumpDetails("jle"),

	# jg rel8 
	0x7f: jumpDetails("jg"),

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 -> rm8
	0x80: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm32 -> rm16/32/64
	0x81: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 4
	},

	# add/or/adc/sbb/and/sub/xor/cmp
	# imm8 -> rm16/32/64
	0x83: {
		"name": ["add", "or", "adc", "sbb", "and", "sub", "xor", "cmp"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# test r8 and rm8
	0x84: {
		"name": "test",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# test r16/32/64 and rm16/32/64
	0x85: {
		"name": "test",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True
	},

	# mov r8 -> rm/8
	0x88: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"readModRegRm": True
	},

	# mov rm16/32/64 -> r16/32/64
	0x89: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True
	},

	# mov r8 -> rm8
	0x8a: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# mov r16/32/64 -> rm16/32/64
	0x8b: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# lea r16/32/64 <- rm
	0x8d: {
		"name": "lea",
		"opcodeType": MISC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cdqe
	0x98: {
		"name": "cdqe",
		"opcodeType": TRANSFER_TYPE
	},

	# nop
	0x90: {
		"name": "nop",
		"opcodeType": MISC_TYPE
	},

	# cdq
	0x99: {
		"name": "cdq",
		"opcodeType": TRANSFER_TYPE
	},

	# movs m16/32/64 -> m16/32/64
	0xa5: {
		"name": "movs",
		"opcodeType": MISC_TYPE,
		"autoOperands": [
			operand.RegisterMemoryOperand(register.Registers[3][7], operand.ES_SEGMENT_OVERRIDE),
			operand.RegisterMemoryOperand(register.Registers[3][6], operand.DS_SEGMENT_OVERRIDE)
		]
	},

	# cmps
	0xa6: {
		"name": "cmps",
		"opcodeType": ARITHMETIC_TYPE,
		"autoOperands": [
			operand.RegisterMemoryOperand(register.Registers[3][6], operand.DS_SEGMENT_OVERRIDE),
			operand.RegisterMemoryOperand(register.Registers[3][7], operand.ES_SEGMENT_OVERRIDE)
		]
	},

	# test al with imm8
	0xa8: {
		"name": "test",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"readImmediateBytes": 1,
		"autoInsertRegister": "000"
	},

	# test ax with imm8
	0xa9: {
		"name": "test",
		"opcodeType": ARITHMETIC_TYPE,
		"readImmediateBytes": 4,
		"autoInsertRegister": "000"
	},

	# stos m8
	0xaa: {
		"name": "stos",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 8,
		"autoOperands": [
			operand.RegisterMemoryOperand(register.Registers[3][7], operand.ES_SEGMENT_OVERRIDE),
			operand.RegisterOperand(register.Registers[0][0])
		]
	},


	# stos m16/32/64
	0xab: {
		"name": "stos",
		"opcodeType": TRANSFER_TYPE,
		"autoOperands": [
			operand.RegisterMemoryOperand(register.Registers[3][7], operand.ES_SEGMENT_OVERRIDE),
			operand.RegisterOperand(register.Registers[2][0])
		]
	},


	# scas
	0xae: {
		"name": "scas",
		"opcodeType": MISC_TYPE,
		"autoOperands": [
			operand.RegisterOperand(register.Registers[0][0]),
			operand.RegisterMemoryOperand(register.Registers[3][7], operand.ES_SEGMENT_OVERRIDE)
		]
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate rm8 by imm8
	0xc0: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate rm16/32/64 by imm8
	0xc1: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# return near
	0xc3: {
		"name": "ret",
		"opcodeType": JUMP_TYPE
	},

	# mov /0 imm8 -> rm8
	0xc6: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# mov /0 imm16/32/64 -> rm16/32/64
	0xc7: {
		"name": "mov",
		"opcodeType": TRANSFER_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 4
	},

	# leave
	0xc9: {
		"name": "leave",
		"opcodeType": JUMP_TYPE
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate rm16 by 1
	0xd0: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"autoImmediateOperands": [1]
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate rm16 by 1
	0xd1: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 16,
		"opcodeExtension": True,
		"readModRegRm": True,
		"autoImmediateOperands": [1]
	},

	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate cl by rm16/32/64
	0xd2: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"autoInsertRegister": "001"
	},


	# rol/ror/rcl/rcr/shl/shr/sal/sar
	# shift/rotate cl by rm16/32/64
	0xd3: {
		"name": ["rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar"],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE, LOGIC_TYPE, LOGIC_TYPE, ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"autoInsertRegister": "001"
	},

	# call near rel16/32
	0xe8: {
		"name": "call",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 4
	},
	
	# jmp rel16/32
	0xe9: {
		"name": "jmp",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 4
	},

	# jmp rel8
	0xeb: {
		"name": "jmp",
		"opcodeType": JUMP_TYPE,
		"readImmediateBytes": 1
	},

	# hlt
	0xf4: {
		"name": "hlt",
		"opcodeType": MISC_TYPE
	},

	# test/test/not/neg/mul/imul/div/idiv
	# rm8
	0xf6: {
		"name": ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"],
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": [1, 1, 0, 0, 0, 0, 0, 0]
	},

	# test/test/not/neg/mul/imul/div/idiv
	# rm16/32/64
	0xf7: {
		"name": ["test", "test", "not", "neg", "mul", "imul", "div", "idiv"],
		"opcodeType": ARITHMETIC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": [4, 4, 0, 0, 0, 0, 0, 0]
	},

	# inc/dec/""/""/""/""/""/""
	0xfe: {
		"name": ["inc", "dec", "", "", "", "", "", ""],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE],
		"dataSize": 8,
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# inc/dec/call/callf/jmp/jmpf/push/""
	0xff: {
		"name": ["inc", "dec", "call", "callf", "jmp", "jmpf", "push", ""],
		"opcodeType": [ARITHMETIC_TYPE, ARITHMETIC_TYPE, JUMP_TYPE, JUMP_TYPE, JUMP_TYPE, JUMP_TYPE, JUMP_TYPE],
		"opcodeExtension": True,
		"readModRegRm": True
	}
};


twoByteOpcodes = {
	# movsd m64 -> xmm1
	0x10: {
		"name": "movsd",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movsd xmm2 -> xmm1/m64
	0x11: {
		"name": "movsd",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True
	},

	# movhlps xmm2 -> xmm1
	0x12: {
		"name": "movhlps",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True
	},

	# unpcklps xmm2/m128 -> xmm1
	0x14: {
		"name": "unpcklps",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True
	},

	# movhps xmm1 -> m64
	0x16: {
		"name": "movhps",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# prefetch, hint_nop
	0x18: {
		"name": ["prefetchnta", "prefetcht0", "prefetcht1", "prefetcht2", "hint_nop", "hint_nop", "hint_nop", "hint_nop"],
		"opcodeType": [TRANSFER_TYPE, TRANSFER_TYPE, TRANSFER_TYPE, TRANSFER_TYPE, MISC_TYPE, MISC_TYPE, MISC_TYPE, MISC_TYPE],
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# nop
	0x1f: {
		"name": "nop",
		"opcodeType": MISC_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True
	},

	# movapd xmm2/m128 -> xmm1
	0x28: {
		"name": "movapd",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movaps xmm1 -> xmm2/m128
	0x29: {
		"name": "movaps",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True
	},

	# cvtsi2sd (r32/m32)/rm64 -> xmm1
	0x2a: {
		"name": "cvtsi2d",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cvttsd2si xmm1/m64 -> r32/64
	0x2c: {
		"name": "cvttsd2si",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# ucomisd xmm1, xmm2/m64
	0x2e: {
		"name": "ucomisd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cmovb rm16/32/64 -> r16/32/64
	0x42: conditionalMoveDetails("cmovb"),

	# cmovae rm16/32/64 -> r16/32/64
	0x43: conditionalMoveDetails("cmovae"),

	# cmove rm16/32/64 -> r16/32/64
	0x44: conditionalMoveDetails("cmove"),

	# cmovne rm16/32/64 -> r16/32/64
	0x45: conditionalMoveDetails("cmovne"),

	# cmovbe rm16/32/64 -> r16/32/64
	0x46: conditionalMoveDetails("cmovbe"),
	
	# cmova rm16/32/64 -> r16/32/64
	0x47: conditionalMoveDetails("cmova"),

	# cmovs rm16/32/64 -> r16/32/64
	0x48: conditionalMoveDetails("cmovs"),

	# cmovns rm16/32/64 -> r16/32/64
	0x49: conditionalMoveDetails("cmovns"),

	# cmovl rm16/32/64 -> r16/32/64
	0x4c: conditionalMoveDetails("cmovl"),

	# cmovge rm16/32/64 -> r16/32/64
	0x4d: conditionalMoveDetails("cmovge"),

	# cmole rm16/32/64 -> r16/32/64
	0x4e: conditionalMoveDetails("cmovle"),

	# cmovg rm16/32/64 -> r16/32/64
	0x4f: conditionalMoveDetails("cmovg"),

	# andpd xmm2/m128 to xmm1
	0x54: {
		"name": "andpd",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# andnpd xmm2/m128 to xmm1
	0x55: {
		"name": "andnpd",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# orpd xmm2/m128 to xmm1
	0x56: {
		"name": "orpd",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# xorpd xmm1, xm22/m128
	0x57: {
		"name": "xorpd",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# addps xmm2/m128 to xmm1
	0x58: {
		"name": "addps",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# mulsd xmm2/m64 to xmm1
	0x59: {
		"name": "mulsd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# cvtps2pd xmm2/m64 -> xmm1
	0x5a: {
		"name": "cvtps2pd",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# subsd xmm2/m64 to xmm1
	0x5c: {
		"name": "subsd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# minsd xmm2/m64 to xmm1
	0x5d: {
		"name": "minsd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# divsd xmm2/m64 to xmm1
	0x5e: {
		"name": "divsd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# maxsd xmm2/m64 to xmm1
	0x5f: {
		"name": "maxsd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# punpckldq mm/m32 -> mm
	0x62: {
		"name": "punpckldq",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# pcmpgtd mm/m64 -> mm
	0x66: {
		"name": "pcmpgtd",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},


	# punpcklqdq mm/m32 -> mm
	0x6c: {
		"name": "punpcklqdq",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# punpckhqdq xmm2/m128 -> xmm1
	0x6d: {
		"name": "punpckhqdq",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},


	# movq mm -> rm32/64
	0x6e: {
		"name": "movq",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movdqu mm64 -> mm
	0x6f: {
		"name": "movdqu",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# pshufd xmm2/m128 + imm8 -> xmm1
	0x70: {
		"name": "pshufd",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 1	
	},

	# psrlq/psrldq/psllq/pslldq logical shift xmm imm8
	0x73: {
		"name": ["", "", "psrlq", "psrldq", "", "", "psllq", "pslldq"],
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# pcmpeqb mm/m64 -> mm
	0x74: {
		"name": "pcmpeqb",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# pcmpeqd mm/m64 -> mm
	0x76: {
		"name": "pcmpeqd",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movq rm32/64 -> mm
	0x7e: {
		"name": "movq",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		# "rmIsSource": False
	},

	# movdqa mm64 -> mm
	0x7f: {
		"name": "movdqa",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
	},

	# jb rel32
	0x82: jumpDetails("jb", 4),

	# jae rel32
	0x83: jumpDetails("jae", 4),

	# je rel32
	0x84: jumpDetails("je", 4),

	# jne rel32
	0x85: jumpDetails("jne", 4),
	
	# jbe rel32
	0x86: jumpDetails("jbe", 4),

	# ja rel32
	0x87: jumpDetails("ja", 4),

	# ja rel32
	0x88: jumpDetails("js", 4),

	# jp rel32
	0x8a: jumpDetails("jp", 4),

	# jnp rel32
	0x8b: jumpDetails("jnp", 4),

	# jl rel32
	0x8c: jumpDetails("jl", 4),

	# jge rel32
	0x8d: jumpDetails("jge", 4),

	# jle rel32
	0x8e: jumpDetails("jle", 4),

	# jns rel32
	0x89: jumpDetails("jns", 4),

	# jle rel32
	0x8f: jumpDetails("jg", 4),

	# setb /0 rm8
	0x92: setByteOnConditionDetails("setb"),

	# setae /0 rm8
	0x93: setByteOnConditionDetails("setae"),

	# sete /0 rm8
	0x94: setByteOnConditionDetails("sete"),

	# setne /0 rm8
	0x95: setByteOnConditionDetails("setne"),

	# setbe /0 rm8
	0x96: setByteOnConditionDetails("setbe"),

	# seta /0 rm8
	0x97: setByteOnConditionDetails("seta"),

	# sets /0 rm8
	0x98: setByteOnConditionDetails("sets"),

	# setns /0 rm8
	0x99: setByteOnConditionDetails("setns"),
	
	# setl /0 rm8
	0x9c: setByteOnConditionDetails("setl"),

	# setge /0 rm8
	0x9d: setByteOnConditionDetails("setge"),

	# setle /0 rm8
	0x9e: setByteOnConditionDetails("setle"),

	# setg /0 rm8
	0x9f: setByteOnConditionDetails("setg"),

	# bt rm16/32/64 r16/32/64
	0xa3: {
		"name": "bt",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True
	},

	# shld r/m16 r16 imm8
	0xa4: {
		"name": "shld",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# shld r/m16 r16 cl
	0xa5: {
		"name": "shld",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"autoInsertRegister": "001",
	},

	# shrd r/m16 r16 imm8
	0xac: {
		"name": "shrd",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# shrd r/m16 r16 cl
	0xad: {
		"name": "shrd",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"autoInsertRegister": "001",
	},

	# imul r16/32/64 <- r16/32/64 * rm16/32/64
	0xaf: {
		"name": "imul",
		"opcodeType": ARITHMETIC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# bt/bts/br/btc rm16/32 imm8
	0xba: {
		"name": ["", "", "", "", "bt", "bts", "btr", "btc"],
		"opcodeType": TRANSFER_TYPE,
		"opcodeExtension": True,
		"readModRegRm": True,
		"readImmediateBytes": 1
	},

	# movzx rm8 -> r16/32/64
	0xb6: {
		"name": "movzx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movzx rm16 -> r32/64
	0xb7: {
		"name": "movzx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# bsr rm16/32/63 -> r16/32/64
	0xbd: {
		"name": "bsr",
		"opcodeType": MISC_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movsx rm8 -> r16/32/64
	0xbe: {
		"name": "movsx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movsx rm16 -> r32/64
	0xbf: {
		"name": "movsx",
		"opcodeType": TRANSFER_TYPE,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# pinsrw r32/m16 + imm8 -> mm
	0xc4: {
		"name": "pinsrw",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 1	
	},


	# pextrw mm + imm8 -> reg
	0xc5: {
		"name": "pextrw",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 1	
	},


	# shufps xmm2/m128 + imm8 -> xmm1
	0xc6: {
		"name": "shufps",
		"opcodeType": TRANSFER_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False,
		"readImmediateBytes": 1	
	},

	# pand mm/m64 bitwise and mm
	0xdb: {
		"name": "pand",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# paddq xmm2/m128 to xmm1
	0xd4: {
		"name": "paddq",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# movq xmm1 -> xmm2/m128
	0xd6: {
		"name": "movq",
		"opcodeType": ARITHMETIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True
	},

	# pandn mm/m64 bitwise and not mm
	0xdf: {
		"name": "pandn",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# por mm/m64 bitwise or mm
	0xeb: {
		"name": "por",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# pxor mm/m64 bitwise xor mm
	0xef: {
		"name": "pxor",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# pmuludq xmm2/m64 to xmm1
	0xf4: {
		"name": "pmuludq",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# psubq xmm2/m128 to xmm1
	0xfb: {
		"name": "psubq",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	},

	# paddd xmm2/m128 to xmm1
	0xfe: {
		"name": "paddd",
		"opcodeType": LOGIC_TYPE,
		"dataSize": 128,
		"readModRegRm": True,
		"rmIsSource": False
	}
};

# Total unique opcodes 194
# Total actual opcodes by type
# 	0 transfer   68
# 	1 arithmetic 46
# 	2 logic      31
# 	3 misc       7
# 	4 jump       33

# Total unique opcodes 250
# Total actual opcodes by type
# 	0 transfer   72
# 	1 arithmetic 86
# 	2 logic      43
# 	3 misc       11
# 	4 jump       38

def countOpcodeTypes():
	opcodeCount = 0;
	opcodeTypes = [0] * len(OPCODE_TYPES);

	for opcodesDict in [top5BitsOpcodes, twoByteTop5BitsOpcodes, oneByteOpcodes, twoByteOpcodes]:
		for opcode in opcodesDict.values():
			opcodeName = opcode["name"];
			opcodeType = opcode["opcodeType"];

			if (type(opcodeName) == str):
				opcodeCount += 1;
				opcodeTypes[opcodeType] += 1;
			else:
				# If there are 3 names but all same type
				# Turn it from type = t
				# Into type = [t, t, t]
				if (type(opcodeType) == int):
					opcodeType = [opcodeType] * len(opcodeName);

				for (n, t) in zip(opcodeName, opcodeType):
					if (n != ""):
						opcodeTypes[t] += 1;

			# if (type(opcodeType) == int):
			# 	opcodeCount += 1;
			# 	opcodeTypes[opcodeType] += 1;
			# else:
			# 	for t in opcodeType:
			# 		opcodeCount += 1;
			# 		opcodeTypes[t] += 1;

	return opcodeCount, opcodeTypes;

# UNIQUE_OPCODE_TYPE_COUNT = [100] * len(OPCODE_TYPES);
# UNIQUE_OPCODE_COUNT = sum(UNIQUE_OPCODE_TYPE_COUNT);

UNIQUE_OPCODE_COUNT, UNIQUE_OPCODE_TYPE_COUNT = countOpcodeTypes();


def getOpcodeParamOrDefault(opcodeDetails, parameter):
	if (parameter in opcodeDetails):
		return opcodeDetails[parameter];
	else:
		if (parameter in opcodeParameterDefaults):
			return opcodeParameterDefaults[parameter];
		else:
			print("Unknown opcode parameter:", str(parameter));
			return None;


class Opcode(object):
	def __init__(self, opcode, extension, name, opcodeType):
		if (str(type(opcodeType)) != "<type 'int'>"):
			print(opcodeType);
		self._opcode = opcode;
		self._extension = extension;
		self._name = name;
		self._opcodeType = opcodeType;


	@property
	def opcode(self):
		return self._opcode;


	@property
	def extension(self):
		return self._extension;


	@property
	def name(self):
		return self._name;


	@property
	def opcodeType(self):
		return self._opcodeType;


	def __repr__(self):
		h = hex(self._opcode);
		hNoPrefix = h[2:];
		if (len(hNoPrefix) % 2 == 1):
			h = "0x0" + hNoPrefix;

		s = "Opcode(opcode = " + h;
		if (self._extension != -1):
			s += ", extension = " + hex(self._extension);
		s += ", name = " + self._name;
		s += ", type = " + opcodeTypeToString(self._opcodeType);
		s += ")";
		return s;

	def __hash__(self):
		return hash((self._opcode, self._extension, self._name));

	def __eq__(self, other):
		if (other == None):
			return False;
		return ((self._opcode, self._extension, self._name) == (other._opcode, other._extension, self._name));


	   #  def __hash__(self):
    #     return hash((self.name, self.location))

    # def __eq__(self, other):
    #     return (self.name, self.location) == (other.name, other.location)


OpcodesCache = { };

def getOpcode(opcodeByte, extension, name, opcodeType):
	# Haven't found opcode yet
	opcode = None;

	# Byte already in cache
	if (opcodeByte in OpcodesCache):
		# Get opcode out
		opcode = OpcodesCache[opcodeByte];

		# Opcode has extension (so the value in cache is a list)
		if (extension != -1):
			# Get the real opcode or None if this specific one not yet created
			opcode = opcode[extension];

	# Handle case for opcode name being slightly different
	# E.g. Has a rep prefix
	# Just return a new opcode, don't cache
	if (opcode != None):
		if (opcode.name != name):
			return Opcode(opcodeByte, extension, name, opcodeType);

	# Haven't seen opcode yet
	# i.e. not in cache, or a not-seen extension of opcode that has been seen
	if (opcode == None):
		# Create opcode
		opcode = Opcode(opcodeByte, extension, name, opcodeType);

		# Put in cache
		if (extension == -1):
			OpcodesCache[opcodeByte] = opcode;
		else:
			OpcodesCache[opcodeByte] = [None] * 8;
			OpcodesCache[opcodeByte][extension] = opcode;

	return opcode;



