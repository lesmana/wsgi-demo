#!/usr/bin/env python

import wsgiref.simple_server
import urllib.parse
import html
import http.cookies

def getqueryget(environ):
  queryget = {}
  querygetstr = environ.get('QUERY_STRING', '')
  if querygetstr:
    querygetraw = urllib.parse.parse_qs(querygetstr)
    for key, value in querygetraw.items():
      queryget[key] = html.escape(value[0])
  return queryget

def getquerypost(environ):
  querypost = {}
  contentlengthstr = environ.get('CONTENT_LENGTH', '')
  if contentlengthstr:
    contentlength = int(contentlengthstr)
    querypoststream = environ['wsgi.input']
    querypostbytes = querypoststream.read(contentlength)
    querypoststr = str(querypostbytes, 'utf8')
    querypostraw = urllib.parse.parse_qs(querypoststr)
    for key, value in querypostraw.items():
      querypost[key] = html.escape(value[0])
  return querypost

def getcookies(environ):
  cookies = {}
  cookiestr = environ['HTTP_COOKIE']
  if cookiestr:
    cookiesraw = http.cookies.SimpleCookie(cookiestr)
    for key, value in cookiesraw.items():
      cookies[key] = value
  return cookies

def index(environ, start_response):
  queryget = getqueryget(environ)
  querypost = getquerypost(environ)
  cookies = getcookies(environ)
  htmlstring = f"""
    <html>
    <title>demo wsgi</title>
    <body>
    <p>query get</p>
    {queryget}
    <p>query post</p>
    {querypost}
    <p>cookies</p>
    {cookies}
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
