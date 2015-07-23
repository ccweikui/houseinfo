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

class HouseParser:
	"""
	对链家学区房RootUrl页面进行爬取处理
	"""
	def __init__(self):
		#请求的URL地址
		#self.rootUrl = "http://beijing.homelink.com.cn/school/pg"
		#self.rootUrl = "http://bj.lianjia.com/school/pg"
		self.rootUrl = "http://bj.lianjia.com/ershoufang/pg"
		self.suffixUrl = "sc1"
		#self.prefixUrl = "http://beijing.homelink.com.cn/ershoufang/"
		self.prefixUrl = "http://bj.lianjia.com"
		self.prefixText = "/ershoufang/"
		self.totalPage = 1740
		#正确处理的houseId的列表
		self.success_houseIds = {}
		self.houses = []
		# 最后存储的Excel文件
		self.book = xlwt.Workbook(encoding='utf-8')
		self.worksheet = self.book.add_sheet('houseinfo')
		self.writeExcelHead()
		# Excel文件中的索引位置
		self.excelIndex = 0
		#此次处理的时间戳
		self.timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))

	def getHouseList(self,pageCount):
		"""
		获取所有的学期房列表
		"""
		request = urllib2.Request(self.rootUrl+str(pageCount)+self.suffixUrl)
		content = urllib2.urlopen(request).read()
		originContent = content
		
		#寻找content中所有的列信息
		soup = BeautifulSoup(originContent)
		body = soup.body
		
		houseList = body.find_all('div',attrs={"class": "info-panel"})
		for houseStr in houseList:
			try:
				self.processHouse(houseStr)
			except Exception ,e:
				print e
		#每页数据获取后进行存储
		self.saveToFile()
		self.houses = []
	
	def processHouse(self,houseStr):
		"""
		对每个学区房记录进行处理
		"""
		houseInfo = houseStr.find_all('a')
		houseId = houseInfo[0]['href'][len(self.prefixText):][:-5]
		addressUrl = self.prefixUrl + houseInfo[1]['href']
		address = self.processAddress(addressUrl)
		price = (houseStr.find('div',attrs={"class": "price-pre"})).text
		area = (houseStr.find('div',attrs={"class": "where"}).find_all('span'))[3].text
		#如果houseId没被处理过
		if not houseId in self.success_houseIds:
			print houseId,address,price,area
			house = House()
			house.houseId = houseId
			house.address = address
			house.price = price
			house.area = area
			house.flage = 0
			self.houses.append(house)
			self.success_houseIds[houseId] = house
		else:
			print "id:%s  exist" % houseId
			print houseId,address,price,area
			house = self.success_houseIds[houseId]
			if(houseId == house.houseId and address == house.address and price == house.price and area == house.area):
				house.flage = 1
			else:
				house.flage = 2
				print "The same houseId have different data"
			self.houses.append(house)
	
	def processAddress(self,url):
		"""
		获取小区详细的地址
		"""
		request = urllib2.Request(url)
		originContent = urllib2.urlopen(request).read()
		#寻找content中所有的列信息
		soup = BeautifulSoup(originContent)
		body = soup.body
		addressInfo = body.find('div',attrs={"class": "title fl"}).find_all('span')
		#district = addressInfo[0].text
		ad = addressInfo[0].text[1:][:-1]
		xiaoqu = addressInfo[1].text
		return u'北京市' + ad + xiaoqu

	def writeExcelHead(self):
		"""
		定义Excel表的表头
		"""
		self.worksheet.write(0, 0, label = '编号')
		self.worksheet.write(0, 1, label = '地址')
		self.worksheet.write(0, 2, label = '每套面积')
		self.worksheet.write(0, 3, label = '单价')
		self.worksheet.write(0, 4, label = '重复标记')

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
			self.worksheet.write(actualIndex+1, 4, label = house.flage)
		self.excelIndex += len(self.houses)
		#self.book.save('houseInfo_homelink_origin_'+self.timestamp+'.xls')
		self.book.save('houseInfo_homelink_origin.xls')

if __name__ == '__main__':
	houseParser = HouseParser()
	for pageCount in range(houseParser.totalPage):
		print "第%d页" % (pageCount + 1)
		houseParser.getHouseList(pageCount+1)
		time.sleep(HM_PagePerTime)
