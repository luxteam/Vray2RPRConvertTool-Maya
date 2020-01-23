
'''

	Vray to RadeonProRender Converter

	History:
	v.1.0 - First version


'''

import maya.mel as mel
import maya.cmds as cmds
import os
import time
import math
import traceback

MAX_RAY_DEPTH = None

# log functions

def write_converted_property_log(rpr_name, rs_name, rpr_attr, rs_attr):

	try:
		file_path = cmds.file(q=True, sceneName=True) + ".log"
		with open(file_path, 'a') as f:
			f.write(u"    property {}.{} is converted to {}.{}   \r\n".format(rs_name, rs_attr, rpr_name, rpr_attr).encode('utf-8'))
	except Exception as ex:
		pass


def write_own_property_log(text):

	try:
		file_path = cmds.file(q=True, sceneName=True) + ".log"
		with open(file_path, 'a') as f:
			f.write("    {}   \r\n".format(text))
	except Exception as ex:
		pass


def start_log(rs, rpr):

	try:
		text  = u"Found node: \r\n    name: {} \r\n".format(rs).encode('utf-8')
		text += "type: {} \r\n".format(cmds.objectType(rs))
		text += u"Converting to: \r\n    name: {} \r\n".format(rpr).encode('utf-8')
		text += "type: {} \r\n".format(cmds.objectType(rpr))
		text += "Conversion details: \r\n"

		file_path = cmds.file(q=True, sceneName=True) + ".log"
		with open(file_path, 'a') as f:
			f.write(text)
	except Exception as ex:
		pass
	


def end_log(rs):

	try:
		text  = u"Conversion of {} is finished.\n\n \r\n".format(rs).encode('utf-8')

		file_path = cmds.file(q=True, sceneName=True) + ".log"
		with open(file_path, 'a') as f:
			f.write(text)
	except Exception as ex:
		pass
		

# additional fucntions

def copyProperty(rpr_name, conv_name, rpr_attr, conv_attr):

	# full name of attribute
	conv_field = conv_name + "." + conv_attr
	rpr_field = rpr_name + "." + rpr_attr
	vr_type = type(getProperty(conv_name, conv_attr))
	rpr_type = type(getProperty(rpr_name, rpr_attr))

	try:
		listConnections = cmds.listConnections(conv_field)
		# connection convert
		if listConnections and cmds.objectType(listConnections[0]) != "transform":
			obj, channel = cmds.connectionInfo(conv_field, sourceFromDestination=True).split('.')
			source_name, source_attr = convertMaterial(obj, channel).split('.')
			connectProperty(source_name, source_attr, rpr_name, rpr_attr)
		# complex color conversion for each channel (RGB/XYZ/HSV)
		elif not listConnections and vr_type == tuple:

			# change attr for channel conversion in some cases
			if cmds.objectType(conv_name) == 'VRayMtl' and conv_attr == 'color':
				conv_attr = "diffuseColor"
			elif cmds.objectType(conv_name) == 'VRayCarPaintMtl' and conv_attr == 'color':
				conv_attr = "base_color"
			elif cmds.objectType(conv_name) in ('VRayLightRectShape', 'VRayLightSphereShape', 'VRayLightMesh') and conv_attr == 'lightColor':
				conv_attr = "color"
			conv_field = conv_name + "." + conv_attr

			# RGB 
			if cmds.objExists(conv_field + "R") and cmds.objExists(rpr_field + "R"):
				copyProperty(rpr_name, conv_name, rpr_attr + "R", conv_attr + "R")
				copyProperty(rpr_name, conv_name, rpr_attr + "G", conv_attr + "G")
				copyProperty(rpr_name, conv_name, rpr_attr + "B", conv_attr + "B")
			elif cmds.objExists(conv_field + "R") and cmds.objExists(rpr_field + "X"):
				copyProperty(rpr_name, conv_name, rpr_attr + "X", conv_attr + "R")
				copyProperty(rpr_name, conv_name, rpr_attr + "Y", conv_attr + "G")
				copyProperty(rpr_name, conv_name, rpr_attr + "Z", conv_attr + "B")
			elif cmds.objExists(conv_field + "R") and cmds.objExists(rpr_field + "H"):
				copyProperty(rpr_name, conv_name, rpr_attr + "H", conv_attr + "R")
				copyProperty(rpr_name, conv_name, rpr_attr + "S", conv_attr + "G")
				copyProperty(rpr_name, conv_name, rpr_attr + "V", conv_attr + "B")
			# XYZ 
			elif cmds.objExists(conv_field + "X") and cmds.objExists(rpr_field + "R"):
				copyProperty(rpr_name, conv_name, rpr_attr + "R", conv_attr + "X")
				copyProperty(rpr_name, conv_name, rpr_attr + "G", conv_attr + "Y")
				copyProperty(rpr_name, conv_name, rpr_attr + "B", conv_attr + "Z")
			elif cmds.objExists(conv_field + "X") and cmds.objExists(rpr_field + "X"):
				copyProperty(rpr_name, conv_name, rpr_attr + "X", conv_attr + "X")
				copyProperty(rpr_name, conv_name, rpr_attr + "Y", conv_attr + "Y")
				copyProperty(rpr_name, conv_name, rpr_attr + "Z", conv_attr + "Z")
			elif cmds.objExists(conv_field + "X") and cmds.objExists(rpr_field + "H"):
				copyProperty(rpr_name, conv_name, rpr_attr + "H", conv_attr + "X")
				copyProperty(rpr_name, conv_name, rpr_attr + "S", conv_attr + "Y")
				copyProperty(rpr_name, conv_name, rpr_attr + "V", conv_attr + "Z")
			# HSV 
			elif cmds.objExists(conv_field + "H") and cmds.objExists(rpr_field + "R"):
				copyProperty(rpr_name, conv_name, rpr_attr + "R", conv_attr + "H")
				copyProperty(rpr_name, conv_name, rpr_attr + "G", conv_attr + "S")
				copyProperty(rpr_name, conv_name, rpr_attr + "B", conv_attr + "V")
			elif cmds.objExists(conv_field + "H") and cmds.objExists(rpr_field + "X"):
				copyProperty(rpr_name, conv_name, rpr_attr + "X", conv_attr + "H")
				copyProperty(rpr_name, conv_name, rpr_attr + "Y", conv_attr + "S")
				copyProperty(rpr_name, conv_name, rpr_attr + "Z", conv_attr + "V")
			elif cmds.objExists(conv_field + "H") and cmds.objExists(rpr_field + "H"):
				copyProperty(rpr_name, conv_name, rpr_attr + "H", conv_attr + "H")
				copyProperty(rpr_name, conv_name, rpr_attr + "S", conv_attr + "S")
				copyProperty(rpr_name, conv_name, rpr_attr + "V", conv_attr + "V")
			else:
				print("Failed to find right variant for {}.{} conversion".format(conv_name, conv_attr))

		# field conversion
		else:
			if vr_type == rpr_type or vr_type == unicode:
				setProperty(rpr_name, rpr_attr, getProperty(conv_name, conv_attr))
			elif vr_type == tuple and rpr_type == float:
				if cmds.objExists(conv_field + "R"):
					conv_attr += "R"
				elif cmds.objExists(conv_field + "X"):
					conv_attr += "X"
				elif cmds.objExists(conv_field + "H"):
					conv_attr += "H"
				setProperty(rpr_name, rpr_attr, getProperty(conv_name, conv_attr))
			elif vr_type == float and rpr_type == tuple:
				if cmds.objExists(rpr_field + "R"):
					rpr_attr1 = rpr_attr + "R"
					rpr_attr2 = rpr_attr + "G"
					rpr_attr3 = rpr_attr + "B"
				elif cmds.objExists(rpr_field + "X"):
					rpr_attr1 = rpr_attr + "X"
					rpr_attr2 = rpr_attr + "Y"
					rpr_attr3 = rpr_attr + "Z"
				elif cmds.objExists(conv_field + "H"):
					rpr_attr1 = rpr_attr + "H"
					rpr_attr2 = rpr_attr + "S"
					rpr_attr3 = rpr_attr + "V"
				setProperty(rpr_name, rpr_attr1, getProperty(conv_name, conv_attr))
				setProperty(rpr_name, rpr_attr2, getProperty(conv_name, conv_attr))
				setProperty(rpr_name, rpr_attr3, getProperty(conv_name, conv_attr))

			write_converted_property_log(rpr_name, conv_name, rpr_attr, conv_attr)
	except Exception as ex:
		traceback.print_exc()
		print(u"Error while copying from {} to {}".format(conv_field, rpr_field).encode('utf-8'))


def setProperty(rpr_name, rpr_attr, value):

	# full name of attribute
	rpr_field = rpr_name + "." + rpr_attr

	try:
		if type(value) == tuple:
			cmds.setAttr(rpr_field, value[0], value[1], value[2])
		elif type(value) == str or type(value) == unicode:
			cmds.setAttr(rpr_field, value, type="string")
		else:
			cmds.setAttr(rpr_field, value)
		write_own_property_log(u"Set value {} to {}.".format(value, rpr_field).encode('utf-8'))
	except Exception as ex:
		traceback.print_exc()
		print(u"Set value {} to {} is failed. Check the values and their boundaries. ".format(value, rpr_field).encode('utf-8'))
		write_own_property_log(u"Set value {} to {} is failed. Check the values and their boundaries. ".format(value, rpr_field).encode('utf-8'))


def getProperty(material, attr):

	# full name of attribute
	field = material + "." + attr
	try:
		value = cmds.getAttr(field)
		if type(value) == list:
			value = value[0]
	except Exception as ex:
		traceback.print_exc()
		write_own_property_log(u"There is no {} field in this node. Check the field and try again. ".format(field).encode('utf-8'))
		return

	return value


def mapDoesNotExist(rs_name, rs_attr):

	# full name of attribute
	rs_field = rs_name + "." + rs_attr

	try:
		if cmds.listConnections(rs_field):
			return 0
		elif cmds.objExists(rs_field + "R"):
			if cmds.listConnections(rs_field + "R") or cmds.listConnections(rs_field + "G") or cmds.listConnections(rs_field + "B"):
				return 0
		elif cmds.objExists(rs_field + "X"):
			if cmds.listConnections(rs_field + "X") or cmds.listConnections(rs_field + "Y") or cmds.listConnections(rs_field + "Z"):
				return 0
		elif cmds.objExists(rs_field + "H"):
			if cmds.listConnections(rs_field + "H") or cmds.listConnections(rs_field + "S")	or cmds.listConnections(rs_field + "V"):
				return 0
	except Exception as ex:
		traceback.print_exc()
		write_own_property_log(u"There is no {} field in this node. Check the field and try again. ".format(rs_field).encode('utf-8'))
		return

	return 1


