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

class BaiduToGoogle:
	"""
	将百度坐标转换成谷歌坐标
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

	def getHouseList(self):
		"""
		从文件中获取房屋信息列表
		"""
		data = xlrd.open_workbook('houseInfo_address.xls')
		table = data.sheet_by_name(u'houseinfo')
		for index in range(1,table.nrows):
			houseId = table.cell(index,0).value
			address = table.cell(index,1).value
			area = table.cell(index,2).value
			price = table.cell(index,3).value
			longitude = table.cell(index,4).value
			latitude = table.cell(index,5).value
		
			house = House()
			house.houseId = houseId
			house.address = address
			house.price = price
			house.area = area
			house.longitude = longitude
			house.latitude = latitude
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
			longitude = house.longitude
			latitude = house.latitude
			glongitude,glatitude = self.toGoogle(longitude,latitude)
			if glongitude != 0:
				house.glongitude = glongitude
				house.glatitude = glatitude
	
	def toGoogle(self,longitude,latitude):
		"""
		使用地址服务将百度坐标转换成Google坐标
		"""
		requestUrl = DecodeUrl + "lng=" + str(longitude) + "&lat=" + str(latitude)
		content = self.sendRequest(requestUrl)
		originContent = content.decode('gb2312','ignore').encode('utf-8')
		originContent = json.loads(originContent)
		
		print originContent
		if ('State' in originContent):
			status = originContent['State']
			if (status):
				longitude = originContent['Lng']
				latitude = originContent['Lat']
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
		self.worksheet.write(0, 6, label = '谷歌经度')
		self.worksheet.write(0, 7, label = '谷歌纬度')

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
			self.worksheet.write(actualIndex+1, 6, label = house.glongitude)
			self.worksheet.write(actualIndex+1, 7, label = house.glatitude)
		self.book.save('houseInfo_google.xls')

if __name__ == '__main__':
	baiduToGoogle = BaiduToGoogle()
	baiduToGoogle.getHouseList()
