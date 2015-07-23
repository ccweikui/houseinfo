# -*- coding=utf8 -*-
import sys
import urllib2
import time
import datetime
import json

from bs4 import BeautifulSoup
import xlwt
import xlrd

from config import *
from house import House

class AddressShift:
	"""
	将地址转换成百度坐标
	"""
	def __init__(self):
		#正确处理的houseId的列表
		self.success_houseIds = {}
		#未能正确处理的houseId的列表
		self.fail_houseIds = {}
		#存储每页学区房列表信息
		self.houses = []
		# 最后存储的Excel文件
		self.book = xlwt.Workbook(encoding='utf-8')
		self.worksheet = self.book.add_sheet('houseinfo')
		self.writeExcelHead()
		# Excel文件中的索引位置
		self.excelIndex = 0
		#此次处理的时间戳
		self.timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))

	def getHouseList(self):
		"""
		从文件中获取房屋信息列表
		"""
		data = xlrd.open_workbook('houseInfo_origin.xls')
		table = data.sheet_by_name(u'houseinfo')
		for index in range(1,table.nrows):
			houseId = table.cell(index,0).value
			address = table.cell(index,1).value
			area = table.cell(index,2).value
			price = table.cell(index,3).value
		
			house = House()
			house.houseId = houseId
			house.address = address
			house.price = price
			house.area = area
			self.houses.append(house)

			if (index % PageNumber == 0):
				self.processHouses()
				self.saveToFile()
				self.excelIndex += len(self.houses)
				self.houses = []
		if (len(self.houses) != 0):
			self.processHouses()
			self.saveToFile()
			self.houses = []

	def processHouses(self):
		"""
		对学区房列表进行处理
		"""
		for house in self.houses:
			address = house.address
			longitude,latitude = self.processLocation(address)
			if longitude != 0:
				house.longitude = longitude
				house.latitude = latitude
	
	def processLocation(self,address):
		"""
		使用地理位置获取经纬度信息
		"""
		requestUrl = GeoCoding + address.encode('utf-8')
		content = self.sendRequest(requestUrl)
		originContent = content.decode('gb2312','ignore').encode('utf-8')
		originContent = json.loads(originContent)
		print originContent
		if ('status' in originContent):
			status = originContent['status']
			if (status == 0):
				longitude = originContent['result']['location']['lng']
				latitude = originContent['result']['location']['lat']
			else:
				longitude = Longitute 
				latitude = Latitude
		else:
			longitude = Longitute 
			latitude = Latitude
		return (longitude,latitude)

	def sendRequest(self,requestUrl):
		"""
		使用百度地图接口获取经纬度信息
		发送请求并处理超时情况
		"""
		print requestUrl
		count = 0
		timeOut = True
		content = "{}"
		while (count < RetryCount and timeOut):
			count += 1
			print count
			try:
				request = urllib2.Request(requestUrl)
				content = urllib2.urlopen(request,timeout=10).read()
				timeOut = False
			except urllib2.URLError, e:  
				print e
			except Exception ,e:
				print e
			if timeOut:
				time.sleep(2 * count)
		return content

	def writeExcelHead(self):
		"""
		定义Excel表的表头
		"""
		self.worksheet.write(0, 0, label = '编号')
		self.worksheet.write(0, 1, label = '地址')
		self.worksheet.write(0, 2, label = '每套面积')
		self.worksheet.write(0, 3, label = '单价')
		self.worksheet.write(0, 4, label = '百度经度')
		self.worksheet.write(0, 5, label = '百度纬度')

	def saveToFile(self):
		"""
		保存到指定的文件中 
		"""
		for index,house in enumerate(self.houses):
			actualIndex = index + self.excelIndex
			self.worksheet.write(actualIndex+1, 0, label = house.houseId)
			self.worksheet.write(actualIndex+1, 1, label = house.address)
			self.worksheet.write(actualIndex+1, 2, label = house.area)
			self.worksheet.write(actualIndex+1, 3, label = house.price)
			self.worksheet.write(actualIndex+1, 4, label = house.longitude)
			self.worksheet.write(actualIndex+1, 5, label = house.latitude)
		#self.book.save('houseInfo_address_' + self.timestamp + '.xls')
		self.book.save('houseInfo_address.xls')

if __name__ == '__main__':
	addressShift = AddressShift()
	addressShift.getHouseList()
