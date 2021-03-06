#! /usr/bin/env python
# encoding: utf-8
# WARNING! All changes made to this file will be lost!

import os,re,logging,traceback,sys
try:
	if'NOCOLOR'not in os.environ:
		import waflib.ansiterm
except:
	pass
LOG_FORMAT="%(asctime)s %(c1)s%(zone)s%(c2)s %(message)s"
HOUR_FORMAT="%H:%M:%S"
zones=''
verbose=0
colors_lst={'USE':True,'BOLD':'\x1b[01;1m','RED':'\x1b[01;31m','GREEN':'\x1b[32m','YELLOW':'\x1b[33m','PINK':'\x1b[35m','BLUE':'\x1b[01;34m','CYAN':'\x1b[36m','NORMAL':'\x1b[0m','cursor_on':'\x1b[?25h','cursor_off':'\x1b[?25l',}
got_tty=not os.environ.get('TERM','dumb')in['dumb','emacs']
if got_tty:
	try:
		got_tty=sys.stderr.isatty()
	except AttributeError:
		got_tty=False
if not got_tty or'NOCOLOR'in os.environ:
	colors_lst['USE']=False
def get_term_cols():
	return 80
try:
	import struct,fcntl,termios
except ImportError:
	pass
else:
	if got_tty:
		def get_term_cols_real():
			dummy_lines,cols=struct.unpack("HHHH",fcntl.ioctl(sys.stderr.fileno(),termios.TIOCGWINSZ,struct.pack("HHHH",0,0,0,0)))[:2]
			return cols
		try:
			get_term_cols_real()
		except:
			pass
		else:
			get_term_cols=get_term_cols_real
def get_color(cl):
	if not colors_lst['USE']:return''
	return colors_lst.get(cl,'')
class color_dict(object):
	def __getattr__(self,a):
		return get_color(a)
	def __call__(self,a):
		return get_color(a)
colors=color_dict()
re_log=re.compile(r'(\w+): (.*)',re.M)
class log_filter(logging.Filter):
	def __init__(self,name=None):
		pass
	def filter(self,rec):
		rec.c1=colors.PINK
		rec.c2=colors.NORMAL
		rec.zone=rec.module
		if rec.levelno>=logging.INFO:
			if rec.levelno>=logging.ERROR:
				rec.c1=colors.RED
			elif rec.levelno>=logging.WARNING:
				rec.c1=colors.YELLOW
			else:
				rec.c1=colors.GREEN
			return True
		zone=''
		m=re_log.match(rec.msg)
		if m:
			zone=rec.zone=m.group(1)
			rec.msg=m.group(2)
		if zones:
			return getattr(rec,'zone','')in zones or'*'in zones
		elif not verbose>2:
			return False
		return True
class formatter(logging.Formatter):
	def __init__(self):
		logging.Formatter.__init__(self,LOG_FORMAT,HOUR_FORMAT)
	def format(self,rec):
		if rec.levelno>=logging.WARNING or rec.levelno==logging.INFO:
			try:
				return'%s%s%s'%(rec.c1,rec.msg,rec.c2)
			except:
				return rec.c1+rec.msg+rec.c2
		return logging.Formatter.format(self,rec)
log=None
def debug(*k,**kw):
	if verbose:
		k=list(k)
		k[0]=k[0].replace('\n',' ')
		global log
		log.debug(*k,**kw)
def error(*k,**kw):
	global log
	log.error(*k,**kw)
	if verbose>2:
		st=traceback.extract_stack()
		if st:
			st=st[:-1]
			buf=[]
			for filename,lineno,name,line in st:
				buf.append('  File "%s", line %d, in %s'%(filename,lineno,name))
				if line:
					buf.append('	%s'%line.strip())
			if buf:log.error("\n".join(buf))
def warn(*k,**kw):
	global log
	log.warn(*k,**kw)
def info(*k,**kw):
	global log
	log.info(*k,**kw)
def init_log():
	global log
	log=logging.getLogger('waflib')
	log.handlers=[]
	log.filters=[]
	hdlr=logging.StreamHandler()
	hdlr.setFormatter(formatter())
	log.addHandler(hdlr)
	log.addFilter(log_filter())
	log.setLevel(logging.DEBUG)
def make_logger(path,name):
	logger=logging.getLogger(name)
	hdlr=logging.FileHandler(path,'w')
	formatter=logging.Formatter('%(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.DEBUG)
	return logger
def pprint(col,str,label='',sep='\n'):
	sys.stderr.write("%s%s%s %s%s"%(colors(col),str,colors.NORMAL,label,sep))
