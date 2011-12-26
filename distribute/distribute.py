#!/usr/bin/env python

import sys
import os
import subprocess
import errno
import imp
from optparse import OptionParser

import func.overlord.client as fc

def check_module(filename):
	"""
	Execute pyflakes on module on local machine to determine syntax errors. 
	Errors are raised to caller. Func specific errors (e.g. func_module imports) 
	are ignored.
	"""
	try:
		imp.find_module('pyflakes')
	except ImportError, e:
		print("Pyflakes not found. Either install pyflakes or rerun with --no-check")
		sys.exit(1)
	try:
		open(filename) # check if file exists
	except IOError, e:
		if e.errno == errno.ENOENT:
			print('Could not find module')
			sys.exit(1)
		else:
			print("Error opening source file: " + e)
			raise
	print("Running pyflakes on "+filename+':')
	p = subprocess.Popen(['pyflakes', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	if p.returncode == 1:
		if stderr:
			print(stderr)
			print('Could not distibute '+filename)
			sys.exit(1)
		if stdout:
			print(stdout)

def python_version(minion):
	"""Returns the python version of the minion as a string. Pass an fc.Client() instance associated to only one minion"""
	rc,stdout,stderr = minion.command.run('/usr/bin/env python -V')[minion.list_minions()[0]]
	if rc != 0:
		print('Failed to get python version for '+minion.client_names[0])
		return False
	return ''.join(stderr.split(' ')[1][:3])

def restart_func(minion):
	"""Restarts funcd on given minion. Pass an fc.Client() instance associated to only one minion"""
	rc,stdout,stderr = minion.command.run('/sbin/service funcd restart')[minion.list_minions()[0]]
	if rc !=0:
		return False
	if len(stdout.split('OK')) < 3:
		return False
	return True

def distribute(client, modules):
	minions = client.list_minions()
	for i in minions:
		minion = fc.Client(i)
		pyver = python_version(minion)
		if not pyver:
			continue
		for mod in modules:
			if not minion.local.copyfile.send(mod, '/usr/lib/python'+pyver+'/site-packages/func/minion/modules/'+mod):
				print('Failed to distribute '+mod+' to '+minion.list_minions())
		if not restart_func(minion):
			print('Failed to restart funcd on '+minion.list_minions())

if __name__ == "__main__":
	clients = "*"
	usage = "usage: %prog [options] [module(s) absolute path]"
	parser = OptionParser(usage=usage)
	parser.add_option("-m", "--minions", action="store", type="string", dest="minions", help="select minion(s) separated by semicolons (e.g. -m 'kidtoyz.rutgers.edu;mysqltest1.rutgers.edu;eden*')")
	parser.add_option("-g", "--groups", action="store", type="string", dest="groups", help="select group(s) separated by semicolons (e.g. -g 'directors;mysql')")
	parser.add_option("-n", "--no-check", action="store_true", dest="no_check", default=False, help="do not run module through pyflakes before distributing")

	(options, args) = parser.parse_args()
	if options.minions:
		clients = options.minions
	if options.groups:
		if not options.minions:
			clients = ''
		groups = ['@'+i for i in options.groups.split(';')]
		for i in groups:
			clients = clients+';'+i
		clients = clients.strip(';')
		
	if len(args) < 1:
		parser.error("need at least one module to distribute")
		sys.exit(1)
	if not options.no_check:
		for mod in args:
			check_module(mod)

	client = fc.Client(clients)
	distribute(client, args)
