#!/usr/bin/python3

class Custom_Exception(Exception):
	
	def __init__(self, data):
		self.data = data

	def __str__(self):
		return self.data