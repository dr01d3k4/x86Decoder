import abc;

IMMEDIATE_TYPE = 0;
REGISTER_TYPE = 1;
REGISTER_MEMORY_TYPE = 2;
IMMEDIATE_MEMORY_TYPE = 3;
REGISTER_DISPLACEMENT_TYPE = 4;
REGISTER_SCALE_TYPE = 5;
SIB_TYPE = 6;
REGISTER_SCALE_DISPLACEMENT_TYPE = 7;
SIB_DISPLACEMENT_TYPE = 8;

OPERAND_TYPES = [
	"immediate",
	"register",
	"[register]",
	"[immediate]",
	"[register + immediate]",
	"[register * scale]",
	"[register + register * scale]",
	"[register * scale + immediate]",
	"[register + register * scale + immediate]",
];


def getSibOperandType(hasBase, hasIndex, hasDisplacement):
	sibType = -1;

	if (not hasDisplacement):
		if (hasBase):
			if (hasIndex):
				sibType = SIB_TYPE; """ [b + i*s] """
			else:
				sibType = REGISTER_MEMORY_TYPE; """ [b] """
		else:
			if (hasIndex):
				sibType = REGISTER_SCALE_TYPE; """ [i*s] """
			else:
				print("Unknown SIB type with no base, no index and no displacement");

	else:
		if (hasBase):
			if (hasIndex):
				sibType = SIB_DISPLACEMENT_TYPE; """ [b + i*s + d] """
			else:
				sibType = REGISTER_DISPLACEMENT_TYPE; """ [b + d] """
		else:
			if (hasIndex):
				sibType = REGISTER_SCALE_DISPLACEMENT_TYPE; """ [i*s + d] """
			else:
				sibType = IMMEDIATE_MEMORY_TYPE; """ [d] """

	return sibType;


def immediateValueToString(value):
	return hex(value);


def registerValueToString(register):
	return str(register);


def memoryLocationToString(location):
	return "[" + location + "]";


def immediateAdditionString(immediate):
	sign = "+" if immediate >= 0 else "-";
	return sign + " " + immediateValueToString(abs(immediate));


def scaleIndexBaseToStringNoMemory(scale, index, base):
	sib = "";

	if (base != None):
		sib += registerValueToString(base);
		
	if ((base != None) and (index != None)):
		sib += " + ";

	if (index != None):
		sib += registerValueToString(index);

	if (scale != 1):
		sib += " * " + str(scale);

	return sib;



def scaleIndexBaseToString(scale, index, base):
	return memoryLocationToString(scaleIndexBaseToStringNoMemory(scale, index, base));


def scaleIndexBaseImmediateToString(scale, index, base, immediate):
	sib = scaleIndexBaseToStringNoMemory(scale, index, base);
	sib += " ";
	sib += immediateAdditionString(immediate);
	return memoryLocationToString(sib);


class Operand(object):
	__metaclass__ = abc.ABCMeta;

	def __init__(self):
		pass;

	@abc.abstractmethod
	def getOperandType():
		pass;

	def __repr__(self):
		return "Operand()";

	def __str__(self):
		return "";


class RegisterOperand(Operand):
	def __init__(self, register):
		super(Operand, self).__init__();

		self._register = register;

	def getOperandType(self):
		return REGISTER_TYPE;

	def __repr__(self):
		return "RegisterOperand(register = " + repr(self._register) + ")";

	def __str__(self):
		return registerValueToString(self._register);


class ImmediateOperand(Operand):
	def __init__(self, value):
		super(Operand, self).__init__();

		self._value = value;

	def getOperandType(self):
		return IMMEDIATE_TYPE;

	def __repr__(self):
		return "ImmediateOperand(value = " + hex(self._value) + ")";

	def __str__(self):
		return immediateValueToString(self._value);


class RegisterMemoryOperand(Operand):
	def __init__(self, register):
		super(Operand, self).__init__();

		self._register = register;

	def getOperandType(self):
		return REGISTER_MEMORY_TYPE;

	def __repr__(self):
		return "RegisterMemoryOperand(register = " + repr(self._register) + ")";

	def __str__(self):
		return memoryLocationToString(registerValueToString(self._register));


class RegisterDisplacementOperand(Operand):
	def __init__(self, register, displacement):
		super(Operand, self).__init__();

		self._register = register;
		self._displacement = displacement;

	def getOperandType(self):
		return REGISTER_DISPLACEMENT_TYPE;

	def __repr__(self):
		return "RegisterDisplacementOperand(register = " + repr(self._register) + ", displacement = " + hex(self._displacement) + ")";

	def __str__(self):
		if (self._displacement == 0):
			return memoryLocationToString(registerValueToString(self._register));
		else:
			return memoryLocationToString(registerValueToString(self._register) + " " + immediateAdditionString(self._displacement));


class ScaleIndexBaseOperand(Operand):
	def __init__(self, scale, index, base):
		super(Operand, self).__init__();

		self._scale = scale;
		self._index = index;
		self._base = base;

	def getOperandType(self):
		return getSibOperandType(self._base != None, self._index != None, False);

	def __repr__(self):
		return "ScaleIndexBaseOperand(" \
				"scale = " + str(self._scale) + ", " + \
				"index = " + repr(self._index) + ", " + \
				"base = " + repr(self._base) + ")";

	def __str__(self):
		return scaleIndexBaseToString(self._scale, self._index, self._base);


class ScaleIndexBaseDisplacementOperand(Operand):
	def __init__(self, scale, index, base, displacement):
		super(Operand, self).__init__();

		self._scale = scale;
		self._index = index;
		self._base = base;
		self._displacement = displacement;

	def getOperandType(self):
		return getSibOperandType(self._base != None, self._index != None, True);

	def __repr__(self):
		return "ScaleIndexBaseDisplacementOperand(" \
				"scale = " + str(self._scale) + ", " + \
				"index = " + repr(self._index) + ", " + \
				"base = " + repr(self._base) + ", " + \
				"displacement = " + hex(self._displacement) + ")";

	def __str__(self):
		return scaleIndexBaseImmediateToString(self._scale, self._index, self._base, self._displacement);


class ImmediateDisplacementOperand(Operand):
	def __init__(self, value):
		super(Operand, self).__init__();

		self._value = value;

	def getOperandType(self):
		return IMMEDIATE_MEMORY_TYPE;

	def __repr__(self):
		return "ImmediateDisplacementOperand(value = " + hex(self._value) + ")";

	def __str__(self):
		return memoryLocationToString(immediateValueToString(self._value));