def connectProperty(source_name, source_attr, rpr_name, rpr_attr):

	# full name of attribute
	source = source_name + "." + source_attr
	rpr_field = rpr_name + "." + rpr_attr

	try:
		source_type = type(getProperty(source_name, source_attr))
		dest_type = type(getProperty(rpr_name, rpr_attr))

		if rpr_attr in ("surfaceShader", "volumeShader"):
			cmds.connectAttr(source, rpr_field, force=True)

		elif cmds.objExists(source_name + ".outAlpha") and cmds.objExists(source_name + ".outColor"):

			if cmds.objectType(source_name) == "file":
				setProperty(source_name, "ignoreColorSpaceFileRules", 1)

			if source_type == dest_type:
				cmds.connectAttr(source, rpr_field, force=True)
			elif source_type == tuple and dest_type == float:
				source = source_name + ".outAlpha"
				cmds.connectAttr(source, rpr_field, force=True)
			elif source_type == float and dest_type == tuple:
				source = source_name + ".outColor"
				cmds.connectAttr(source, rpr_field, force=True)

		else:
			if source_type == dest_type:
				cmds.connectAttr(source, rpr_field, force=True)
			elif source_type == tuple and dest_type == float:
				if cmds.objExists(source + "R"):
					source += "R"
				elif cmds.objExists(source + "X"):
					source += "X"
				elif cmds.objExists(source + "X"):
					source += "H"
				cmds.connectAttr(source, rpr_field, force=True)
			elif source_type == float and dest_type == tuple:
				if cmds.objExists(rpr_field + "R"):
					rpr_field1 = rpr_field + "R"
					rpr_field2 = rpr_field + "G"
					rpr_field3 = rpr_field + "B"
				elif cmds.objExists(rpr_field + "X"):
					rpr_field1 = rpr_field + "X"
					rpr_field2 = rpr_field + "Y"
					rpr_field3 = rpr_field + "Z"
				elif cmds.objExists(rpr_field + "H"):
					rpr_field1 = rpr_field + "H"
					rpr_field2 = rpr_field + "S"
					rpr_field3 = rpr_field + "V"
				cmds.connectAttr(source, rpr_field1, force=True)
				cmds.connectAttr(source, rpr_field2, force=True)
				cmds.connectAttr(source, rpr_field3, force=True)

		write_own_property_log(u"Created connection from {} to {}.".format(source, rpr_field).encode('utf-8'))
	except Exception as ex:
		traceback.print_exc()
		print(u"Connection {} to {} is failed.".format(source, rpr_field).encode('utf-8'))
		write_own_property_log(u"Connection {} to {} is failed.".format(source, rpr_field).encode('utf-8'))


def invertValue(rpr_name, conv_name, rpr_attr, conv_attr):
	connection = cmds.listConnections(conv_name + "." + conv_attr)
	if connection and cmds.objectType(connection[0]) == "reverse":
		if mapDoesNotExist(connection[0], "input"):
			setProperty(rpr_name, rpr_attr, getProperty(connection[0], "input"))
		else:
			if cmds.listConnections(connection[0] + ".input"):
				copyProperty(rpr_name, connection[0],  rpr_attr, "input")
			elif cmds.listConnections(connection[0] + ".inputX"):
				copyProperty(rpr_name, connection[0],  rpr_attr, "inputX")
			elif cmds.listConnections(connection[0] + ".inputY"):
				copyProperty(rpr_name, connection[0],  rpr_attr, "inputY")
			elif cmds.listConnections(connection[0] + ".inputZ"):
				copyProperty(rpr_name, connection[0],  rpr_attr, "inputZ")
	elif connection:
		reverse_arith = cmds.shadingNode("RPRArithmetic", asUtility=True)
		reverse_arith = cmds.rename(reverse_arith, "Reverse_arithmetic")
		setProperty(reverse_arith, "operation", 1)
		setProperty(reverse_arith, "inputA", (1, 1, 1))
		copyProperty(reverse_arith, conv_name, "inputB", conv_attr)
		connectProperty(reverse_arith, "out", rpr_name, rpr_attr)
	else:
		conv_value = getProperty(conv_name, conv_attr)
		if type(conv_value) == float:
			setProperty(rpr_name, rpr_attr, 1 - conv_value)
		elif type(conv_value) == tuple:
			setProperty(rpr_name, rpr_attr, (1 - conv_value[0], 1 - conv_value[1], 1 - conv_value[2]))

	

