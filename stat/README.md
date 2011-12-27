# stat
A module that gathers information on processes, users, memory/cpu, disk health, filesystem usage, and files from minions.

## Installation
Copy `stat.py` to Func's module directory (e.g. /usr/lib/python2.4/site-packages/func/minion/modules), or use [distribute](https://github.com/pilliq/funclets/tree/master/distribute).

## Usage
```./minionstat.py [options] minions```

### Options
```-m, --minions``` a list of minions to stat separated by semicolons

```-g, --groups ``` a list of groups to stat separated by semicolons

```-v, --verbose``` provide more statistics

```-t, --wait-time``` specify the time interval between polling a minion for a completed job in seconds. Default is 1 second

## Examples
Run a short stat on all minions:
```
\# ./minionstat.py
<<< kidtoyz.rutgers.edu >>>
Uptime: 216 days 15 hours 41 minutes
Load: 0.12, 0.03, 0.01
Users: 2
Processes: 91 (50 forks)
Files:
 open: 1530  allocated: 0  max: 48371
Memory:
 Memtotal:     524288 kB
 MemTotal:     524288 kB
 MemFree:      17860  kB
 Buffers:      31380 kB
 Cached:       33348 kB
 SwapCached:   124 kB
Disk Usage:
 Filesystem               1K-blocks   Used        Available   Use%  Mounted        
 /dev/xvda2               9350716     3455700     5420016     39    /              
 /dev/xvda1               483886      37976       420910      9     /boot          
```

Run a long stat on one minion:
```
\# ./minionstat.py -v -m kidtoyz.rutgers.edu

<<< kidtoyz.rutgers.edu >>>
Uptime: 216 days 15 hours 41 minutes
Load: 0.00, 0.00, 0.00
Users:
 hamber	10Oct11	-bash
 marker	03Oct11	sshd:

Last logged in users:
 aberdeen pts/0        Tue Nov 29 12:37 - 12:37  (00:00)     192.168.160.139
 tupmust  pts/5        Fri Oct 21 11:26 - 12:33  (01:07)     kidtoyz2.rutgers.edu
 tupmust  pts/6        Fri Oct 14 13:59 - 16:20  (02:20)     192.168.227.53
 tupmust  pts/5        Fri Oct 14 13:22 - 13:21 (3+23:59)    kidtoyz2.rutgers.edu
 elio     pts/3        Wed Oct 12 15:48 - 10:25 (57+19:36)   192.168.216.59
 hamber   pts/1        Mon Oct 10 17:05   still logged in    jla.rutgers.edu
 tupmust  pts/4        Fri Oct  7 12:00 - 12:30 (14+00:29)   192.168.227.53
 hamber   pts/3        Tue Oct  4 17:55 - 17:05 (5+23:09)    jla.rutgers.edu
 hamber   pts/3        Tue Oct  4 17:55 - 17:55  (00:00)     jla.rutgers.edu
 marker   pts/2        Mon Oct  3 16:58   still logged in    jla.rutgers.edu
 
Processes: 91 (50 forks)

Files:
 open: 1530  allocated: 0  max: 48371

Top Processes:
 %CPU   PID USER     COMMAND
  6.0  5033 root     /usr/bin/python /usr/bin/funcd --daemon
  0.0     9 root     [xenwatch]
  0.0    92 root     [aio/0]
  0.0    91 root     [kswapd0]
  0.0    90 root     [pdflush]
  0.0    89 root     [pdflush]
  0.0     7 root     [kthread]
  0.0   744 root     [kjournald]
  0.0   720 root     [kmpath_handlerd]
 
Top Mem:
 283.0 MiB   nscd
 24.6 MiB    httpd (11)
 18.9 MiB    funcd
 16.9 MiB    mysqld
 8.5 MiB     sshd (5)

iostat:
 Device     tps         Blk_read/s  Blk_wrtn/s  Blk_read    Blk_wrtn    
 xvda       2.64        0.87        46.51       16247990    870713660   
 xvda1      0.00        0.00        0.00        2140        52          
 xvda2      2.64        0.87        46.51       16245594    870713608   
 xvdb       0.00        0.00        0.00        3287        46544       
 xvdb1      0.00        0.00        0.00        2807        46544       

Disk Usage:
 Filesystem               1K-blocks   Used        Available   Use%  Mounted        
 army:/vol/oss/rpmprivate 52428800    29091072    23337728    56    /army/rpmprivate
 config:/sos/config       471859200   343295936   128563264   73    /sos/config    
 /dev/xvda2               9350716     3455680     5420036     39    /              
 army:/vol/centos/centos  419430400   122524192   296906208   30    /army/centos   
 army:/vol/oss/quotatest  10485760    207104      10278656    2     /army/quotatest
 /dev/xvda1               483886      37976       420910      9     /boot          

```

