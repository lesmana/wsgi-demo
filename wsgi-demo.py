#!/usr/bin/env python

# wsgi demo
# Copyright Lesmana Zimmer lesmana@gmx.de
# Licensed under WTFPL version 2
# http://www.wtfpl.net/about/

import wsgiref.simple_server
import urllib.parse
import html
import http.cookies

import io

def getqueryget(environ):
  queryget = {}
  querygetstr = environ.get('QUERY_STRING', '')
  if querygetstr:
    queryget = urllib.parse.parse_qs(querygetstr)
  return queryget

def formatquery(query):
  htmlstr = io.StringIO()
  for rawkey, rawvalues in query.items():
    for rawvalue in rawvalues:
      key = html.escape(rawkey)
      value = html.escape(rawvalue)
      htmlstr.write(f'<li>{key}: {value}</li>')
  return htmlstr.getvalue()

def demoget(environ, start_response):
  queryget = getqueryget(environ)
  querygetstr = formatquery(queryget)
  htmlstring = f'''
    <html>
    <title>wsgi get demo</title>
    <body>
    <p><a href="?foo=bar">one key (?foo=bar)</a></p>
    <p><a href="?foo=bar&bar=baz">two keys (?foo=bar&bar=baz)</a></p>
    <p><a href="?foo=bar&foo=baz">one key repeated (?foo=bar&foo=baz)</a></p>
    <p>query get</p>
    <ul>
    {querygetstr}
    </ul>
    <p><a href="/">back</a></p>
    </body>
    </html>
  '''
  htmlbytes = bytes(htmlstring, 'utf8')
  status = '200 OK'
  headers = [('Content-Type', 'text/html; charset=utf-8')]
  start_response(status, headers)
  return [htmlbytes]

def getquerypost(environ):
  querypost = {}
  contentlengthstr = environ.get('CONTENT_LENGTH', '')
  if contentlengthstr:
    contentlength = int(contentlengthstr)
    querypoststream = environ['wsgi.input']
    querypostbytes = querypoststream.read(contentlength)
    querypoststr = str(querypostbytes, 'utf8')
    querypost = urllib.parse.parse_qs(querypoststr)
  return querypost

def demopost(environ, start_response):
  querypost = getquerypost(environ)
  querypoststr = formatquery(querypost)
  htmlstring = f'''
    <html>
    <title>wsgi post demo</title>
    <body>
    <form action="" method="post">
    <p>foo: <input type="text" name="foo" value="1"></p>
    <p>bar: <input type="text" name="bar" value="2"></p>
    <p>bar: <input type="text" name="bar"> (key repeated)</p>
    <p><input type="submit" value="submit"></p>
    </form>
    <p>query post</p>
    <ul>
    {querypoststr}
    </ul>
    <p><a href="/">back</a></p>
    </body>
    </html>
  '''
  htmlbytes = bytes(htmlstring, 'utf8')
  status = '200 OK'
  headers = [('Content-Type', 'text/html; charset=utf-8')]
  start_response(status, headers)
  return [htmlbytes]

def getcookies(environ):
  cookies = http.cookies.SimpleCookie()
  cookiestr = environ.get('HTTP_COOKIE', '')
  if cookiestr:
    cookies.load(cookiestr)
  return cookies

def formatcookies(cookies):
  htmlstr = io.StringIO()
  for cookie in cookies.values():
    rawcookiestr = cookie.OutputString()
    cookiestr = html.escape(rawcookiestr)
    htmlstr.write(f'<li>{cookiestr}</li>')
  return htmlstr.getvalue()

def democookie(environ, start_response):
  cookies = getcookies(environ)
  cookiesstr = formatcookies(cookies)
  htmlstring = f'''
    <html>
    <title>wsgi cookie demo</title>
    <body>
    <p>cookies</p>
    <ul>
    {cookiesstr}
    </ul>
    <p><a href="setcookie1">set cookie1</a></p>
    <p><a href="setcookie2">set cookie2</a></p>
    <p><a href="delcookie1">del cookie1</a></p>
    <p><a href="delcookie2">del cookie2</a></p>
    <p><a href="/">back to main</a></p>
    </body>
    </html>
  '''
  htmlbytes = bytes(htmlstring, 'utf8')
  status = '200 OK'
  headers = [('Content-Type', 'text/html; charset=utf-8')]
  start_response(status, headers)
  return [htmlbytes]

def cookieaction(environ, start_response, action, number):
  cookiename = f'cookie{number}'
  htmlstring = f'''
    <html>
    <title>wsgi cookie demo action</title>
    <p>cookie {number} is {action}</p>
    <p><a href="democookie">back to cookie page</a></p>
    <body>
    </body>
    </html>
  '''
  htmlbytes = bytes(htmlstring, 'utf8')
  cookie = http.cookies.SimpleCookie()
  cookie[cookiename] = f'cookie number {number}'
  if action == 'del':
    cookie[cookiename]['max-age'] = 0
  status = '200 OK'
  headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie', cookie[cookiename].OutputString())
        ]
  start_response(status, headers)
  return [htmlbytes]

def index(environ, start_response):
  htmlstring = f'''
    <html>
    <title>wsgi demo</title>
    <body>
    <p><a href="demoget">demo get</a></p>
    <p><a href="demopost">demo post</a></p>
    <p><a href="democookie">demo cookie</a></p>
    <p><a href="demoerror">demo error page</a> (page does not exist)</p>
    </body>
    </html>
  '''
  htmlbytes = bytes(htmlstring, 'utf8')
  status = '200 OK'
  headers = [('Content-Type', 'text/html; charset=utf-8')]
  start_response(status, headers)
  return [htmlbytes]

def errorpage(environ, start_response, path):
  textstring = 'error 404 not found: ' + path
  textbytes = bytes(textstring, 'utf8')
  status = '404 NOT FOUND'
  headers = [('Content-Type', 'text/plain; charset=utf-8')]
  start_response(status, headers)
  return [textbytes]

def demoserver(environ, start_response):
  path = environ.get('PATH_INFO', '').lstrip('/')
  if path == '':
    return index(environ, start_response)
  elif path == 'demoget':
    return demoget(environ, start_response)
  elif path == 'demopost':
    return demopost(environ, start_response)
  elif path == 'democookie':
    return democookie(environ, start_response)
  elif path == 'setcookie1':
    return cookieaction(environ, start_response, 'set', 1)
  elif path == 'setcookie2':
    return cookieaction(environ, start_response, 'set', 2)
  elif path == 'delcookie1':
    return cookieaction(environ, start_response, 'del', 1)
  elif path == 'delcookie2':
    return cookieaction(environ, start_response, 'del', 2)
  else:
    return errorpage(environ, start_response, path)

def main():
  httpd = wsgiref.simple_server.make_server('', 31337, demoserver)
  print('Serving HTTP on port 31337')
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print('keyboard interrupt')
    print('shutting down')

if __name__ == '__main__':
  main()