def convertbump2d(conv_name, source):

	if cmds.objExists(conv_name + "_rpr"):
		rpr = conv_name + "_rpr"
	else:
		bump_type = getProperty(conv_name, "bumpInterp")
		if not bump_type:
			rpr = cmds.shadingNode("RPRBump", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_rpr")
		else:
			rpr = cmds.shadingNode("RPRNormal", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_rpr")

		# Logging to file
		start_log(conv_name, rpr)

		# Fields conversion
		copyProperty(rpr, conv_name, "color", "bumpValue")
		copyProperty(rpr, conv_name, "strength", "bumpDepth")

		# Logging to file
		end_log(conv_name)

	conversion_map = {
		"outNormal": "out",
		"outNormalX": "outX",
		"outNormalY": "outY",
		"outNormalZ": "outZ"
	}

	rpr += "." + conversion_map[source]
	return rpr


def convertBlendColors(conv_name, source):

	if cmds.objExists(conv_name + "_rpr"):
		rpr = conv_name + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRBlendValue", asUtility=True)
		rpr = cmds.rename(rpr, conv_name + "_rpr")

		# Logging to file
		start_log(conv_name, rpr)

		# Fields conversion
		copyProperty(rpr, conv_name, "inputA", "color1")
		copyProperty(rpr, conv_name, "inputB", "color2")
		copyProperty(rpr, conv_name, "weight", "blender")

		# Logging to file
		end_log(conv_name)

	conversion_map = {
		"output": "out",
		"outputR": "outR",
		"outputG": "outG",
		"outputB": "outB"
	}

	rpr += "." + conversion_map[source]
	return rpr


def convertLuminance(conv_name, source):

	if cmds.objExists(conv_name + "_rpr"):
		rpr = conv_name + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
		rpr = cmds.rename(rpr, conv_name + "_rpr")

		# Logging to file
		start_log(conv_name, rpr)

		# Fields conversion
		copyProperty(rpr, conv_name, "inputA", "value")
		setProperty(rpr, "inputB", (0, 0, 0))
		setProperty(rpr, "operation", 19)

		# Logging to file
		end_log(conv_name)

	conversion_map = {
		"outValue": "outX"
	}

	rpr += "." + conversion_map[source]
	return rpr


def convertColorComposite(conv_name, source):

	operation = getProperty(conv_name, "operation")
	if operation == 2:
		if cmds.objExists(conv_name + "_rpr"):
			rpr = conv_name + "_rpr"
		else:
			rpr = cmds.shadingNode("RPRBlendValue", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_rpr")

			# Logging to file
			start_log(conv_name, rpr)

			# Fields conversion
			copyProperty(rpr, conv_name, "inputA", "alphaA")
			copyProperty(rpr, conv_name, "inputB", "alphaB")
			copyProperty(rpr, conv_name, "weight", "factor")
			

			# Logging to file
			end_log(conv_name)

		conversion_map = {
			"outAlpha": "outR"
		}

		rpr += "." + conversion_map[source]
		return rpr

	else:

		if cmds.objExists(conv_name + "_rpr"):
			rpr = conv_name + "_rpr"
		else:
			rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_rpr")

			# Logging to file
			start_log(conv_name, rpr)

			# Fields conversion
			if operation in (0, 4, 5):
				setProperty(rpr, "operation", 0)
				if source == "outAlpha":
					copyProperty(rpr, conv_name, "inputA", "alphaA")
					copyProperty(rpr, conv_name, "inputB", "alphaB")
				else:
					copyProperty(rpr, conv_name, "inputA", "colorA")
					copyProperty(rpr, conv_name, "inputB", "colorB")
			elif operation == 1:
				if source == "outAlpha":
					if mapDoesNotExist(conv_name, "alphaA") and mapDoesNotExist(conv_name, "alphaB"):
						alphaA = getProperty(conv_name, alphaA)
						alphaB = getProperty(conv_name, alphaB)
						if alphaA > alphaB:
							copyProperty(rpr, conv_name, "inputA", "alphaA")
							copyProperty(rpr, conv_name, "inputB", "alphaB")
						else:
							copyProperty(rpr, conv_name, "inputA", "alphaB")
							copyProperty(rpr, conv_name, "inputB", "alphaA")
					elif mapDoesNotExist(conv_name, "alphaA"):
						copyProperty(rpr, conv_name, "inputA", "alphaA")
						copyProperty(rpr, conv_name, "inputB", "alphaB")
					elif mapDoesNotExist(conv_name, "alphaB"):
						copyProperty(rpr, conv_name, "inputA", "alphaB")
						copyProperty(rpr, conv_name, "inputB", "alphaA")
					else:
						copyProperty(rpr, conv_name, "inputA", "alphaA")
						copyProperty(rpr, conv_name, "inputB", "alphaB")
				else:
					if mapDoesNotExist(conv_name, "colorA") and mapDoesNotExist(conv_name, "colorB"):
						colorA = getProperty(conv_name, alphaA)
						colorB = getProperty(conv_name, colorB)
						if colorA[0] > colorB[0] or colorA[1] > colorB[1] or colorA[2] > colorB[2]:
							copyProperty(rpr, conv_name, "inputA", "colorA")
							copyProperty(rpr, conv_name, "inputB", "colorB")
						else:
							copyProperty(rpr, conv_name, "inputA", "colorB")
							copyProperty(rpr, conv_name, "inputB", "colorA")
					elif mapDoesNotExist(conv_name, "colorA"):
						copyProperty(rpr, conv_name, "inputA", "colorA")
						copyProperty(rpr, conv_name, "inputB", "colorB")
					elif mapDoesNotExist(conv_name, "colorB"):
						copyProperty(rpr, conv_name, "inputA", "colorB")
						copyProperty(rpr, conv_name, "inputB", "colorA")
					else:
						copyProperty(rpr, conv_name, "inputA", "colorA")
						copyProperty(rpr, conv_name, "inputB", "colorB")
			elif operation == 3:
				setProperty(rpr, "operation", 2)
				if source == "outAlpha":
					copyProperty(rpr, conv_name, "inputA", "alphaA")
					copyProperty(rpr, conv_name, "inputB", "alphaB")
				else:
					copyProperty(rpr, conv_name, "inputA", "colorA")
					copyProperty(rpr, conv_name, "inputB", "colorB")
			elif operation == 6:
				setProperty(rpr, "operation", 1)
				if source == "outAlpha":
					if mapDoesNotExist(conv_name, "alphaA"):
						copyProperty(rpr, conv_name, "inputB", "alphaA")
						copyProperty(rpr, conv_name, "inputA", "alphaB")
					else:
						copyProperty(rpr, conv_name, "inputA", "alphaA")
						copyProperty(rpr, conv_name, "inputB", "alphaB")
				else:
					if mapDoesNotExist(conv_name, "alphaA"):
						copyProperty(rpr, conv_name, "inputB", "colorA")
						copyProperty(rpr, conv_name, "inputA", "colorB")
					else:
						copyProperty(rpr, conv_name, "inputA", "colorA")
						copyProperty(rpr, conv_name, "inputB", "colorB")
			elif operation == 7:
				setProperty(rpr, "operation", 25)
				if source == "outAlpha":
					copyProperty(rpr, conv_name, "inputA", "alphaB")
					copyProperty(rpr, conv_name, "inputB", "alphaA")
				else:
					copyProperty(rpr, conv_name, "inputA", "colorB")
					copyProperty(rpr, conv_name, "inputB", "colorA")
			elif operation == 8:
				setProperty(rpr, "operation", 20)
				if source == "outAlpha":
					copyProperty(rpr, conv_name, "inputA", "alphaA")
					copyProperty(rpr, conv_name, "inputB", "alphaB")
				else:
					copyProperty(rpr, conv_name, "inputA", "colorA")
					copyProperty(rpr, conv_name, "inputB", "colorB")


			# Logging to file
			end_log(conv_name)

		conversion_map = {
			"outAlpha": "outX",
			"outColor": "out",
			"outColorR": "outX",
			"outColorG": "outY",
			"outColorB": "outZ"
		}

		rpr += "." + conversion_map[source]
		return rpr


def convertReverse(conv_name, source):

	if cmds.objExists(conv_name + "_rpr"):
		rpr = conv_name + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
		rpr = cmds.rename(rpr, conv_name + "_rpr")

		# Logging to file
		start_log(conv_name, rpr)

		# Fields conversion
		setProperty(rpr, "inputA", (1, 1, 1))
		copyProperty(rpr, conv_name, "inputB", "input")
		setProperty(rpr, "operation", 1)

		# Logging to file
		end_log(conv_name)

	conversion_map = {
		"output": "out",
		"outputX": "outX",
		"outputY": "outY",
		"outputZ": "outZ"
	}

	rpr += "." + conversion_map[source]
	return rpr


def convertPreMultiply(conv_name, source):

	if cmds.objExists(conv_name + "_rpr"):
		rpr = conv_name + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
		rpr = cmds.rename(rpr, conv_name + "_rpr")

		# Logging to file
		start_log(conv_name, rpr)

		# Fields conversion
		copyProperty(rpr, conv_name, "inputA", "inColor")
		alpha = getProperty(conv_name, "inAlpha")
		setProperty(rpr, "inputB", (alpha, alpha, alpha))
		setProperty(rpr, "operation", 2)

		# Logging to file
		end_log(conv_name)

	conversion_map = {
		"outAlpha": "outX",
		"outColor": "out",
		"outColorR": "outX",
		"outColorG": "outY",
		"outColorB": "outZ"
	}

	rpr += "." + conversion_map[source]
	return rpr


def convertVectorProduct(conv_name, source):

	operation = getProperty(conv_name, "operation")
	if operation in (1, 2):
		if cmds.objExists(conv_name + "_rpr"):
			rpr = conv_name + "_rpr"
		else:
			rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_rpr")

			# Logging to file
			start_log(conv_name, rpr)

			# Fields conversion
			if operation == 1:
				setProperty(rpr, "operation", 11)
			elif operation == 2:
				setProperty(rpr, "operation", 12)

			copyProperty(rpr, conv_name, "inputA", "input1")
			copyProperty(rpr, conv_name, "inputB", "input2")

			# Logging to file
			end_log(conv_name)

		conversion_map = {
			"output": "out",
			"outputX": "outX",
			"outputY": "outY",
			"outputZ": "outZ"
		}

		rpr += "." + conversion_map[source]
		return rpr
	else:
		conv_name += "." + source
		return conv_name


def convertChannels(conv_name, source):

	if "outColor" in source:

		if cmds.objExists(conv_name + "_color_rpr"):
			rpr = conv_name + "_color_rpr"
		else:

			rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_color_rpr")

			# Logging to file
			start_log(conv_name, rpr)

			# Fields conversion
			copyProperty(rpr, conv_name, "inputA", "inColor")

			# Logging to file
			end_log(conv_name)

		conversion_map = {
			"outColor": "out",
			"outColorR": "outX",
			"outColorG": "outY",
			"outColorB": "outZ"
		}

		rpr += "." + conversion_map[source]
		return rpr

	elif "outAlpha" in source:

		if cmds.objExists(conv_name + "_alpha_rpr"):
			rpr = conv_name + "_alpha_rpr"
		else:

			rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
			rpr = cmds.rename(rpr, conv_name + "_alpha_rpr")

			# Logging to file
			start_log(conv_name, rpr)

			# Fields conversion
			copyProperty(rpr, conv_name, "inputA", "inAlpha")

			# Logging to file
			end_log(conv_name)

		conversion_map = {
			"outAlpha": "outX"
		}

		rpr += "." + conversion_map[source]
		return rpr


def convertmultiplyDivide(conv_name, source):

	if cmds.objExists(conv_name + "_rpr"):
		rpr = conv_name + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
		rpr = cmds.rename(rpr, conv_name + "_rpr")

		# Logging to file
		start_log(conv_name, rpr)

		# Fields conversion
		operation = getProperty(conv_name, "operation")
		operation_map = {
			1: 2,
			2: 3,
			3: 15
		}
		setProperty(rpr, "operation", operation_map[operation])
		copyProperty(rpr, conv_name, "inputA", "input1")
		copyProperty(rpr, conv_name, "inputB", "input2")
		
		# Logging to file
		end_log(conv_name)

	conversion_map = {
		"output": "out",
		"outputX": "outX",
		"outputY": "outY",
		"outputZ": "outZ"
	}

	rpr += "." + conversion_map[source]
	return rpr


# standard utilities
def convertStandardNode(vrayMaterial, source):

	not_converted_list = ("materialInfo", "defaultShaderList", "shadingEngine", "place2dTexture")
	try:
		for attr in cmds.listAttr(vrayMaterial):
			connection = cmds.listConnections(vrayMaterial + "." + attr)
			if connection:
				if cmds.objectType(connection[0]) not in not_converted_list and attr not in (source, "message"):
					obj, channel = cmds.connectionInfo(vrayMaterial + "." + attr, sourceFromDestination=True).split('.')
					source_name, source_attr = convertMaterial(obj, channel).split('.')
					connectProperty(source_name, source_attr, vrayMaterial, attr)
	except Exception as ex:
		pass

	return vrayMaterial + "." + source


# unsupported utilities
def convertUnsupportedNode(vrayMaterial, source, postfix="_UNSUPPORTED_NODE"):

	if cmds.objExists(vrayMaterial + postfix):
		rpr = vrayMaterial + postfix
	else:
		rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
		rpr = cmds.rename(rpr, vrayMaterial + postfix)

		# Logging to file
		start_log(vrayMaterial, rpr)

		# 2 connection save
		try:
			setProperty(rpr, "operation", 0)
			unsupported_connections = 0
			for attr in cmds.listAttr(vrayMaterial):
				connection = cmds.listConnections(vrayMaterial + "." + attr)
				if connection:
					if cmds.objectType(connection[0]) not in ("materialInfo", "defaultShaderList", "shadingEngine") and attr not in (source, "message"):
						if unsupported_connections < 2:
							obj, channel = cmds.connectionInfo(vrayMaterial + "." + attr, sourceFromDestination=True).split('.')
							source_name, source_attr = convertMaterial(obj, channel).split('.')
							valueType = type(getProperty(vrayMaterial, attr))
							if valueType == tuple:
								if unsupported_connections < 1:
									connectProperty(source_name, source_attr, rpr, "inputA")
								else:
									connectProperty(source_name, source_attr, rpr, "inputB")
							else:
								if unsupported_connections < 1:
									connectProperty(source_name, source_attr, rpr, "inputAX")
								else:
									connectProperty(source_name, source_attr, rpr, "inputBX")
							unsupported_connections += 1
		except Exception as ex:
			traceback.print_exc()

		# Logging to file
		end_log(vrayMaterial)

	sourceType = type(getProperty(vrayMaterial, source))
	if sourceType == tuple:
		rpr += ".out"
	else:
		rpr += ".outX"

	return rpr


def convertVRayTemperature(vr, source):

	if cmds.objExists(vr + "_rpr"):
		rpr = vr + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRArithmetic", asUtility=True)
		rpr = cmds.rename(rpr, vr + "_rpr")

		# Logging to file
		start_log(vr, rpr)

		# Fields conversion
		setProperty(rpr, 'operation', 0)
		setProperty(rpr, 'inputB', (0, 0, 0))
		colorMode = getProperty(vr, 'colorMode')
		if colorMode:
			setProperty(rpr, 'inputA', convertTemperature(getProperty(vr, 'temperature')))
		else:
			copyProperty(rpr, vr, "inputA", "color")
		

		# Logging to file
		end_log(vr)

	conversion_map = {
		"color": "out",
		"colorR": "outX",
		"colorG": "outY",
		"colorB": "outZ",
		"temperature": "out",
		"rgbMultiplier": "out",
		"gammaCorrection": "out",
		"alpha": "out",
		"red": "outX",
		"green": "outY",
		"blue": "outZ"
	}

	rpr += "." + conversion_map[source]
	return rpr


def convertVRayFresnel(vr, source):

	if cmds.objExists(vr + "_rpr"):
		rpr = vr + "_rpr"
	else:
		rpr = cmds.shadingNode("RPRBlendValue", asUtility=True)
		rpr = cmds.rename(rpr, vr + "_rpr")

		# Logging to file
		start_log(vr, rpr)

		# Fields conversion
		colorConstantFront = cmds.shadingNode("colorConstant", asUtility=True)
		copyProperty(colorConstantFront, vr, 'inColor', 'frontColor')

		colorConstantSide = cmds.shadingNode("colorConstant", asUtility=True)
		copyProperty(colorConstantSide, vr, 'inColor', 'sideColor')

		RPRFresnel = cmds.shadingNode("RPRFresnel", asUtility=True)
		copyProperty(RPRFresnel, vr, 'ior', 'IOR')

		connectProperty(colorConstantFront, 'outColor', rpr, 'inputA')
		connectProperty(colorConstantSide, 'outColor', rpr, 'inputB')
		connectProperty(RPRFresnel, 'out', rpr, 'weight')

		# Logging to file
		end_log(vr)

	conversion_map = {
		"outColor": "out",
		"outColorR": "outR",
		"outColorG": "outG",
		"outColorB": "outB"
	}

	rpr += "." + conversion_map[source]
	return rpr



# Create default uber material for unsupported material
def convertUnsupportedMaterial(vrayMaterial, source):

	assigned = checkAssign(vrayMaterial)
	
	if cmds.objExists(vrayMaterial + "_rpr"):
		rprMaterial = vrayMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRUberMaterial", asShader=True)
		rprMaterial = cmds.rename(rprMaterial, (vrayMaterial + "_UNSUPPORTED_MATERIAL"))

		# Check shading engine in vrayMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")

		# Logging to file
		start_log(vrayMaterial, rprMaterial)

		# set green color
		setProperty(rprMaterial, "diffuseColor", (0, 1, 0))

		end_log(vrayMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayMtl
########################

def convertVRayMtl(vrMaterial, source):

	assigned = checkAssign(vrMaterial)
	
	if cmds.objExists(vrMaterial + "_rpr"):
		rprMaterial = vrMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRUberMaterial", asShader=True)
		rprMaterial = cmds.rename(rprMaterial, vrMaterial + "_rpr")

		# Check shading engine in vrMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")
			
		# Enable properties, which are default in VRay
		defaultEnable(rprMaterial, vrMaterial, "diffuse", "diffuseColorAmount", "color")
		defaultEnable(rprMaterial, vrMaterial, "reflections", "reflectionColorAmount", "reflectionColor")
		defaultEnable(rprMaterial, vrMaterial, "refraction", "refractionColorAmount", "fogColor")
		
		# Logging to file
		start_log(vrMaterial, rprMaterial)

		# Basic parameters
		copyProperty(rprMaterial, vrMaterial, "diffuseColor", "color")
		copyProperty(rprMaterial, vrMaterial, "diffuseWeight", "diffuseColorAmount")
		copyProperty(rprMaterial, vrMaterial, "diffuseRoughness", "roughnessAmount")
		illumColor = getProperty(vrMaterial, 'illumColor')
		if illumColor[0] or illumColor[1] or illumColor[2]:
			setProperty(rprMaterial, 'emissive', 1)
			copyProperty(rprMaterial, vrMaterial, "emissiveColor", "illumColor")

		# opacity
		opacity_color = getProperty(vrMaterial, "opacityMap")
		if opacity_color[0] < 1 or opacity_color[1] < 1 or opacity_color[2] < 1:
			if mapDoesNotExist(vrMaterial, "opacityMap"):
				transparency = 1 - max(opacity_color)
				setProperty(rprMaterial, "transparencyLevel", transparency)
			else:
				invertValue(rprMaterial, vrMaterial, "transparencyLevel", "opacityMap")
			setProperty(rprMaterial, "transparencyEnable", 1)

		# reflection
		copyProperty(rprMaterial, vrMaterial, "reflectColor", "reflectionColor")
		copyProperty(rprMaterial, vrMaterial, "reflectWeight", "reflectionColorAmount")

		metalness = getProperty(vrMaterial, 'metalness')
		if metalness:
			setProperty(rprMaterial, 'reflectMetalMaterial', 1)
			copyProperty(rprMaterial, vrMaterial, 'reflectMetalness', 'metalness')
			copyProperty(rprMaterial, vrMaterial, 'reflectColor', 'color')

		useRoughness = getProperty(vrMaterial, 'useRoughness')
		if useRoughness:
			copyProperty(rprMaterial, vrMaterial, "reflectRoughness", "reflectionGlossiness")
		else:
			invertValue(rprMaterial, vrMaterial, 'reflectRoughness', 'reflectionGlossiness')

		lockFresnelIORToRefractionIOR = getProperty(vrMaterial, 'lockFresnelIORToRefractionIOR')
		if lockFresnelIORToRefractionIOR:
			setProperty(rprMaterial, 'refraction', 1)
			setProperty(rprMaterial, 'refractLinkToReflect', 1)

		fresnelIOR = getProperty(vrMaterial, 'fresnelIOR')
		if mapDoesNotExist(vrMaterial, 'fresnelIOR') and fresnelIOR > 10:
			setProperty(rprMaterial, "reflectIOR", 10)
		else:
			copyProperty(rprMaterial, vrMaterial, "reflectIOR", "fresnelIOR")

		if fresnelIOR < 0.1 or fresnelIOR > 10:
			setProperty(rprMaterial, 'reflectMetalMaterial', 1) 
			setProperty(rprMaterial, 'reflectMetalness', 1)

		copyProperty(rprMaterial, vrMaterial, "reflectAnisotropy", "anisotropy")
		anisotropyDerivation = getProperty(vrMaterial, 'anisotropyDerivation')
		if anisotropyDerivation:
			copyProperty(rprMaterial, vrMaterial, 'reflectAnisotropyRotation', 'anisotropyUVWGen')
		else:
			anisotropyRotation = getProperty(vrMaterial, 'anisotropyRotation')
			anisotropyRotation_mod = math.modf(anisotropyRotation)[0]
			anisotropyAxis = getProperty(vrMaterial, 'anisotropyAxis')
			if anisotropyAxis == 0:
				rprAnisotropyRotation = -0.403 * (anisotropyRotation_mod ** 3) + 0.5714 * (anisotropyRotation_mod ** 2) -1.086 * anisotropyRotation_mod - 0.1993
			elif anisotropyAxis == 1:
				rprAnisotropyRotation = -1 * anisotropyRotation_mod
			elif anisotropyAxis == 2:
				rprAnisotropyRotation = -1.5873 * anisotropyRotation_mod ** 3 + 2.4603 * anisotropyRotation_mod ** 2 - 1.373 * anisotropyRotation_mod + 0.7
				setProperty(rprMaterial, 'reflectAnisotropyRotation', rprAnisotropyRotation)

		global MAX_RAY_DEPTH

		reflectionsMaxDepth = getProperty(vrMaterial, 'reflectionsMaxDepth')
		if MAX_RAY_DEPTH and reflectionsMaxDepth < MAX_RAY_DEPTH:
			MAX_RAY_DEPTH = reflectionsMaxDepth

		refractionsMaxDepth = getProperty(vrMaterial, 'refractionsMaxDepth')
		if MAX_RAY_DEPTH and refractionsMaxDepth < MAX_RAY_DEPTH:
			MAX_RAY_DEPTH = refractionsMaxDepth

		copyProperty(rprMaterial, vrMaterial, 'refractColor', 'fogColor')
		refractColor = getProperty(vrMaterial, 'refractionColor')
		rpr_refl_weight = getProperty(vrMaterial, 'refractionColorAmount') * (0.3 * refractColor[0] + 0.59 * refractColor[1] + 0.11 * refractColor[2])
		setProperty(rprMaterial, 'refractWeight', rpr_refl_weight)
		invertValue(rprMaterial, vrMaterial, 'refractRoughness', 'refractionGlossiness')
		copyProperty(rprMaterial, vrMaterial, 'refractIor', 'refractionIOR')

		if getProperty(vrMaterial, 'refractionIOR') == 1:
			setProperty(rprMaterial, 'refractThinSurface', 1)

		traceRefractions = getProperty(vrMaterial, 'traceRefractions')
		if traceRefractions:
			setProperty(rprMaterial, 'refraction', 1)

		sssOn = getProperty(vrMaterial, 'sssOn')
		if sssOn:
			setProperty(rprMaterial, 'sssEnable', 1)

		# bump
		if not mapDoesNotExist(vrMaterial, 'bumpMap') and source != 'blend_bump':
			bumpMapType = getProperty(vrMaterial, 'bumpMapType')
			if bumpMapType in (0, 1):
				if bumpMapType == 0:
					rpr_node = cmds.shadingNode("RPRBump", asUtility=True)
				elif bumpMapType == 1:
					rpr_node = cmds.shadingNode("RPRNormal", asUtility=True)
				copyProperty(rpr_node, vrMaterial, 'color', 'bumpMap')
				copyProperty(rpr_node, vrMaterial, 'strength', 'bumpMult')
				setProperty(rprMaterial, 'normalMapEnable', 1)
				connectProperty(rpr_node, 'out', rprMaterial, 'normalMap')

		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayAlSurface
########################

def convertVRayAlSurface(vrMaterial, source):

	assigned = checkAssign(vrMaterial)
	
	if cmds.objExists(vrMaterial + "_rpr"):
		rprMaterial = vrMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRUberMaterial", asShader=True)
		rprMaterial = cmds.rename(rprMaterial, vrMaterial + "_rpr")

		# Check shading engine in vrMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")
		
		# Logging to file
		start_log(vrMaterial, rprMaterial)

		# Enable properties, which are default in VRay
		defaultEnable(rprMaterial, vrMaterial, "diffuse", "diffuseStrength", "diffuse")
		defaultEnable(rprMaterial, vrMaterial, "reflections", "reflect1Strength", "reflect1")

		# opacity
		opacity = getProperty(vrMaterial, "opacity")
		if opacity < 1:
			if mapDoesNotExist(vrMaterial, "opacity"):
				transparency = 1 - opacity
				setProperty(rprMaterial, "transparencyLevel", transparency)
			else:
				invertValue(rprMaterial, vrMaterial, "transparencyLevel", "opacityMap")
			setProperty(rprMaterial, "transparencyEnable", 1)

		# diffuse parameters
		copyProperty(rprMaterial, vrMaterial, "diffuseColor", "diffuse")
		copyProperty(rprMaterial, vrMaterial, "diffuseWeight", "diffuseStrength")

		if not mapDoesNotExist(vrMaterial, 'diffuseBumpMap'):
			diffuseBumpType = getProperty(vrMaterial, 'diffuseBumpType')
			if diffuseBumpType in (0, 1):
				if diffuseBumpType == 0:
					rpr_node = cmds.shadingNode("RPRBump", asUtility=True)
				elif diffuseBumpType == 1:
					rpr_node = cmds.shadingNode("RPRNormal", asUtility=True)
				copyProperty(rpr_node, vrMaterial, 'color', 'diffuseBumpMap')
				copyProperty(rpr_node, vrMaterial, 'strength', 'diffuseBumpAmount')
				setProperty(rprMaterial, 'useShaderNormal', 0)
				connectProperty(rpr_node, 'out', rprMaterial, 'diffuseNormal')

		# refl
		copyProperty(rprMaterial, vrMaterial, "reflectColor", "reflect1")
		copyProperty(rprMaterial, vrMaterial, "reflectWeight", "reflect1Strength")
		copyProperty(rprMaterial, vrMaterial, "reflectRoughness", "reflect1Roughness")
		copyProperty(rprMaterial, vrMaterial, "reflectIOR", "reflect1IOR")

		if not mapDoesNotExist(vrMaterial, 'reflect1BumpMap'):
			reflect1BumpType = getProperty(vrMaterial, 'reflect1BumpType')
			if reflect1BumpType in (0, 1):
				if reflect1BumpType == 0:
					rpr_node = cmds.shadingNode("RPRBump", asUtility=True)
				elif reflect1BumpType == 1:
					rpr_node = cmds.shadingNode("RPRNormal", asUtility=True)
				copyProperty(rpr_node, vrMaterial, 'color', 'reflect1BumpMap')
				copyProperty(rpr_node, vrMaterial, 'strength', 'reflect1BumpAmount')
				setProperty(rprMaterial, 'reflectUseShaderNormal', 0)
				connectProperty(rpr_node, 'out', rprMaterial, 'reflectNormal')

		# sss
		copyProperty(rprMaterial, vrMaterial, 'sssWeight', 'sssMix')
		if getProperty(vrMaterial, 'sssMix') > 0:
			setProperty(rprMaterial, 'sssEnable', 1)

		# sss1
		sss1_rad_x_den_scale = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss1_rad_x_den_scale = cmds.rename(sss1_rad_x_den_scale, 'sss1_rad_x_den_scale')
		setProperty(sss1_rad_x_den_scale, 'operation', 2)
		copyProperty(sss1_rad_x_den_scale, vrMaterial, 'inputA', 'sss1Radius')
		copyProperty(sss1_rad_x_den_scale, vrMaterial, 'inputB', 'sssDensityScale')

		sss1_rad_x_weight = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss1_rad_x_weight = cmds.rename(sss1_rad_x_weight, 'sss1_rad_x_weight')
		setProperty(sss1_rad_x_weight, 'operation', 2)
		connectProperty(sss1_rad_x_den_scale, 'out', sss1_rad_x_weight, 'inputA')
		copyProperty(sss1_rad_x_weight, vrMaterial, 'inputB', 'sss1Weight')

		sss1_rad_x_color = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss1_rad_x_color = cmds.rename(sss1_rad_x_color, 'sss1_rad_x_color')
		setProperty(sss1_rad_x_color, 'operation', 2)
		connectProperty(sss1_rad_x_weight, 'out', sss1_rad_x_color, 'inputA')
		copyProperty(sss1_rad_x_color, vrMaterial, 'inputB', 'sss1Color')

		# sss2

		sss2_rad_x_den_scale = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss2_rad_x_den_scale = cmds.rename(sss2_rad_x_den_scale, 'sss2_rad_x_den_scale')
		setProperty(sss2_rad_x_den_scale, 'operation', 2)
		copyProperty(sss2_rad_x_den_scale, vrMaterial, 'inputA', 'sss2Radius')
		copyProperty(sss2_rad_x_den_scale, vrMaterial, 'inputB', 'sssDensityScale')

		sss2_rad_x_weight = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss2_rad_x_weight = cmds.rename(sss2_rad_x_weight, 'sss2_rad_x_weight')
		setProperty(sss2_rad_x_weight, 'operation', 2)
		connectProperty(sss2_rad_x_den_scale, 'out', sss2_rad_x_weight, 'inputA')
		copyProperty(sss2_rad_x_weight, vrMaterial, 'inputB', 'sss2Weight')

		sss2_rad_x_color = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss2_rad_x_color = cmds.rename(sss2_rad_x_color, 'sss2_rad_x_color')
		setProperty(sss2_rad_x_color, 'operation', 2)
		connectProperty(sss2_rad_x_weight, 'out', sss2_rad_x_color, 'inputA')
		copyProperty(sss2_rad_x_color, vrMaterial, 'inputB', 'sss2Color')

		# sss3

		sss3_rad_x_den_scale = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss3_rad_x_den_scale = cmds.rename(sss3_rad_x_den_scale, 'sss3_rad_x_den_scale')
		setProperty(sss3_rad_x_den_scale, 'operation', 2)
		copyProperty(sss3_rad_x_den_scale, vrMaterial, 'inputA', 'sss3Radius')
		copyProperty(sss3_rad_x_den_scale, vrMaterial, 'inputB', 'sssDensityScale')

		sss3_rad_x_weight = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss3_rad_x_weight = cmds.rename(sss3_rad_x_weight, 'sss3_rad_x_weight')
		setProperty(sss3_rad_x_weight, 'operation', 2)
		connectProperty(sss3_rad_x_den_scale, 'out', sss2_rad_x_weight, 'inputA')
		copyProperty(sss3_rad_x_weight, vrMaterial, 'inputB', 'sss3Weight')

		sss3_rad_x_color = cmds.shadingNode("RPRArithmetic", asUtility=True)
		sss3_rad_x_color = cmds.rename(sss3_rad_x_color, 'sss3_rad_x_color')
		setProperty(sss3_rad_x_color, 'operation', 2)
		connectProperty(sss3_rad_x_weight, 'out', sss3_rad_x_color, 'inputA')
		copyProperty(sss3_rad_x_color, vrMaterial, 'inputB', 'sss3Color')

		# sss radius
		mix_sss1_sss2 = cmds.shadingNode("RPRArithmetic", asUtility=True)
		mix_sss1_sss2 = cmds.rename(mix_sss1_sss2, 'mix_sss1_color_and_sss2_color')
		setProperty(mix_sss1_sss2, 'operation', 20)
		connectProperty(sss1_rad_x_color, 'out', mix_sss1_sss2, 'inputA')
		connectProperty(sss2_rad_x_color, 'out', mix_sss1_sss2, 'inputB')

		mix_sss3 = cmds.shadingNode("RPRArithmetic", asUtility=True)
		mix_sss3 = cmds.rename(mix_sss3, 'mix_sss3_color')
		setProperty(mix_sss3, 'operation', 20)
		connectProperty(mix_sss1_sss2, 'out', mix_sss3, 'inputA')
		connectProperty(sss3_rad_x_color, 'out', mix_sss3, 'inputB')
		connectProperty(mix_sss3, 'out', rprMaterial, 'subsurfaceRadius0')

		# get radius weight
		sss_radius_dict = {'sss1Radius': getProperty(vrMaterial, 'sss1Radius'), 'sss2Radius': getProperty(vrMaterial, 'sss2Radius'), 'sss3Radius': getProperty(vrMaterial, 'sss3Radius')}
		highest_radius = max(sss_radius_dict, key=sss_radius_dict.get)
		sss_radius_dict.pop(highest_radius)
		middle_radius = max(sss_radius_dict, key=sss_radius_dict.get)
		lowest_radius = min(sss_radius_dict, key=sss_radius_dict.get)
		lowest_radius_weight = 1 / (getProperty(vrMaterial, lowest_radius) * 100 / getProperty(vrMaterial, highest_radius))
		middle_radius_weight = 1 / (getProperty(vrMaterial, middle_radius) * 100 / getProperty(vrMaterial, highest_radius))

		# volume and backscattering color
		low_and_mid_with_low_weight = cmds.shadingNode("RPRBlendValue", asUtility=True)
		low_and_mid_with_low_weight = cmds.rename(low_and_mid_with_low_weight, 'low_and_mid_with_low_weight')
		connectProperty(sss1_rad_x_color, 'out', low_and_mid_with_low_weight, 'inputA')
		connectProperty(sss3_rad_x_color, 'out', low_and_mid_with_low_weight, 'inputB')
		setProperty(low_and_mid_with_low_weight, 'weight', lowest_radius_weight)

		high_and_mid_with_low_weight = cmds.shadingNode("RPRBlendValue", asUtility=True)
		high_and_mid_with_low_weight = cmds.rename(high_and_mid_with_low_weight, 'high_and_mid_with_low_weight')
		connectProperty(low_and_mid_with_low_weight, 'out', high_and_mid_with_low_weight, 'inputA')
		connectProperty(sss2_rad_x_color, 'out', high_and_mid_with_low_weight, 'inputB')
		setProperty(high_and_mid_with_low_weight, 'weight', middle_radius_weight)

		setProperty(rprMaterial, 'separateBackscatterColor', 1)
		connectProperty(high_and_mid_with_low_weight, 'out', rprMaterial, 'backscatteringColor')
		connectProperty(high_and_mid_with_low_weight, 'out', rprMaterial, 'volumeScatter')

		# bump
		if not mapDoesNotExist(vrMaterial, 'bumpMap'):
			bumpType = getProperty(vrMaterial, 'bumpType')
			if bumpType in (0, 1):
				if bumpType == 0:
					rpr_node = cmds.shadingNode("RPRBump", asUtility=True)
				elif bumpType == 1:
					rpr_node = cmds.shadingNode("RPRNormal", asUtility=True)
				copyProperty(rpr_node, vrMaterial, 'color', 'bumpMap')
				copyProperty(rpr_node, vrMaterial, 'strength', 'bumpAmount')
				setProperty(rprMaterial, 'normalMapEnable', 1)
				connectProperty(rpr_node, 'out', rprMaterial, 'normalMap')



		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayCarPaintMtl
########################

def convertVRayCarPaintMtl(vrMaterial, source):

	assigned = checkAssign(vrMaterial)
	
	if cmds.objExists(vrMaterial + "_rpr"):
		rprMaterial = vrMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRUberMaterial", asShader=True)
		rprMaterial = cmds.rename(rprMaterial, vrMaterial + "_rpr")

		# Check shading engine in vrMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")
		
		# Logging to file
		start_log(vrMaterial, rprMaterial)

		defaultEnable(rprMaterial, vrMaterial, "clearCoat", "coat_strength", "coat_color")		

		# diffuse parameters
		copyProperty(rprMaterial, vrMaterial, "diffuseColor", "color")

		# refl 
		setProperty(rprMaterial, 'reflections', 1)
		copyProperty(rprMaterial, vrMaterial, "reflectColor", "color")
		setProperty(rprMaterial, 'reflectMetalMaterial', 1)
		copyProperty(rprMaterial, vrMaterial, 'reflectMetalness', 'base_reflection')
		invertValue(rprMaterial, vrMaterial, 'reflectRoughness', 'base_glossiness')

		if not mapDoesNotExist(vrMaterial, 'base_bumpMap'):
			base_bumpMapType = getProperty(vrMaterial, 'base_bumpMapType')
			if base_bumpMapType in (0, 1):
				if base_bumpMapType == 0:
					rpr_node = cmds.shadingNode("RPRBump", asUtility=True)
				elif base_bumpMapType == 1:
					rpr_node = cmds.shadingNode("RPRNormal", asUtility=True)
				copyProperty(rpr_node, vrMaterial, 'color', 'base_bumpMap')
				copyProperty(rpr_node, vrMaterial, 'strength', 'base_bumpMult')
				setProperty(rprMaterial, 'normalMapEnable', 1)
				connectProperty(rpr_node, 'out', rprMaterial, 'normalMap')

		if not getProperty(vrMaterial, 'base_trace_reflections'):
			setProperty(rprMaterial, 'reflectMetalness', 0)

		# coat
		if getProperty(vrMaterial, 'coat_trace_reflections'):

			copyProperty(rprMaterial, vrMaterial, 'coatWeight', 'coat_strength')
			copyProperty(rprMaterial, vrMaterial, 'coatColor', 'coat_color') 
			invertValue(rprMaterial, vrMaterial, 'coatRoughness', 'coat_glossiness')

			if not mapDoesNotExist(vrMaterial, 'coat_bumpMap'):
				coat_bumpMapType = getProperty(vrMaterial, 'coat_bumpMapType')
				if coat_bumpMapType in (0, 1):
					if coat_bumpMapType == 0:
						rpr_node = cmds.shadingNode("RPRBump", asUtility=True)
					elif coat_bumpMapType == 1:
						rpr_node = cmds.shadingNode("RPRNormal", asUtility=True)
					copyProperty(rpr_node, vrMaterial, 'color', 'coat_bumpMap')
					copyProperty(rpr_node, vrMaterial, 'strength', 'coat_bumpMult')
					setProperty(rprMaterial, 'coatUseShaderNormal', 0)
					connectProperty(rpr_node, 'out', rprMaterial, 'normalMap')

		else:
			setProperty(rprMaterial, 'clearCoat', 0)

		if getProperty(vrMaterial, 'coat_trace_reflections') and getProperty(vrMaterial, 'coat_strength') > 0:
			blend_material = cmds.shadingNode("RPRBlendMaterial", asShader=True)
			blend_sg = blend_material + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=blend_sg)
			connectProperty(blend_material, "outColor", blend_sg, "surfaceShader")

			metal_uber = cmds.shadingNode("RPRUberMaterial", asShader=True)
			setProperty(metal_uber, 'reflections', 1)
			setProperty(metal_uber, 'reflectRoughness', 0)
			setProperty(metal_uber, 'reflectMetalMaterial', 1)
			setProperty(metal_uber, 'reflectMetalness', 1)

			connectProperty(rprMaterial, 'outColor', blend_material, 'color0')
			connectProperty(metal_uber, 'outColor', blend_material, 'color1')
			copyProperty(blend_material, vrMaterial, 'weight', 'coat_strength')

			rprMaterial = blend_material


		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayLightMtl
########################

def convertVRayLightMtl(vrMaterial, source):

	assigned = checkAssign(vrMaterial)
	
	if cmds.objExists(vrMaterial + "_rpr"):
		rprMaterial = vrMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRUberMaterial", asShader=True)
		rprMaterial = cmds.rename(rprMaterial, vrMaterial + "_rpr")

		# Check shading engine in vrMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")
		
		# Logging to file
		start_log(vrMaterial, rprMaterial)

		setProperty(rprMaterial, 'diffuse', 0)

		setProperty(rprMaterial, 'emissive', 1)
		colorMode = getProperty(vrMaterial, 'colorMode')
		if colorMode:
			setProperty(rprMaterial, 'emissiveColor', convertTemperature(getProperty(vrMaterial, 'temperature')))
		else:
			copyProperty(rprMaterial, vrMaterial, 'emissiveColor', 'color')
		copyProperty(rprMaterial, vrMaterial, 'emissiveIntensity', 'colorMultiplier')

		if getProperty(vrMaterial, 'emitOnBackSide'):
			setProperty(rprMaterial, 'emissiveDoubleSided', 1)

		# opacity
		opacity_color = getProperty(vrMaterial, "opacity")
		if opacity_color[0] < 1 or opacity_color[1] < 1 or opacity_color[2] < 1:
			if mapDoesNotExist(vrMaterial, "opacity"):
				transparency = 1 - max(opacity_color)
				setProperty(rprMaterial, "transparencyLevel", transparency)
			else:
				invertValue(rprMaterial, vrMaterial, "transparencyLevel", "opacity")
			setProperty(rprMaterial, "transparencyEnable", 1)

		if getProperty(vrMaterial, 'multiplyColorByOpacity'):
			mult_color_by_opacity = cmds.shadingNode("RPRArithmetic", asUtility=True)
			mult_color_by_opacity = cmds.rename(mult_color_by_opacity, 'mult_color_by_opacity')
			setProperty(mult_color_by_opacity, 'operation', 2)
			copyProperty(mult_color_by_opacity, rprMaterial, 'inputA', 'emissiveColor')
			copyProperty(mult_color_by_opacity, rprMaterial, 'inputB', 'transparencyLevel')
			connectProperty(mult_color_by_opacity, 'out', rprMaterial, 'emissiveColor')

		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayHairNextMtl
########################

def convertVRayHairNextMtl(vrMaterial, source):

	assigned = checkAssign(vrMaterial)
	
	if cmds.objExists(vrMaterial + "_rpr"):
		rprMaterial = vrMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRUberMaterial", asShader=True)
		rprMaterial = cmds.rename(rprMaterial, vrMaterial + "_rpr")

		# Check shading engine in vrMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")
		
		# Logging to file
		start_log(vrMaterial, rprMaterial)

		setProperty(rprMaterial, 'reflections', 1)
		setProperty(rprMaterial, 'clearCoat', 1)

		setProperty(rprMaterial, 'reflectAnisotropy', 1)
		setProperty(rprMaterial, 'reflectAnisotropyRotation', 0.35)
		setProperty(rprMaterial, 'reflectIOR', 10)

		# transparency
		transparency = getProperty(vrMaterial, "transparency")
		if transparency < 1:
			if mapDoesNotExist(vrMaterial, "transparency"):
				transparency = 1 - transparency
				setProperty(rprMaterial, "transparencyLevel", transparency)
			else:
				invertValue(rprMaterial, vrMaterial, "transparencyLevel", "transparency")
			setProperty(rprMaterial, "transparencyEnable", 1)

		copyProperty(rprMaterial, vrMaterial, 'diffuseColor', 'diffuse_color')
		copyProperty(rprMaterial, vrMaterial, 'diffuseWeight', 'diffuse_amount')
		invertValue(rprMaterial, vrMaterial, 'coatRoughness', 'primary_glossiness_boost')
		invertValue(rprMaterial, vrMaterial, 'reflectRoughness', 'glossiness')

		arith1 = cmds.shadingNode("RPRArithmetic", asUtility=True)
		setProperty(arith1, 'operation', 2)
		copyProperty(arith1, vrMaterial, 'inputA', 'dye_color')
		invertValue(arith1, vrMaterial, 'inputB', 'melanin')

		arith2 = cmds.shadingNode('RPRArithmetic', asUtility=True)
		setProperty(arith2, 'operation', 2)
		connectProperty(arith1, 'out', arith2, 'inputA')
		setProperty(arith2, 'inputB', (0.3, 0.3, 0.3))

		arith3 = cmds.shadingNode('RPRArithmetic', asUtility=True)
		setProperty(arith3, 'operation', 2)
		connectProperty(arith2, 'out', arith3, 'inputA')
		copyProperty(arith3, vrMaterial, 'inputB', 'secondary_tint')
		connectProperty(arith3, 'out', rprMaterial, 'reflectColor')

		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayBlendMtl
########################


def convertVRayBlendMtl(vrMaterial, source):
	assigned = checkAssign(vrMaterial)
	
	if cmds.objExists(vrMaterial + "_rpr"):
		rprMaterial = vrMaterial + "_rpr"
	else:
		# Creating new Uber material
		rprMaterial = cmds.shadingNode("RPRBlendMaterial", asShader=True)
		
		# Logging to file
		start_log(vrMaterial, rprMaterial)

		baseMtl = cmds.listConnections(vrMaterial + '.base_material')
		if baseMtl:
			connectProperty(convertMaterial(baseMtl[0], ''), 'outColor', rprMaterial, 'color0')
		else:
			baseMtl = cmds.shadingNode("RPRUberMaterial", asShader=True)
			setProperty(baseMtl, 'transparencyEnable', 1)
			setProperty(baseMtl, 'transparencyLevel', 0)
			connectProperty(baseMtl, 'outColor', rprMaterial, 'color0')

		# materials count
		materials_count = 0
		for i in range(0, 9):
			if cmds.listConnections(vrMaterial + '.coat_material_{}'.format(i)):
				materials_count += 1

		first_material = True
		for i in range(0, 9):
			coatMaterial = cmds.listConnections(vrMaterial + '.coat_material_{}'.format(i))
			if coatMaterial:
				if materials_count > 1:
					if first_material:
						connectProperty(convertMaterial(coatMaterial[0], ''), 'outColor', rprMaterial, 'color1')
						copyProperty(rprMaterial, vrMaterial, 'weight', 'blend_amount_{}'.format(i))	
						first_material = False
					else:
						prev_rprMaterial = rprMaterial
						rprMaterial = cmds.shadingNode("RPRBlendMaterial", asShader=True)
						connectProperty(prev_rprMaterial, 'outColor', rprMaterial, 'color0')
						connectProperty(convertMaterial(coatMaterial[0], ''), 'outColor', rprMaterial, 'color1')
						copyProperty(rprMaterial, vrMaterial, 'weight', 'blend_amount_{}'.format(i))	
				else:
					connectProperty(convertMaterial(coatMaterial[0], ''), 'outColor', rprMaterial, 'color1')
					copyProperty(rprMaterial, vrMaterial, 'weight', 'blend_amount_{}'.format(i))	

		# rename and create SG for last blend material
		rprMaterial = cmds.rename(rprMaterial, vrMaterial + "_rpr")

		# Check shading engine in vrMaterial
		if assigned:
			sg = rprMaterial + "SG"
			cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
			connectProperty(rprMaterial, "outColor", sg, "surfaceShader")

		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


######################## 
##  VRayBumpMtl
########################

def convertVRayBumpMtl(vrMaterial, source):

	baseMtl = cmds.listConnections(vrMaterial + '.base_material')[0]

	if cmds.objExists(baseMtl + "_rpr"):
		rprMaterial = baseMtl + "_rpr"
	else:
		# script will return material.blend_bump, we need only material name
		rprMaterial = convertMaterial(baseMtl, "blend_bump").split('.')[0]

		start_log(vrMaterial, rprMaterial)

		sg = rprMaterial + "SG"
		cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
		connectProperty(rprMaterial, "outColor", sg, "surfaceShader")

		materialType = cmds.objectType(rprMaterial)
		if materialType == 'RPRUberMaterial':
			if not mapDoesNotExist(vrMaterial, 'bumpMap'):
				base_mtl_map_type = getProperty(baseMtl, 'bumpMapType')
				bump_map_type = getProperty(vrMaterial, 'bumpMapType')
				if mapDoesNotExist(baseMtl, 'bumpMap') or base_mtl_map_type != bump_map_type:
					setProperty(rprMaterial,'normalMapEnable', 1)
					copyProperty(rprMaterial, vrMaterial, 'normalMap', 'bumpMap')
				else:
					if base_mtl_map_type in (0, 1):
						if base_mtl_map_type == 0:
							map_node = cmds.shadingNode("RPRBump", asUtility=True)
						elif base_mtl_map_type == 1:
							map_node = cmds.shadingNode("RPRNormal", asUtility=True)

						bumps_blend = cmds.shadingNode("RPRBlendValue", asUtility=True)
						bumps_blend = cmds.rename(bumps_blend, "Blend bumps")
						copyProperty(bumps_blend, baseMtl, 'inputA', 'bumpMap')
						copyProperty(bumps_blend, vrMaterial, 'inputB', 'bumpMap')
						setProperty(bumps_blend, "weight", 0.2)
						connectProperty(bumps_blend, 'out', map_node, 'color')

						setProperty(rprMaterial,'normalMapEnable', 1)
						connectProperty(map_node, 'out', rprMaterial, 'normalMap')

		end_log(vrMaterial)

	if source:
		rprMaterial += "." + source
	return rprMaterial


def convertVRayLightDomeShape(dome_light):

	if cmds.objExists("RPRIBL"):
		iblShape = "RPRIBLShape"
		iblTransform = "RPRIBL"
	else:
		# create IBL node
		iblShape = cmds.createNode("RPRIBL", n="RPRIBLShape")
		iblTransform = cmds.listRelatives(iblShape, p=True)[0]
		setProperty(iblTransform, "scale", (1001.25, 1001.25, 1001.25))

	# Logging to file 
	start_log(dome_light, iblShape)
  
	copyProperty(iblShape, dome_light, 'intensity', 'intensityMult')

	# Copy properties from vr dome light
	domeTransform = cmds.listRelatives(dome_light, p=True)[0]
	setProperty(iblTransform, "rotateY", getProperty(domeTransform, "rotateY") - 90)
	
	file = cmds.listConnections(dome_light + ".domeTex")
	if file:
		setProperty(iblTransform, "filePath", getProperty(file[0], "fileTextureName"))

	invisible = getProperty(dome_light, 'invisible')
	if invisible:
		setProperty(iblShape, 'display', 0)
	else:
		setProperty(iblShape, 'display', 1)
		   
	# Logging to file
	end_log(dome_light) 


def convertVRayLightIESShape(vr_light): 

	# Vray light transform
	splited_name = vr_light.split("|")
	vrTransform = "|".join(splited_name[0:-1])
	group = "|".join(splited_name[0:-2])

	if cmds.objExists(vrTransform + "_rpr"):
		rprTransform = vrTransform + "_rpr"
		rprLightShape = cmds.listRelatives(rprTransform)[0]
	else: 
		rprLightShape = cmds.createNode("RPRIES", n="RPRIESLight")
		rprLightShape = cmds.rename(rprLightShape, splited_name[-1] + "_rpr")
		rprTransform = cmds.listRelatives(rprLightShape, p=True)[0]
		rprTransform = cmds.rename(rprTransform, splited_name[-2] + "_rpr")
		rprLightShape = cmds.listRelatives(rprTransform)[0]

		if group:
			cmds.parent(rprTransform, group)

		rprTransform = group + "|" + rprTransform
		rprLightShape = rprTransform + "|" + rprLightShape

	# Logging to file 
	start_log(vr_light, rprLightShape)

	# Copy properties from vrLight
	vrayIntensity = getProperty(vr_light, 'intensityMult')
	setProperty(rprLightShape, 'intensity', 19.9024909 * vrayIntensity ** 3 - 14.3247047 * vrayIntensity ** 2 + 3.4341693 * vrayIntensity + 0.0762945)

	colorMode = getProperty(vr_light, 'colorMode')
	if colorMode:
		setProperty(rprLightShape, 'color', convertTemperature(getProperty(vr_light, 'temperature')))
	else:
		copyProperty(rprLightShape, vr_light, "color", "lightColor")
	
	setProperty(rprLightShape, "iesFile", getProperty(vr_light, "iesFile"))
	
	copyProperty(rprTransform, vrTransform, "translate", "translate")
	setProperty(rprTransform, 'rotateX', getProperty(vrTransform, 'rotateX') - 90)
	copyProperty(rprTransform, vrTransform, "rotateY", "rotateY")
	copyProperty(rprTransform, vrTransform, "rotateZ", "rotateZ")
	copyProperty(rprTransform, vrTransform, "scale", "scale")

	copyProperty(rprLightShape, vr_light, 'visibility', 'display')

	# Logging to file
	end_log(vr_light) 


def convertVRayLightRectShape(vr_light): 

	# Redshift light transform
	splited_name = vr_light.split("|")
	vrTransform = "|".join(splited_name[0:-1])
	group = "|".join(splited_name[0:-2])

	if cmds.objExists(vrTransform + "_rpr"):
		rprTransform = vrTransform + "_rpr"
		rprLightShape = cmds.listRelatives(rprTransform)[0]
	else: 
		rprLightShape = cmds.createNode("RPRPhysicalLight", n="RPRPhysicalLightShape")
		rprLightShape = cmds.rename(rprLightShape, splited_name[-1] + "_rpr")
		rprTransform = cmds.listRelatives(rprLightShape, p=True)[0]
		rprTransform = cmds.rename(rprTransform, splited_name[-2] + "_rpr")
		rprLightShape = cmds.listRelatives(rprTransform)[0]

		if group:
			cmds.parent(rprTransform, group)

		rprTransform = group + "|" + rprTransform
		rprLightShape = rprTransform + "|" + rprLightShape

	# Logging to file 
	start_log(vr_light, rprLightShape)

	# Copy properties from vrLight

	light_units = getProperty(vr_light, 'units')
	if light_units in (0, 1, 4):
		setProperty(rprLightShape, 'intensityUnits', 1)
		copyProperty(rprLightShape, vr_light, 'lightIntensity', 'intensityMult')
	elif light_units == 2:
		setProperty(rprLightShape, 'intensityUnits', 1)
		setProperty(rprLightShape, 'lightIntensity', getProperty(vr_light, 'intensityMult') / 1000)
	elif light_units == 3:
		setProperty(rprLightShape, 'intensityUnits', 2)
		copyProperty(rprLightShape, vr_light, 'lightIntensity', 'intensityMult')

	if getProperty(vr_light, 'shapeType'):
		setProperty(rprLightShape, 'areaLightShape', 0)
		setProperty(rprTransform, 'scaleX', getProperty(vr_light, 'uSize') * getProperty(vrTransform, 'scaleX'))
		setProperty(rprTransform, 'scaleY', getProperty(vr_light, 'uSize') * getProperty(vrTransform, 'scaleY'))
	else:
		setProperty(rprLightShape, 'areaLightShape', 3)
		setProperty(rprTransform, 'scaleX', getProperty(vr_light, 'uSize') * getProperty(vrTransform, 'scaleX'))
		setProperty(rprTransform, 'scaleY', getProperty(vr_light, 'vSize') * getProperty(vrTransform, 'scaleY'))

	copyProperty(rprLightShape, vr_light, 'colorMode', 'colorMode')
	if getProperty(vr_light, 'colorMode') == 1:
		mel.eval("onTemperatureChanged(\"{}\")".format(rprLightShape))

	copyProperty(rprLightShape, vr_light, 'temperature', 'temperature')
	copyProperty(rprLightShape, vr_light, 'colorPicker', 'lightColor')

	if getProperty(vr_light, 'useRectTex'):
		rectTex_mult_rectTexA = cmds.shadingNode("RPRArithmetic", asUtility=True)
		setProperty(rectTex_mult_rectTexA, 'operation', 2)
		copyProperty(rectTex_mult_rectTexA, vr_light, 'inputA', 'rectTex')
		copyProperty(rectTex_mult_rectTexA, vr_light, 'inputB', 'rectTexA')
		if getProperty(vr_light, 'multiplyByTheLightColor'):
			multiplyByTheLightColor = cmds.shadingNode("RPRArithmetic", asUtility=True)
			setProperty(multiplyByTheLightColor, 'operation', 2)
			copyProperty(multiplyByTheLightColor, vr_light, 'inputA', 'lightColor')
			connectProperty(rectTex_mult_rectTexA, 'out', multiplyByTheLightColor, 'inputB')
			connectProperty(multiplyByTheLightColor, 'out', rprLightShape, 'colorPicker')
		else:
			connectProperty(rectTex_mult_rectTexA, 'out', rprLightShape, 'colorPicker')

	copyProperty(rprTransform, vrTransform, "translate", "translate")
	copyProperty(rprTransform, vrTransform, "rotate", "rotate")

	if getProperty(vr_light, 'invisible'):
		setProperty(rprLightShape, 'areaLightVisible', 0)
	else:
		setProperty(rprLightShape, 'areaLightVisible', 1)

	# Logging to file
	end_log(vr_light) 


def convertVRayLightSphereShape(vr_light): 

	# Redshift light transform
	splited_name = vr_light.split("|")
	vrTransform = "|".join(splited_name[0:-1])
	group = "|".join(splited_name[0:-2])

	if cmds.objExists(vrTransform + "_rpr"):
		rprTransform = vrTransform + "_rpr"
		rprLightShape = cmds.listRelatives(rprTransform)[0]
	else: 
		rprLightShape = cmds.createNode("RPRPhysicalLight", n="RPRPhysicalLightShape")
		rprLightShape = cmds.rename(rprLightShape, splited_name[-1] + "_rpr")
		rprTransform = cmds.listRelatives(rprLightShape, p=True)[0]
		rprTransform = cmds.rename(rprTransform, splited_name[-2] + "_rpr")
		rprLightShape = cmds.listRelatives(rprTransform)[0]

		if group:
			cmds.parent(rprTransform, group)

		rprTransform = group + "|" + rprTransform
		rprLightShape = rprTransform + "|" + rprLightShape

	# Logging to file 
	start_log(vr_light, rprLightShape)

	# Copy properties from vrLight

	light_units = getProperty(vr_light, 'units')
	if light_units in (0, 1, 4):
		setProperty(rprLightShape, 'intensityUnits', 1)
		copyProperty(rprLightShape, vr_light, 'lightIntensity', 'intensityMult')
	elif light_units == 2:
		setProperty(rprLightShape, 'intensityUnits', 1)
		setProperty(rprLightShape, 'lightIntensity', getProperty(vr_light, 'intensityMult') / 1000)
	elif light_units == 3:
		setProperty(rprLightShape, 'intensityUnits', 2)
		copyProperty(rprLightShape, vr_light, 'lightIntensity', 'intensityMult')

	copyProperty(rprLightShape, vr_light, 'colorMode', 'colorMode')
	if getProperty(vr_light, 'colorMode') == 1:
		mel.eval("onTemperatureChanged(\"{}\")".format(rprLightShape))

	copyProperty(rprLightShape, vr_light, 'temperature', 'temperature')
	copyProperty(rprLightShape, vr_light, 'colorPicker', 'lightColor')

	if getProperty(vr_light, 'invisible'):
		setProperty(rprLightShape, 'areaLightVisible', 0)
	else:
		setProperty(rprLightShape, 'areaLightVisible', 1)

	setProperty(rprLightShape, 'areaLightShape', 4)
	sphere, polySphere = cmds.polySphere()

	try:
		cmds.select(clear=True)
		setProperty(rprLightShape, "areaLightSelectingMesh", 1)
		cmds.select(sphere)
	except Exception as ex:
		traceback.print_exc()
		print("Failed to attach mesh to rpr physical light")

	copyProperty(sphere, vrTransform, "translate", "translate")
	copyProperty(sphere, vrTransform, "rotate", "rotate")
	copyProperty(sphere, vrTransform, "scale", "scale")

	copyProperty(polySphere, vr_light, 'radius', 'radius')
	subdivision = int(math.modf(getProperty(vr_light, 'sphereSegments'))[1])
	setProperty(polySphere, 'subdivisionsAxis', subdivision)
	setProperty(polySphere, 'subdivisionsHeight', subdivision)
	
	# Logging to file
	end_log(vr_light) 



def convertVRayLightMeshLightLinking(vr_light): 

	# Redshift light transform
	splited_name = vr_light.split("|")
	vrTransform = "|".join(splited_name[0:-1])
	group = "|".join(splited_name[0:-2])

	if cmds.objExists(vrTransform + "_rpr"):
		rprTransform = vrTransform + "_rpr"
		rprLightShape = cmds.listRelatives(rprTransform)[0]
	else: 
		rprLightShape = cmds.createNode("RPRPhysicalLight", n="RPRPhysicalLightShape")
		rprLightShape = cmds.rename(rprLightShape, splited_name[-1] + "_rpr")
		rprTransform = cmds.listRelatives(rprLightShape, p=True)[0]
		rprTransform = cmds.rename(rprTransform, splited_name[-2] + "_rpr")
		rprLightShape = cmds.listRelatives(rprTransform)[0]

		if group:
			cmds.parent(rprTransform, group)

		rprTransform = group + "|" + rprTransform
		rprLightShape = rprTransform + "|" + rprLightShape

	# Logging to file 
	start_log(vr_light, rprLightShape)

	# Copy properties from vrLight
	lightlink_transform = cmds.listRelatives(vr_light, p=True)[0]
	vr_light = cmds.listConnections(lightlink_transform, type="VRayLightMesh")[0]

	light_units = getProperty(vr_light, 'units')
	if light_units in (0, 1, 4):
		setProperty(rprLightShape, 'intensityUnits', 1)
		copyProperty(rprLightShape, vr_light, 'lightIntensity', 'intensityMult')
	elif light_units == 2:
		setProperty(rprLightShape, 'intensityUnits', 1)
		setProperty(rprLightShape, 'lightIntensity', getProperty(vr_light, 'intensityMult') / 1000)
	elif light_units == 3:
		setProperty(rprLightShape, 'intensityUnits', 2)
		copyProperty(rprLightShape, vr_light, 'lightIntensity', 'intensityMult')

	copyProperty(rprLightShape, vr_light, 'colorMode', 'colorMode')
	if getProperty(vr_light, 'colorMode') == 1:
		mel.eval("onTemperatureChanged(\"{}\")".format(rprLightShape))

	copyProperty(rprLightShape, vr_light, 'temperature', 'temperature')
	copyProperty(rprLightShape, vr_light, 'colorPicker', 'lightColor')

	if getProperty(vr_light, 'invisible'):
		setProperty(rprLightShape, 'areaLightVisible', 0)
	else:
		setProperty(rprLightShape, 'areaLightVisible', 1)

	setProperty(rprLightShape, 'areaLightShape', 4)
	mesh_obj = cmds.listConnections(vr_light, type='transform')

	try:
		cmds.select(clear=True)
		setProperty(rprLightShape, "areaLightSelectingMesh", 1)
		cmds.select(mesh_obj)
	except Exception as ex:
		traceback.print_exc()
		print("Failed to attach mesh to rpr physical light")

	if getProperty(vr_light, 'useTex'):
		tex_mult = cmds.shadingNode("RPRArithmetic", asUtility=True)
		setProperty(tex_mult, 'operation', 2)
		copyProperty(tex_mult, vr_light, 'inputA', 'tex')
		copyProperty(tex_mult, vr_light, 'inputB', 'texA')
		connectProperty(tex_mult, 'out', rprLightShape, 'colorPicker')
	
	# Logging to file
	end_log(vr_light) 


def convertTemperature(temperature):
	temperature = temperature / 100

	if temperature <= 66:
		colorR = 255
	else:
		colorR = temperature - 60
		colorR = 329.698727446 * colorR ** -0.1332047592
		if colorR < 0:
			colorR = 0
		if colorR > 255:
			colorR = 255


	if temperature <= 66:
		colorG = temperature
		colorG = 99.4708025861 * math.log(colorG) - 161.1195681661
		if colorG < 0:
			colorG = 0
		if colorG > 255:
			colorG = 255
	else:
		colorG = temperature - 60
		colorG = 288.1221695283 * colorG ** -0.0755148492
		if colorG < 0:
			colorG = 0
		if colorG > 255:
			colorG = 255


	if temperature >= 66:
		colorB = 255
	elif temperature <= 19:
		colorB = 0
	else:
		colorB = temperature - 10
		colorB = 138.5177312231 * math.log(colorB) - 305.0447927307
		if colorB < 0:
			colorB = 0
		if colorB > 255:
			colorB = 255

	colorR = colorR / 255
	colorG = colorG / 255
	colorB = colorB / 255

	return (colorR, colorG, colorB)



# Convert material. Returns new material name.
def convertMaterial(material, source):

	material_type = cmds.objectType(material)

	conversion_func = {

		# VRay materials
		"VRayMtl": convertVRayMtl,
		"VRayBumpMtl": convertVRayBumpMtl,
		"VRayCarPaintMtl": convertVRayCarPaintMtl,
		"VRayBlendMtl": convertVRayBlendMtl,
		"VRayLightMtl": convertVRayLightMtl,
		"VRayAlSurface": convertVRayAlSurface,
		"VRayHairNextMtl": convertVRayHairNextMtl,
		"VRayFastSSS2Mtl": convertUnsupportedMaterial,
		"VRayFlakesMtl": convertUnsupportedMaterial,
		"VRayMeshMaterial": convertUnsupportedMaterial,
		"VRayMtl2Sided": convertUnsupportedMaterial,
		"VRayMtlGLSL": convertUnsupportedMaterial,
		"VRayHair3Mtl": convertUnsupportedMaterial,
		"VRayMtlMDL": convertUnsupportedMaterial,
		"VRayMtlOSL": convertUnsupportedMaterial,
		"VRayMtlRenderStats": convertUnsupportedMaterial,
		"VRayMtlWrapper": convertUnsupportedMaterial,
		"VRayPointParticleMtl": convertUnsupportedMaterial,
		"VRayScannedMtl": convertUnsupportedMaterial,
		"VRayStochasticFlakesMtl": convertUnsupportedMaterial,
		"VRaySwitchMtl": convertUnsupportedMaterial,
		"VRayToonMtl": convertUnsupportedMaterial,
		"VRayVRmatMtl": convertUnsupportedMaterial,

		# VRay Volumetric
		"VRayAerialPerspective": convertUnsupportedMaterial,
		"VRayEnvironmentFog": convertUnsupportedMaterial,
		"VRayScatterFog": convertUnsupportedMaterial,
		"VRaySimpleFog": convertUnsupportedMaterial,
		"VRaySphereFadeVolume": convertUnsupportedMaterial,

		# Standard utilities
		"clamp": convertUnsupportedNode,
		"colorCondition": convertUnsupportedNode,
		"colorComposite": convertColorComposite,
		"blendColors": convertBlendColors,
		"luminance": convertLuminance,
		"reverse": convertReverse,
		"premultiply": convertPreMultiply,
		"channels": convertChannels,
		"vectorProduct": convertVectorProduct,
		"multiplyDivide": convertmultiplyDivide,
		"bump2d": convertbump2d,

		# VRay utilities
		"VRayTemperature": convertVRayTemperature,
		"VRayFresnel": convertVRayFresnel

	}

	if material_type in conversion_func:
		rpr = conversion_func[material_type](material, source)
	else:
		if isVRayType(material):
			rpr = convertUnsupportedNode(material, source)
		else:
			rpr = convertStandardNode(material, source)

	return rpr


# Convert light. Returns new light name.
def convertLight(light):

	light_type = cmds.objectType(light)

	conversion_func = {

		# VRay lights

		"VRayLightDomeShape": convertVRayLightDomeShape,
		"VRayLightRectShape": convertVRayLightRectShape,
		#"VRaySunShape": convertVRaySunShape,
		#"VRaySky": convertVRaySky,
		"VRayLightSphereShape": convertVRayLightSphereShape,
		"VRayLightMeshLightLinking": convertVRayLightMeshLightLinking,
		"VRayLightIESShape": convertVRayLightIESShape,

	}

	conversion_func[light_type](light)


def isVRayType(obj):

	if cmds.objExists(obj):
		objType = cmds.objectType(obj)
		if "VRay" in objType:
			return 1
	return 0


def cleanScene():

	listMaterials = cmds.ls(materials=True)
	for material in listMaterials:
		if isVRayType(material):
			shEng = cmds.listConnections(material, type="shadingEngine")
			try:
				cmds.delete(shEng[0])
				cmds.delete(material)
			except Exception as ex:
				traceback.print_exc()

	listLights = cmds.ls(l=True, type=["VRayLightRectShape", "VRayLightDomeShape", "VRaySunShape", "VRaySky", "VRaySunTarget", "VRayLightSphereShape", \
		"VRayLightMeshLightLinking", "VRayLightMesh", "VRayLightIESShape"])
	for light in listLights:
		transform = cmds.listRelatives(light, p=True)
		try:
			light_type = cmds.objectType(light) 
			cmds.delete(light)
			if light_type != "VRayLightMesh":
				cmds.delete(transform[0])
		except Exception as ex:
			traceback.print_exc()

	listObjects = cmds.ls(l=True)
	for obj in listObjects:
		if isVRayType(object):
			try:
				cmds.delete(obj)
			except Exception as ex:
				traceback.print_exc()


def remap_value(value, maxInput, minInput, maxOutput, minOutput):

	value = maxInput if value > maxInput else value
	value = minInput if value < minInput else value

	inputDiff = maxInput - minInput
	outputDiff = maxOutput - minOutput

	remapped_value = minOutput + ((float(value - minInput) / float(inputDiff)) * outputDiff)

	return remapped_value


def clampValue(value, minValue, maxValue):
	return max(min(value, maxValue), minValue)


def checkAssign(material):

	if isVRayType(material):
		materialSG = cmds.listConnections(material, type="shadingEngine")
		if materialSG:
			cmds.hyperShade(objects=material)
			assigned = cmds.ls(sl=True)
			if assigned:
				return 1
	return 0


def defaultEnable(RPRmaterial, VRmaterial, enable, weight, color):

	if (getProperty(VRmaterial, color) == (0, 0, 0) or getProperty(VRmaterial, weight) == 0) and mapDoesNotExist(VRmaterial, color):
		setProperty(RPRmaterial, enable, 0)
	else:
		setProperty(RPRmaterial, enable, 1)


def repathScene():
	scene_workspace = cmds.workspace(q=True, dir=True)
	print('Your workspace located in {}'.format(scene_workspace))
	unresolved_files = cmds.filePathEditor(query=True, listFiles="", unresolved=True, attributeOnly=True)
	if unresolved_files:
		for item in unresolved_files:
			print("Repathing node {}".format(item, os.path.join(item, scene_workspace)))
			cmds.filePathEditor(item, repath=scene_workspace, recursive=True, ra=1)


def convertScene():

	# Repath paths in scene files (filePathEditor)
	repathScene()

	# Check plugins
	if not cmds.pluginInfo("vrayformaya", q=True, loaded=True):
		try:
			cmds.loadPlugin("vrayformaya", quiet=True)
		except Exception as ex:
			response = cmds.confirmDialog(title="Error",
							  message=("V-Ray plugin is not installed.\nInstall V-Ray plugin before conversion."),
							  button=["OK"],
							  defaultButton="OK",
							  cancelButton="OK",
							  dismissString="OK")
			exit("V-Ray plugin is not installed")

	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		try:
			cmds.loadPlugin("RadeonProRender", quiet=True)
		except Exception as ex:
			response = cmds.confirmDialog(title="Error",
							  message=("RadeonProRender plugin is not installed.\nInstall RadeonProRender plugin before conversion."),
							  button=["OK"],
							  defaultButton="OK",
							  cancelButton="OK",
							  dismissString="OK")
			exit("RadeonProRender plugin is not installed")

	# Vray engine set before conversion
	setProperty("defaultRenderGlobals","currentRenderer", "vray")

	# TODO Convert Vray Environment

	'''
	env = cmds.ls(type="VrayEnvironment")
	if env:
		try:
			convertVrayEnvironment(env[0])
		except Exception as ex:
			traceback.print_exc()
			print("Error while converting environment. ")
	'''

	# TODO Convert Vray PhysicalSky

	'''
	sky = cmds.ls(type="VrayPhysicalSky")
	if sky:
		try:
			convertVrayPhysicalSky(sky[0])
		except Exception as ex:
			traceback.print_exc()
			print("Error while converting physical sky. \n")
	'''

	# Get all lights from scene
	listLights = cmds.ls(l=True, type=["VRayLightRectShape", "VRayLightDomeShape", "VRaySunShape", "VRaySky", "VRayLightSphereShape", \
		"VRayLightMeshLightLinking", "VRayLightIESShape", "areaLight", "spotLight", "pointLight", "directionalLight"])

	# Convert lights
	for light in listLights:
		try:
			convertLight(light)
		except Exception as ex:
			traceback.print_exc()
			print("Error while converting {} light. \n".format(light))
		
	# Get all materials from scene
	listMaterials = cmds.ls(materials=True)
	materialsDict = {}
	for each in listMaterials:
		if checkAssign(each):
			materialsDict[each] = convertMaterial(each, "")

	for vr, rpr in materialsDict.items():
		try:
			cmds.hyperShade(objects=vr)
			rpr_sg = cmds.listConnections(rpr, type="shadingEngine")[0]
			cmds.sets(forceElement=rpr_sg)
		except Exception as ex:
			traceback.print_exc()
			print("Error while converting {} material. \n".format(vr))
	
	# globals conversion
	try:
		setProperty("defaultRenderGlobals","currentRenderer", "FireRender")
		setProperty("defaultRenderGlobals", "imageFormat", 8)

		# TODO iterations conversion

		# TODO check this
		setProperty("RadeonProRenderGlobals", "giClampIrradiance", 1)
		setProperty("RadeonProRenderGlobals", "giClampIrradianceValue", 5)
		setProperty("RadeonProRenderGlobals", "raycastEpsilon", 0.001)
		if MAX_RAY_DEPTH:
			setProperty("RadeonProRenderGlobals", "maxRayDepth", MAX_RAY_DEPTH)

		
		# TODO render settings conversion

	except:
		pass


def auto_launch():
	convertScene()
	cleanScene()

def manual_launch():
	print("Convertion start!")
	startTime = 0
	testTime = 0
	startTime = time.time()
	convertScene()
	testTime = time.time() - startTime
	print("Convertion finished! Time: " + str(testTime))

	response = cmds.confirmDialog(title="Convertation finished",
							  message=("Total time: " + str(testTime) + "\nDelete all V-Ray instances?"),
							  button=["Yes", "No"],
							  defaultButton="Yes",
							  cancelButton="No",
							  dismissString="No")

	if response == "Yes":
		cleanScene()


def onMayaDroppedPythonFile(empty):
	manual_launch()

if __name__ == "__main__":
	manual_launch()



