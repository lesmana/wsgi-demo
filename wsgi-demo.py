#!/usr/bin/env python

# wsgi demo
# Copyright Lesmana Zimmer lesmana@gmx.de
# Licensed under WTFPL version 2
# http://www.wtfpl.net/about/

import wsgiref.simple_server
import urllib.parse
import html
import http.cookies

import collections
import io

def getqueryget(environ):
  queryget = collections.defaultdict(list)
  querygetstr = environ.get('QUERY_STRING', '')
  if querygetstr:
    querygetraw = urllib.parse.parse_qs(querygetstr)
    for key, values in querygetraw.items():
      for value in values:
        queryget[key].append(html.escape(value))
  return queryget

def demoget(environ, start_response):
  queryget = getqueryget(environ)
  htmlstring = f"""
    <html>
    <title>wsgi get demo</title>
    <body>
    <p><a href="?foo=bar">one key</a></p>
    <p><a href="?foo=bar&bar=baz">two keys</a></p>
    <p><a href="?foo=bar&foo=baz">one key repeated</a></p>
    <p>query get</p>
    {queryget}
    <p><a href="/">back</a></p>
    </body>
    </html>
  """
  status = '200 OK'
  headers = [('Content-Type', 'text/html')]
  start_response(status, headers)
  return [bytes(htmlstring, 'utf8')]

def getquerypost(environ):
  querypost = collections.defaultdict(list)
  contentlengthstr = environ.get('CONTENT_LENGTH', '')
  if contentlengthstr:
    contentlength = int(contentlengthstr)
    querypoststream = environ['wsgi.input']
    querypostbytes = querypoststream.read(contentlength)
    querypoststr = str(querypostbytes, 'utf8')
    querypostraw = urllib.parse.parse_qs(querypoststr)
    for key, values in querypostraw.items():
      for value in values:
        querypost[key].append(html.escape(value))
  return querypost

def demopost(environ, start_response):
  querypost = getquerypost(environ)
  htmlstring = f"""
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
    {querypost}
    <p><a href="/">back</a></p>
    </body>
    </html>
  """
  status = '200 OK'
  headers = [('Content-Type', 'text/html')]
  start_response(status, headers)
  return [bytes(htmlstring, 'utf8')]

def getcookies(environ):
  cookies = http.cookies.SimpleCookie()
  cookiestr = environ.get('HTTP_COOKIE', '')
  if cookiestr:
    cookies.load(cookiestr)
  return cookies

def formatcookies(cookies):
  html = io.StringIO()
  for cookie in cookies.values():
    html.write(f'<li>{cookie.OutputString()}</li>')
  return html.getvalue()

def democookie(environ, start_response):
  cookies = getcookies(environ)
  htmlstring = f"""
    <html>
    <title>wsgi cookie demo</title>
    <body>
    <p>cookies</p>
    <ul>
    {formatcookies(cookies)}
    </ul>
    <p><a href="setcookie1">set cookie 1</a></p>
    <p><a href="setcookie2">set cookie 2</a></p>
    <p><a href="delcookie1">del cookie 1</a></p>
    <p><a href="delcookie2">del cookie 2</a></p>
    <p><a href="/">back to main</a></p>
    </body>
    </html>
  """
  status = '200 OK'
  headers = [('Content-Type', 'text/html')]
  start_response(status, headers)
  return [bytes(htmlstring, 'utf8')]

def cookieaction(environ, start_response, action, number):
  htmlstring = f"""
    <html>
    <title>wsgi cookie demo action</title>
    <p>cookie {number} is {action}</p>
    <p><a href="democookie">back to cookie page</a></p>
    <body>
    </body>
    </html>
  """
  cookie = http.cookies.SimpleCookie()
  cookie[number] = f'cookie number {number}'
  if action == 'del':
    cookie[number]['max-age'] = 0
  status = '200 OK'
  headers = [
        ('Content-Type', 'text/html'),
        ('Set-Cookie', cookie[number].OutputString())
        ]
  start_response(status, headers)
  return [bytes(htmlstring, 'utf8')]

def index(environ, start_response):
  htmlstring = f"""
    <html>
    <title>wsgi demo</title>
    <body>
    <p><a href="demoget">demo get</a></p>
    <p><a href="demopost">demo post</a></p>
    <p><a href="democookie">demo cookie</a></p>
    <p><a href="demoerror">demo error page</a> (page does not exist)</p>
    </body>
    </html>
  """
  status = '200 OK'
  headers = [('Content-Type', 'text/html')]
  start_response(status, headers)
  return [bytes(htmlstring, 'utf8')]

def errorpage(environ, start_response, path):
  status = '404 NOT FOUND'
  headers = [('Content-Type', 'text/plain')]
  start_response(status, headers)
  return [bytes('error 404 not found: ' + path, 'utf8')]

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
    return cookieaction(environ, start_response, 'set', '1')
  elif path == 'setcookie2':
    return cookieaction(environ, start_response, 'set', '2')
  elif path == 'delcookie1':
    return cookieaction(environ, start_response, 'del', '1')
  elif path == 'delcookie2':
    return cookieaction(environ, start_response, 'del', '2')
  else:
    return errorpage(environ, start_response, path)

def main():
  httpd = wsgiref.simple_server.make_server('', 31337, demoserver)
  print("Serving HTTP on port 31337")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print('keyboard interrupt')
    print('shutting down')

if __name__ == '__main__':
  main()
