#!/use/bin/python36

import os, re, requests

COOKIE = ""
API = ""
USERVID = ""
SAVED = []

def init():
	'''初始化'''
	global COOKIE, API, SAVED
	if not os.path.exists("cookie"):
		with open("cookie", "w") as f:
			pass
	with open("cookie") as f:
		COOKIE = f.read()
	if not os.path.exists("api"):
		with open("api", "w") as f:
			pass
	with open("api") as f:
		API = f.read()
	if not os.path.exists("saved"):
		with open("saved", "w") as f:
			pass
	with open("saved") as f:
		SAVED = f.read()
	readSavedNote()

def collect_cookie():
	'''获取cookie'''
	global USERVID, COOKIE
	cookie = input("请输入你的cookie:")
	handle_cookie(cookie)
	if not USERVID:
		print("cookie输入错误")
		collect_cookie()
	else:
		COOKIE = cookie
		with open("cookie", 'w') as f:
			f.write(cookie)

def handle_cookie(cookie):
	'''验证cookie'''
	global USERVID
	for c in cookie.split(';'):
		try:
			k, v = c.strip().split('=')
			if k == 'wr_vid' and v is not None and v != '':
				USERVID = v
				break
		except ValueError:
			continue

def collect_api():
	'''获取API'''
	global API
	api_url = input("请输入你的方寸笔迹api地址:")
	API = api_url
	with open("api", 'w') as f:
		f.write(api_url)

def handle_api(url):
	pattern = re.compile("https:\/\/api.fang-cun.net\/api\/open\/note\/.+")
	match = pattern.match(url)
	if match is None:
		print("API地址错误，请重试")
		collect_api()

def getBooks():
	'''读取书架'''
	global COOKIE, USERVID
	headers = {'Cookie': COOKIE}
	params = {'userVid' : USERVID}
	wx_resp = requests.get("https://i.weread.qq.com/shelf/friendCommon", params = params, headers = headers)
	if wx_resp.status_code == 401:
		print("Cookie错误，请重新输入:")
		collect_cookie()
	elif wx_resp.status_code == 200:
		shelf = wx_resp.json()
		for book in shelf['recentBooks']:
			print("正在读取<%s>的读书笔记\n"%book['title'])
			getBookmarks(book['bookId'], book['title'])
	else:
		print("请重试")

def getBookmarks(bookid, book):
	'''读取所有笔记'''
	params = {'bookId' : bookid}
	headers = {'Cookie': COOKIE}
	bookmark_resp = requests.get("https://i.weread.qq.com/book/bookmarklist", params = params, headers = headers)
	bookmarks = bookmark_resp.json()
	for bookmark in bookmarks['updated']:
		print("正在同步读书笔记：%s\n"%bookmark['markText'])
		syncNotes(bookmark['markText'], book, bookmark['bookmarkId'])

def syncNotes(bookmark, book, bookmark_id):
	'''同步笔记'''
	global API, SAVED
	if bookmark_id in SAVED:
		return
	note = "#%s  %s"%(book, bookmark)
	params = {'note': note}
	resp = requests.post(API, data = params)
	result = resp.json()
	if resp.status_code == 200 and result['code']:
		print("已同步")
		SAVED.append(bookmark_id)

def saveNoteId(notes):
	'''记录用户已经同步的笔记ID'''
	with open("saved", "w") as f:
		f.write(notes)

def readSavedNote():
	'''读取用户已经同步的笔记ID'''
	global SAVED
	SAVED = SAVED.split(",")

if __name__ == "__main__":
	init()
	if not COOKIE:
		collect_cookie()
	if not API:
		collect_api()
	handle_cookie(COOKIE)
	getBooks()
	saveNoteId(','.join(SAVED))
