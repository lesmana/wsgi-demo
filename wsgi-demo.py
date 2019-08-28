#!/usr/bin/env python

import wsgiref.simple_server
import urllib.parse
import html
import http.cookies

import collections

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
    <title>demo wsgi</title>
    <body>
    <p><a href="?foo=bar">one key</a></p>
    <p><a href="?foo=bar&bar=baz">two keys</a></p>
    <p><a href="?foo=bar&foo=baz">one key with two values</a></p>
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
    <title>demo wsgi</title>
    <body>
    <form action="" method="post">
    <p>foo: <input type="text" name="foo"></p>
    <p>bar: <input type="text" name="bar"></p>
    <p>bar: <input type="text" name="bar"> (duplicate key)</p>
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
  cookies = {}
  cookiestr = environ['HTTP_COOKIE']
  if cookiestr:
    cookiesraw = http.cookies.SimpleCookie(cookiestr)
    for key, value in cookiesraw.items():
      cookies[key] = value
  return cookies

def democookie(environ, start_response):
  cookies = getcookies(environ)
  htmlstring = f"""
    <html>
    <title>demo wsgi</title>
    <body>
    <p>cookies</p>
    {cookies}
    <p><a href="/">back</a></p>
    </body>
    </html>
  """
  status = '200 OK'
  headers = [('Content-Type', 'text/html')]
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

def wsgidemo(environ, start_response):
  path = environ.get('PATH_INFO', '').lstrip('/')
  if path == '':
    return index(environ, start_response)
  elif path == 'demoget':
    return demoget(environ, start_response)
  elif path == 'demopost':
    return demopost(environ, start_response)
  elif path == 'democookie':
    return democookie(environ, start_response)
  else:
    return errorpage(environ, start_response, path)

def main():
  httpd = wsgiref.simple_server.make_server('', 31337, wsgidemo)
  print("Serving HTTP on port 31337")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print('keyboard interrupt')
    print('shutting down')

if __name__ == '__main__':
  main()
