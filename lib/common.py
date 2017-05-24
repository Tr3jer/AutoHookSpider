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
	def __init__(self):
		self.conn = MySQLdb.connect(
			host='localhost',
			user='root',
			passwd='root',
			db='record',
			port=3306,
			unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock'
		)
		self.cur = self.conn.cursor()

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

	def insert(self,domain,ip,port):
		record_time = time.strftime("%Y%m%d %X", time.localtime())
		sql = "insert into `hooks_record` (`domain`, `ip`, `port`,`record_time`) VALUES ('{}','{}','{}','{}')".format(domain,ip,port,record_time)
		try:
			self.cur.execute(sql)
			self.conn.commit()
			print '\033[15;32m[+] new insert {}\033[0m'.format(domain)

		except:
			pass