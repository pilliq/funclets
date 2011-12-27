#!/usr/bin/env python

import func_module

#Stat exception Classes
class StatShellException(Exception): pass

class Stat(func_module.FuncModule):

	version = '0.0.1'
	api_version = '0.0.1'
	description = 'Gather information on processes, users, memory/cpu, disk health, filesystem usage, and files'

	from command import Command as cmd
	from disk import DiskModule as disk
	from process import ProcessModule as proc

	def check_command(self, rc, stderr, returncode=0):
		"""Checks the output of resulting command. If rc of the output of the command does not match the
			returncode, then a StatShellException is raised with error code as the return code
		"""
		if rc != returncode:
			raise StatShellException('errorcode(%s): %s' %(rc, stderr,))

	def uptime_users_load(self):
		"""Runs w and parses out the uptime, users, and load average into a dictionary mapping"""
		rc,stdout,stderr = self.cmd().run('/usr/bin/w')
		self.check_command(rc,stderr)

		w_dict = {}
		stdout = [str.split() for str in stdout.split('\n')]
		#grab the uptime
		w_dict['uptime'] = {
			'days': stdout[0][2],
			'hours': stdout[0][4].split(':')[0],
			'minutes': stdout[0][4].split(':')[1].strip(',')
		}
		#grab load averages for 1, 5, and 15 min
		w_dict['load'] = {
				'1': stdout[0][9],
				'5': stdout[0][10],
				'15': stdout[0][11]
		}
		#grab number of users
		w_dict['num_users'] = stdout[0][5]
		#grab users, commands, and login times
		w_dict['users'] = []
		for userout in stdout[2:]:
			if userout:
				w_dict['users'].append({
					'user': userout[0],
					'login': userout[3],
					'command': userout[7]
				})
		
		return w_dict

	def df(self, filesystem=''):
		"""Runs df on machine with filesystem as a the specified filesystem"""
		return self.disk().usage(filesystem)

	def num_lsof(self):
		"""Runs lsof on the machine, pipes it to wc, and returns the number of open file descriptors as a string"""
		rc,stdout,stderr = self.cmd().run('/usr/sbin/lsof')
		self.check_command(rc,stderr)
		return len(stdout.split('\n')) - 1

	def num_open_files(self):
		"""Runs /sbin/sysctl fs.file-nr and grabs the open, allocated, and max file descriptors as a dictionary"""
		rc,stdout,stderr =self.cmd().run('/sbin/sysctl fs.file-nr')
		self.check_command(rc,stderr)
		out = stdout.split('\t')
		return {
				'open': out[0][out[0].rfind(' ')+1:],
				'allocated': out[1],
				'max': out[2].strip()
				}

	def meminfo(self):
		"""Reads /proc/meminfo and returns a dictionary of type of memory to amount of memory in kB"""
		rc,stdout,stderr = self.cmd().run('/bin/cat /proc/meminfo')
		self.check_command(rc,stderr)
		return dict([[y.strip(':') for y in x.split()[0:2]] for x in stdout.split('\n')][:-1])
		
	def meminfo_process(self):
		"""Returns an NxN array of per-program memory usage in the form of:
		        [[Private, Shared, Total RAM used, Program], ... ]
		"""
		return self.proc().mem()

	def num_process(self):
		"""Runs ps and returns the total number of processes and the number of forks as a dictionary"""
		rc,stdout,stderr = self.cmd().run("/bin/ps faux | grep -c '\_' && ps -e | wc -l")
		self.check_command(rc,stderr)
		stdout = stdout.split('\n')
		return dict([('processes',stdout[1]),('forks',stdout[0])])
	
	def top_process(self, n=10):
		"""Runs ps and returns the pcpu, pid, user, and command of the top n processes consuming cpu"""
		rc,stdout,stderr = self.cmd().run("/bin/ps -eo pcpu,pid,user,args | /bin/sort -k 1 -r | /usr/bin/head -"+str(n))
		self.check_command(rc,stderr)
		return stdout

	def last_ten_users(self):
		"""Returns a listing of the last 10 logged in users"""
		rc,stdout,stderr = self.cmd().run('/usr/bin/last -a | head')
		self.check_command(rc,stderr)	
		return stdout.split('\n')
	
	def iostat(self):
		"""Runs iostat on minion and returns the status of disks as a list of devices with values in dictionary form"""
		rc,stdout,stderr = self.cmd().run('/usr/bin/iostat')
		self.check_command(rc,stderr)
		out = [line.split() for line in stdout.split('\n')[6:] if line]
		iostat_dict = []
		for line in out:
			iostat_dict.append({
				'device': line[0],
				'tps': line[1],
				'blk_read/s': line[2],
				'blk_wrtn/s': line[3],
				'blk_read': line[4],
				'blk_wrtn': line[5]
			})

		return iostat_dict
			
	def nfsstat(self):
		rc,stdout,stderr = self.cmd().run('/usr/sbin/nfsstat')
		self.check_command(rc,stderr)
		return stdout[:len(stdout)-1]

	def short_stat(self):
		"""Runs commands on local machine for a short stat and returns output in dictionary form"""
		uul = self.uptime_users_load()
		short_dict = {
				'uptime': uul['uptime'],
				'load': uul['load'],
				'mem': self.meminfo(),
				'num_users': uul['num_users'],
				'num_process': self.num_process(),
				'num_files': self.num_open_files(),
				'df': self.df()
			}
		return short_dict

	def long_stat(self):
		"""Runs commands on the local minion for a long stat and returns output in dictionary form"""
		uul = self.uptime_users_load()
		long_dict = {
			'uptime': uul['uptime'],
			'load': uul['load'],
			'users': uul['users'],
			'last': self.last_ten_users(),
			'num_users': uul['num_users'],
			'num_process': self.num_process(),
			'num_files': self.num_open_files(),
			'top_process': self.top_process(),
			'top_mem': self.meminfo_process(),
			'iostat': self.iostat(),
			'nfsstat': self.nfsstat(),
			'df': self.df()
			}
		return long_dict
