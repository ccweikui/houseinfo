# -*- coding=utf8 -*-

class House:
	def __init__(self):
		#房源在系统中的id
		self.houseId = 0
		#地址
		self.address = ""
		#单价
		self.price = ""
		#面积
		self.area = ""
		#经度
		self.longitude = 0
		#纬度
		self.latitude = 0
		#谷歌经度
		self.glongitude = 0
		#谷歌纬度
		self.glatitude = 0
		#是否已经存在
		#0 表示不存在,1表示存在
		self.flage = 0
