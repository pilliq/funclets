#!/usr/bin/env python

import func.overlord.client as fc
import func.jobthing as jobthing
import sys

from time import sleep
from optparse import OptionParser

short_order = ['uptime','load','mem','num_users','num_process','num_files','mem','df']
long_order = ['uptime','load','mem','users','last','num_process','num_files','top_process','top_mem','iostat','nfsstat','df']

def job_failed(minion):
	print("<<< "+minion.list_minions()[0]+" >>>")
	print("Stat Failed\n")
	
def print_df(df, short):
	print('%-26s%-12s%-12s%-12s%-6s%-15s' % (' Filesystem', '1K-blocks', 'Used', 'Available', 'Use%', 'Mounted'))
	for i in df.keys():
		if short:
			if df[i]['fstype'] != 'nfs':
				print('%-26s%-12s%-12s%-12s%-6s%-15s' % (' '+str(df[i]['device']), str(df[i]['total']), str(df[i]['used']), str(df[i]['available']), str(df[i]['percentage']), str(i)))   
		else:
			print('%-26s%-12s%-12s%-12s%-6s%-15s' % (' '+str(df[i]['device']), str(df[i]['total']), str(df[i]['used']), str(df[i]['available']), str(df[i]['percentage']), str(i)))   

def print_short(minion, results):
	name = minion.list_minions()[0]
	results = results[name]
	print("<<< "+name+" >>>")
	uptime = results['uptime']
	print('Uptime: '+uptime['days']+' days '+uptime['hours']+' hours '+uptime['minutes']+' minutes')
	load = results['load']
	print('Load: '+load['1']+' '+load['5']+' '+load['15'])
	print('Users: '+results['num_users'])
	process = results['num_process']
	print('Processes: '+process['processes']+' ('+process['forks']+' forks)')
	print('Files:')
	print(' open: '+str(results['num_files']['open'])+'  allocated: '+str(results['num_files']['allocated'])+'  max: '+str(results['num_files']['max']))
	mem = results['mem']
	print('Memory:')
	print('%-14s %9s' % (' Memtotal:',mem['MemTotal']+' kB',))
	print(' MemTotal:     '+mem['MemTotal']+' kB\n'+' MemFree:      '+mem['MemFree']+' kB\n'.rjust(5)+' Buffers:      '+mem['Buffers']+' kB\n'+' Cached:       '+mem['Cached']+' kB\n'+' SwapCached:   '+mem['SwapCached']+' kB')
	df = results['df']
	print("Disk Usage:")
	print_df(df, 1)

def print_iostat(iostat):
	"""Formats and prints output values from iostat command"""
	if not iostat:
		return None
	print('%-12s%-12s%-12s%-12s%-12s%-12s' % (' Device', 'tps', 'Blk_read/s', 'Blk_wrtn/s', 'Blk_read', 'Blk_wrtn',))
	for dev in iostat:
		print('%-12s%-12s%-12s%-12s%-12s%-12s' % (' '+dev['device'], dev['tps'], dev['blk_read/s'], dev['blk_wrtn/s'], dev['blk_read'], dev['blk_wrtn']))
	print('')
	for entry in iostat:
		break	
	pass
def print_long(minion, results):
	name = minion.list_minions()[0]
	results = results[name]
	print('')
	print("<<< "+name+" >>>")
	uptime = results['uptime']
	print('Uptime: '+uptime['days']+' days '+uptime['hours']+' hours '+uptime['minutes']+' minutes')
	load = results['load']
	print('Load: '+load['1']+' '+load['5']+' '+load['15'])
	users = results['users']
	print("Users:")
	for user in users:
		print(' '+user['user']+'\t'+user['login']+'\t'+user['command'])
	print('')
	print("Last logged in users:")
	for user in results['last']:
		print(' '+user)
	process = results['num_process']
	print('Processes: '+process['processes']+' ('+process['forks']+' forks)\n')
	print('Files:')
	print(' open: '+str(results['num_files']['open'])+'  allocated: '+str(results['num_files']['allocated'])+'  max: '+str(results['num_files']['max'])+'\n')
	print('Top Processes:')
	for line in results['top_process'].split('\n'):
		print(' '+line)
	print('Top Mem:')
	top_mem = [i[2:] for i in results['top_mem']]
	top_mem.reverse()
	for i in top_mem[:5]:
		print(' %-12s%3s' % (i[0],i[1]))
	print('')
	print("IO Status:")
	print_iostat(results['iostat'])
#	print("nfsstat:")
#	for line in results['nfsstat'].split('\n'):
#		print(' '+line)
	print("Disk Usage:")
	print_df(results['df'], 0)
	print('')

def stats(client, short, wait_time):
	minions = client.list_minions()
	jobs = {}
	for i in minions:
		minion = fc.Client(i,async=True)
		if short:
			jobs[minion] = minion.stat.short_stat()
		else:
			jobs[minion] = minion.stat.long_stat()
	while True:
		for minion in jobs.keys():
			(code, results) = minion.job_status(jobs[minion])
			if code == jobthing.JOB_ID_FINISHED:
				if short:
					print_short(minion, results)
				else:
					print_long(minion, results)
				del jobs[minion]
			if code == jobthing.JOB_ID_LOST_IN_SPACE:
				job_failed(minion)
				del jobs[minion]
		if len(jobs) == 0:
			break
		sleep(wait_time)

if __name__ == "__main__":
	clients = '*'
	#to get all clients do func.overlord.client.Client("*").list_minions()
	usage = "usage: %prog [options] minions"
	parser = OptionParser(usage=usage)
	parser.add_option("-m", "--minions", action="store", type="string", dest="minions", help="select minion(s) separated by semicolons (e.g. -m 'kidtoyz.rutgers.edu;mysqltest1.rutgers.edu;eden*')")
	parser.add_option("-g", "--groups", action="store", type="string", dest="groups", help="select group(s) separated by semicolons (e.g. -g 'group;newgr')")
	parser.add_option("-v", "--verbose", action="store_true", dest="long_form", default=False, help="outputs verbose stats")
	parser.add_option("-t", "--wait-time", type="float", action="store", dest="wait_time", default=1, help="specify the time interval to wait when polling a minion for a completed job in seconds, default is 1 second")
	(options, args) = parser.parse_args(args=None, values=None)

	if options.minions:
		clients = options.minions
	if options.groups:
		clients = ''
		groups = options.groups.split(';')
		groups = ['@'+i for i in groups]
		for i in groups:
			clients = clients+';'+i
		clients = clients.strip(';')

	client = fc.Client(clients, async=True)
	if options.long_form:
		stats(client, 0, options.wait_time)
	else:
		stats(client,1, options.wait_time)
