#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#__author__ == Tr3jer_CongRong

import time
import socket
import MySQLdb
import dns.resolver

def port(domain,*port):
	port_result = []
	for i in port:
		s = socket.socket()
		s.settimeout(0.5)
		try:
			if s.connect_ex((domain, i)) == 0:
				port_result.append(i)
				s.close()
		except:
			pass
	return port_result

def host(domain):
	result = []
	myResolver = dns.resolver.Resolver()
	myResolver.lifetime = myResolver.timeout = 2.0
	myResolver.nameservers = [
                '114.114.114.114',
                '119.29.29.29',
                '223.5.5.5',
                '8.8.8.8',
                '182.254.116.116',
                '223.6.6.6',
                '8.8.4.4',
                '180.76.76.76',
                '216.146.35.35',
                '123.125.81.6',
                '218.30.118.6']
	try:
		record = myResolver.query(domain)
		for i in record:
			result.append(i.address)
	except:
		pass

	return result


class domain_db(object):

	def __init__(self,dbname):
		self.dbname = dbname

	def __init_connect__(self):
		self.conn = MySQLdb.connect(
			host='localhost',
			user='root',
			passwd='root',
			db=self.dbname,
			port=3306,
		)
		self.cur = self.conn.cursor()

	def install(self,newdbname):
		install_errorflag = True

		create_dbsql = "CREATE DATABASE " + newdbname
		try:
			self.cur.execute(create_dbsql)
		except:
			install_errorflag = False

		self.dbname = newdbname
		self.__init_connect__()

		create_table = "CREATE TABLE `hooks_record` (`id` bigint(20) NOT NULL AUTO_INCREMENT,`domain` varchar(100) NOT NULL,`ip` text NOT NULL,`port` varchar(100) DEFAULT NULL,`record_time` varchar(30) DEFAULT NULL,`title` varchar(100) DEFAULT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;SET FOREIGN_KEY_CHECKS = 1;"
		try:
			self.cur.execute(create_table)
		except:
			install_errorflag = False

		return install_errorflag


	def run(self):
		sql = "select domain from `hooks_record`"
		result = set()
		try:
			self.cur.execute(sql)

			for i in self.cur.fetchall():
				result.add(i[0])
		except:
			pass

		return result

	def insert(self,domain,ip,port,title):
		record_time = time.strftime("%Y%m%d %X", time.localtime())
		sql = "insert into `hooks_record` (`domain`, `ip`, `port`,`record_time`,`title`) VALUES ('{}','{}','{}','{}','{}')".format(domain,ip,port,record_time,title)
		try:
			self.cur.execute(sql)
			self.conn.commit()
			print '\033[15;32m[+] new insert {}\033[0m'.format(domain)

		except Exception,e:
			print e
			pass
