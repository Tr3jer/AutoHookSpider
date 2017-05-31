#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#__author__ == Tr3jer_CongRong

import requests
import urlparse
import hashlib
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import time
import Queue
import random
import optparse
import threading
from bs4 import BeautifulSoup
import bs4

from lib.common import port,host,domain_db

class autoHookSpider:
	def __init__(self,options):
		self.STOP_ME = False
		self.q = Queue.Queue()
		self.url_hashs = []
		self.lock = threading.Lock()
		self.entrances,self.hooks = [],[]
		domain_do = domain_db(options.dbname)
		if options.install == "Y":
			domain_do.dbname = ""
			domain_do.__init_connect__()

			if not domain_do.install(newdbname=options.dbname):
				print "[+] Install failed, You have installed successfully."
			else:
				print "[+] Install AutoHookSpider Successfull."
		domain_do.__init_connect__()

		self.domain_db = domain_do.run()
		self.thread_cnt = options.thread_cnt
		self.hooks = [i.strip() for i in open(options.hookfile)]
		self.header = {
					"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
				}
		self.mime = ['text/css', 'text/html', 'text/plain', 'text/mathml', 'application/rss+xml','application/atom+xml', 'application/x-javascript']

	def req(self):
		while not self.q.empty() and self.STOP_ME == False:
			try:
				r = requests.get(self.q.get(),headers=self.header,timeout=2)

				if max(map(lambda x:r.headers['Content-Type'].find(x),self.mime)) < 0:
					continue

				print '[{}] {}'.format(r.status_code,r.url)

				tags = BeautifulSoup(r.content,"lxml")

				for tag in tags.find_all('a'):
					try:

						if True in map(lambda x: x == tag['href'][:5], ['http:', 'https']):
							targetTmp = tag['href'].split('/')[2]

							if targetTmp.find(':') != -1:
								targetTmp = targetTmp[:targetTmp.find(':')]

							for i in self.hooks:
								if targetTmp[-len(i):] == i:

									# clear repeat urls
									f,h = self.clear_repeat(tag['href'])
									if not f:
										self.q.put(tag['href'])
										self.lock.acquire()
										self.url_hashs.append(h)
										self.lock.release()

									try:
										self.lock.acquire()
										if targetTmp not in self.domain_db and targetTmp[-len(i)-1:] == '.'+i and len(targetTmp) > len(i)+1:
											hostTmp = host(targetTmp)
											if hostTmp:
												portTmp = ','.join([str(i) for i in port(targetTmp, 80,443,81,82,7001,8080,8081,8088,9081,9080,27017,8069,9200,11211)])
												if not portTmp:
													portTmp = ''
												try:
													self.domain_db.add(targetTmp)
													title = self.get_title(tag['href'])
													domain_do = domain_db(options.dbname)
													domain_do.__init_connect__()
													domain_do.insert(targetTmp,','.join(hostTmp),portTmp,title)

												except:
													pass
									except:
										pass
									finally:
										self.lock.release()
										break
					except:
						pass
			except:
				pass

	def clear_repeat(self, url):
		uri = urlparse.urlparse(url)

		sq = ""
		for match in re.finditer(r"((\A|[?&])(?P<parameter>[^_]\w*)=)(?P<value>[^&#]+)", url):
			sq = sq + match.group(1)

		order = uri.netloc + uri.path + sq
		hash = hashlib.md5(order).hexdigest()

		if hash in self.url_hashs:
			return True, ""
		else:
			return False, hash

	def get_title(self, url):

		try:
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2146.0 Safari/537.36',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				'Referer': url,
			}
			title_url =  url.split('/')[0] + "//" +url.split('/')[2]

			r = requests.get(url=title_url, headers=headers, timeout=3, verify=False, allow_redirects=True)

			html = bs4.BeautifulSoup(r.text.encode(str(r.encoding)), 'html.parser')

			print "[+] %s %s " % (url, html.title.text)
			return html.title.text

		except Exception, e:
			return ""

	def reSelect(self, domain):
		newdomain = random.sample(self.hooks, 1)[0]
		try:
			if port(newdomain, 80):
				self.entrances[self.entrances.index(domain)] = newdomain
				self.q.put('http://{}'.format(newdomain))
			else:
				self.reSelect(domain)
		except:
			self.reSelect(domain)

	def run(self,*args):
		if args:
			self.entrances = args[0].split(',')
			for i in self.entrances:
				self.q.put('http://{}'.format(i))
		else:
			print '[+] Choose Entrances Domain ing ...'
			if len(self.hooks) < self.thread_cnt:
				self.thread_cnt = len(self.hooks)

			self.entrances = random.sample(self.hooks,self.thread_cnt)
			for i in self.entrances:
				if not port(i,80):
					self.reSelect(i)
				else:
					self.q.put('http://{}'.format(i))

		print "[+] Use : {}".format('、'.join(self.entrances))

		for t in xrange(self.thread_cnt):
			t = threading.Thread(target=self.req)
			t.setDaemon(True)
			t.start()
			# t.join()

		while True:
			if threading.activeCount() <= 1:
				break
			else:
				try:
					time.sleep(1.5)

				except KeyboardInterrupt:
					self.STOP_ME = True

if __name__ == '__main__':
	intro = '''
		 ____          _____    _____ _
		| __ ) _   _  |_   _| _____ /(_) ___ _ __
		|  _ \| | | |   | || '__||_ \| |/ _ \ '__|
		| |_) | |_| |   | || |  ___) | |  __/ |
		|____/ \__, |   |_||_| |____// |\___|_|
		       |___/               |__/

	+ --=|                                               |
	+ --=|          AutoHookSpider From PyArms           |
	+ --=|                                               |
	+ --=|           Coded By CongRong(@Tr3jer)          |
	+ --=|           https://www.Thinkings.org/          |
	+ --=|                                               |
	    	     	'''
	print intro
	parser = optparse.OptionParser('usage: python main.py {Options} [ google.com,twitter.com,facebook.com | -t 20 ]')
	parser.add_option('-t', '--Thread', dest='thread_cnt', help='Num Of Scan Threads , 20 By Default', default=20,type=int, metavar='20')
	parser.add_option('-f', '--hookfile', dest='hookfile', help='choose your hooks file', default="hooks.txt")
	parser.add_option('-d', '--dbname', dest='dbname', help='choose your database for Record Log ,default: AutoHookSpider', default="AutoHookSpider")
	parser.add_option('-i', '--install', dest='install', help='install database and table.', default="N")

	(options, args) = parser.parse_args()

	if len(args) >= 1:
		mainRun = autoHookSpider(options)
		mainRun.run(args[0])
	else:
		mainRun = autoHookSpider(options)
		mainRun.run()
