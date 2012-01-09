#!/usr/bin/env python

import time

import func_module

class SyncException(Exception):pass
class SyncShellException(Exception):pass
class SyncOverlordHostsNotFound(Exception):pass

class Sync(func_module.FuncModule):

	from command import Command as cmd

	version = '0.0.1'
	api_version = '0.0.1'
	description = 'Sync files between minions and overlords'

	def check_command(self, rc, stderr, returncode=0):
		"""
		Checks the output of resulting command. If rc of the output of the command does not match the
		returncode, then a StatShellException is raised with error code as the return code
		"""
		if rc != returncode:
			raise SyncShellException('errorcode(%s): %s' % (rc, stderr,))

	def comm(self, file1, file2, options=''):
		"""
		Runs the comm command on the two files with the given options
		"""
		return self.cmd().run("/usr/bin/comm "+options+' '+file1+' '+file2)

	def difference(self, file1, file2):
		"""
		Calls comm on the two files and figures out which entries in file2 are not in file1.
		Returns a list of lines to add to file1 for file1 to look more like file2.
		Takes care of similar lines in different places in both files.
		"""
		rc,stdout,stderr = self.comm(file1, file2, '-3')
		self.check_command(rc,stderr)
		stdout  = [r for r in stdout.strip().split('\n') if r]
		unique1 = [x for x in stdout if x[0] != '\t' and x[0] != '#']
		unique2 = [y for y in stdout if y[0] == '\t' and len(y) > 1] #filter out blank lines
		unique2 = [j.strip('\t') for j in unique2 if j[1] != '#'] #filter out comments
		unique2 = [i for i in unique2 if i.find('127.0.0.1') == -1] #filter out localhost

		#take out duplicate entries
		for i in unique1:
			try:
				unique2.remove(i)	
			except ValueError:
				continue
		
		return unique2
		
	def sync_hosts(self):
		"""
		Compares /etc/hosts and /etc/hosts.overlord and adds new entries from /etc/hosts.overlord to its own hosts file.
		sync_hosts then returns entries in /etc/hosts not found int /etc/hosts.overlord to the caller.
		The overlord must transmit their host file to /etc/hosts.overlord before calling this method.
		If hosts.overlord is not found, sync_hosts raises SyncOverlordHostsNotFound exception. 
		"""
		try:
			hosts_overlord = open('/etc/hosts.overlord','r+')
		except IOError:
			raise SyncOverlordHostsNotFound('Could not find /etc/hosts.overlord file')
		
		entries = self.difference('/etc/hosts', '/etc/hosts.overlord')
		
		try:
			hosts_minion = open('/etc/hosts', 'a')
		except IOError:
			#/etc/hosts/ not found, create one
			hosts_minion = open('/etc/hosts', 'w+')

		hosts_minion.write('\n#Func added on '+time.strftime("%a %b %d %Y %I:%M%p")+'\n')
		for line in entries:
			hosts_minion.write(line+'\n')
	
		# now we check if we have some entries from in /etc/hosts not in /etc/host.overlord and return them
		return self.difference('/etc/hosts.overlord', '/etc/hosts')
