# -*- coding: utf-8 -*-
# csv util

def getEscapeCsvCell(val):
	return '"%s"' % val.replace('"', '""')

def getCsvStrFrom2DArray(arr):
	csv = ''
	for line in arr:
		csv += ','.join([getEscapeCsvCell(x) for x in line])
		csv += '\n'
	return csv
