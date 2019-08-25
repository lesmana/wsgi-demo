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

def whatserver(environ, start_response):
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

def main():
  httpd = wsgiref.simple_server.make_server('', 31337, whatserver)
  print("Serving HTTP on port 31337")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print('keyboard interrupt')
    print('shutting down')

if __name__ == '__main__':
  main()
