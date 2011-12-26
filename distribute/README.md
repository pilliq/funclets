# distribute

A script for transferring [Func](https://fedorahosted.org/func/) modules among minions. 

Distribute runs the module through [pyflakes](https://launchpad.net/pyflakes) if installed, copies the module to its minions, and restarts ```funcd```.

## Usage
```distribute.py [options] [module(s) path]```

### Options
```-m, --minions``` a list of minions to distribute modules to separated by semicolons

```-g, --groups``` a list of groups to distribute modules to separated by semicolons

```-n, --no-check``` do not run the module through pyflakes 
