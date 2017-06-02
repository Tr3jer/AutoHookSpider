#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#__author__ == Tr3jer_CongRong

import sys
import time
import Queue
import random
import requests
import optparse
import threading
from bs4 import BeautifulSoup
from lib.common import port,host,domain_db

class autoHookSpider:
	def __init__(self,options):
		self.STOP_ME = False
		self.q = Queue.Queue()
		self.lock = threading.Lock()
		self.entrances,self.hooks = [],[]
		self.domain_db = domain_db().run()
		self.thread_cnt = options.thread_cnt
		self.hooks = [i.strip() for i in open('hooks.txt')]
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
									self.q.put(tag['href'])

									try:
										self.lock.acquire()
										if targetTmp not in self.domain_db and targetTmp[-len(i)-1:] == '.'+i and len(targetTmp) > len(i)+1:
											hostTmp = host(targetTmp)
											if hostTmp:
												portTmp = ','.join([str(i) for i in port(targetTmp, 80,443)])
												if not portTmp:
													portTmp = ''

												try:
													self.domain_db.add(targetTmp)
													domain_db().insert(targetTmp,','.join(hostTmp),portTmp)
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

		while True:
			if threading.activeCount() <= 1:
				break
			else:
				try:
					time.sleep(0.1)
				except KeyboardInterrupt:
					self.STOP_ME = True
					raise


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

	(options, args) = parser.parse_args()

	if len(args) >= 1:
		mainRun = autoHookSpider(options)
		mainRun.run(args[0])
	else:
		rand = raw_input('Random Select Entrances From Hooks.txt?[Y/N]')
		if rand.lower() == 'y':
			mainRun = autoHookSpider(options)
			mainRun.run()
		else:
			parser.print_help()
			sys.exit(0)