from __future__ import print_function;
from util.binary_file import printHexDump;
from util.byte_util import bytesToHexString, byteToHexStringSpaceAlign;
import elf64.reader as elf64;
from architecture.architecture import getArchitecture;
from compiler.compiler import getCompiler;
import stats.calculate_stats as stats;
import gc;


def printInstructionsWithDebug(instructions, showInstructionDetails = False, startPrintingAt = -1):
	if (startPrintingAt < 0):
		return;

	print("Starting at:", startPrintingAt);
	print("Last instruction:", len(instructions));
	print("Total printing:", len(instructions) - startPrintingAt);

	if (startPrintingAt > 0):
		instructions = instructions[startPrintingAt:];

	if (len(instructions) == 0):
		print("No instructions");
		return;

	lastInstructionStartByte = instructions[-1][0];
	startByteLength = len(byteToHexStringSpaceAlign(lastInstructionStartByte));

	maxInstructionLength = 0;
	maxOpcodeLength = 0;
	for _, instructionBytes, instruction in instructions:
		instructionLength = len(instructionBytes);
		if (instructionLength > maxInstructionLength):
			maxInstructionLength = instructionLength;

		opcodeLength = len(instruction.getOpcode().name);
		if (opcodeLength > maxOpcodeLength):
			maxOpcodeLength = opcodeLength;

	maxMaxOpcodeLength = 6;
	if (maxOpcodeLength > maxMaxOpcodeLength):
		maxOpcodeLength = maxMaxOpcodeLength;

	instructionNumber = max(startPrintingAt, 0);
	for startByte, instructionBytes, instruction in instructions:
		s = "";
		s += "{:4}".format(instructionNumber);
		s += " | ";
		s += byteToHexStringSpaceAlign(startByte, length = startByteLength);
		s += ": ";

		bytesString = bytesToHexString(instructionBytes, bytesBetweenSpaces = 1);
		# 3 because 2 hex chars for 1 byte + 1 space char
		while (len(bytesString) < maxInstructionLength * 3):
			bytesString += " ";

		s += bytesString;
		s += " ";
		s += instruction.toString(maxOpcodeLength);
		print(s);

		if (showInstructionDetails):
			print(repr(instruction));
			if (startByte != lastInstructionStartByte):
				print("-" * 80);

		instructionNumber += 1;


def readElf64File(filename):
	elf64File, errorMessage = elf64.readElf64File(filename);

	if (elf64File == None):
		print("File not loaded: %s" % errorMessage);
		return None;

	return elf64File;


def getTextSection(elf64File):
	textSection = elf64File.getSectionContents(".text");

	if (textSection == None):
		print("Text section not found in file");
		return None;

	return textSection;


def decodeMachineCode(architecture, machineCode, firstByteOffset = 0, startPrintingFrom = -1, startDebugFrom = -1):
	# "withDebug" is because this is a tuple of (startByte, [bytesInInstruction], InstructionInstance)
	instructionsWithDebug = architecture.decode(machineCode, firstByteOffset = firstByteOffset, startDebugAt = startDebugFrom);
	instructions = map(lambda x: x[2], instructionsWithDebug);

	printInstructionsWithDebug(instructionsWithDebug, startPrintingAt = startPrintingFrom, showInstructionDetails = False);

	return instructions;


def calculateStats(architecture, compiler, filename, instructions, writeOutput = print):
	return stats.calculateStats(architecture, compiler, filename, instructions, writeOutput);


def doWorkOnObjectFile(architecture, compiler, filename, writeOutput = print, firstByteOffset = 0, startPrintingFrom = -1, startDebugFrom = -1):
	elf64File = readElf64File(filename);
	textSection = getTextSection(elf64File);

	elf64File.setSectionContents(".text", None);
	elf64File = None;
	gc.collect();

	instructions = decodeMachineCode(architecture, textSection, firstByteOffset, startPrintingFrom, startDebugFrom);
	# print("Total instruction count", len(instructions));
	textSection = None;
	gc.collect();
	
	stats = calculateStats(architecture, compiler, filename, instructions, writeOutput);
	gc.collect();

# 0x8b8b75
"""
500000 instructions
Before optimizations: 53.1s
After REX optimizations: 51.6s
After commenting out debug print calls: 24.6s
After opcode caching: 22.2s
"""

def accumulateLines(lines):
	def inner(line):
		lines.append(line);
	return inner;

def main():
	x86 = getArchitecture("x86");
	gcc = getCompiler("gcc");
	ghc = getCompiler("ghc");
	clang = getCompiler("clang");

	printingStart = -1; # 1275290; # 1340; # 9900; # -1; # 1275199;
	debugStart = -1;
	firstByteOffset = 0x400440; # 0; # 0x4028b0;

	lines = [ ];
	writeOutput = accumulateLines(lines);

	# doWorkOnObjectFile(x86, gcc, "object_files/hello_world_gcc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	# doWorkOnObjectFile(x86, gcc, "object_files/add_function_gcc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	# doWorkOnObjectFile(x86, gcc, "object_files/array_loop_gcc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);
	
	doWorkOnObjectFile(x86, gcc, "object_files/add_function_linked_gcc.out", writeOutput = print, firstByteOffset = 0x400490, startPrintingFrom = printingStart, startDebugFrom = debugStart);
	# doWorkOnObjectFile(x86, clang, "object_files/add_function_linked_clang.out", firstByteOffset = 0x400440, startPrintingFrom = printingStart, startDebugFrom = debugStart);

	# doWorkOnObjectFile(x86, gcc, "object_files/gcc_gcc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);

	# doWorkOnObjectFile(x86, gcc, "object_files/gcc_linked_gcc.out", firstByteOffset = 0x4028b0, startPrintingFrom = printingStart, startDebugFrom = debugStart);
	# doWorkOnObjectFile(x86, clang, "object_files/gcc_linked_clang.out", firstByteOffset = 0x402800, startPrintingFrom = printingStart, startDebugFrom = debugStart,);



	if (len(lines) > 0):
		print("");
		print("Showing lines:");
		print("-" * 80);
		for line in lines:
			print("\"" + str(line) + "\"");
		print("-" * 80);


	# doWorkOnObjectFile(ghc, x86, "object_files/add_function_ghc.o", startPrintingFrom = printingStart, startDebugFrom = debugStart);


main();
# printHexDump("hello_world.o");
# printHexDump("add_function.o");
# printHexDump("array_loop.o");
