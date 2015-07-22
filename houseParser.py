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
	对RootUrl页面进行爬取处理
	
	"""
	def __init__(self):
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
		request = urllib2.Request(RootUrl+str(pageCount))
		content = urllib2.urlopen(request).read()
		originContent = content.decode('gb2312','ignore').encode('utf-8')
		
		#寻找content中所有的列信息
		soup = BeautifulSoup(originContent)
		body = soup.body
		
		houseList = body.find('div',id='searchmain_c_1').find_all('div',attrs={"class": "inventory_list_house inventory_out _houselist"})

		for houseStr in houseList:
			self.processHouse(houseStr)
		#每页数据获取后进行存储
		self.saveToFile()
		self.houses = []
	
	def processHouse(self,houseStr):
		"""
		对每个学区房记录进行处理
		"""
		houseInfo = houseStr.find('div',attrs={"class": "inventory_list_r_tit_list"}).find_all('a')
		houseId = houseInfo[0]['href'][len(PrefixURL):][:-1]
		address = houseStr.find('div',attrs={"class": "inventory_list_r_name_ad"}).text
		detailInfo = houseStr.find('div',attrs={"class": "inventory_list_r_details_r"})
		details = detailInfo.find_all('span')
		price = details[2].text
		area = details[1].text
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
		self.book.save('houseInfo_origin_'+self.timestamp+'.xls')

if __name__ == '__main__':
	houseParser = HouseParser()
	for pageCount in range(TotalPage):
		print "第%d页\n" % (pageCount + 1)
		houseParser.getHouseList(pageCount+1)
		time.sleep(PagePerTime)
