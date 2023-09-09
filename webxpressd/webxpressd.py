import os
import argparse
import signal
import socketserver
import http.server
import requests
import pathlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 

from bs4 import BeautifulSoup

class WebXpressHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

  def do_GET(self):

    status_code = None
    content_type = None
    content = None
    html = None

    if self.path[:7] == "/?http=":
      url = self.path[7:]
      res = requests.get("http://" + url)
      status_code = res.status_code
      content_type = res.headers['Content-Type']
      if content_type == "text/html" or content_type == "text/plain":
        html = res.text
      elif content_type == "image/jpeg" or content_type == "image/png":
        content = res.content
    elif self.path[:8] == "/?https=":
      url = self.path[8:]
      res = requests.get("https://" + url)
      status_code = res.status_code
      content_type = res.headers['Content-Type']
      if content_type == "text/html" or content_type == "text/plain":
        html = res.text
      elif content_type == "image/jpeg" or content_type == "image/png":
        content = res.content
#    elif self.path[:16] == "/?chrome=1&http=":
#      url = self.path[16:]
#      self.server.driver.get("http://" + url)
#      html = self.server.driver.page_source      
#    elif self.path[:17] == "/?chrome=1&https=":
#      url = self.path[17:]
#      self.server.driver.get("https://" + url)
#      html = self.server.driver.page_source

    if html is not None:

      soup = BeautifulSoup(html, 'html.parser')

      for tag in soup.findAll(['meta', 'link', 'style', 'script', 'iframe', 'picture']):
        tag.decompose()

      for img in soup.findAll(['img']):
        if img["src"][:7] == "http://":
          img["src"] = "http://webxpressd/?http=" + img["src"][7:]
        elif img["src"][:8] == "https://":
          img["src"] = "http://webxpressd/?https=" + img["src"][8:]
        elif img["src"][:1] == "/":
          if self.path[:7] == "/?http=":
            pos = self.path[7:].find('/')
            img["src"] = "http://webxpressd/?http=" + self.path[7:7+pos+1] + img["src"][1:]
          elif self.path[:8] == "/?https=":
            pos = self.path[8:].find('/')
            img["src"] = "http://webxpressd/?https=" + self.path[8:8+pos+1] + img["src"][1:]
        else:
          if self.path[:7] == "/?http=":
            pos = self.path[7:].rfind('/')
            img["src"] = "http://webxpressd/?http=" + self.path[7:7+pos+1] + img["src"]
          elif self.path[:8] == "/https=":
            pos = self.path[8:].rfind('/')
            img["src"] = "http://webxpressd/?https=" + self.path[8:8+pos+1] + img["src"] 

      content = soup.encode('cp932', 'ignore')

    if status_code == 200:
      self.send_response(status_code)
      self.send_header('Content-Type', content_type)
      self.end_headers()
      self.wfile.write(content)
    else:
      self.send_response(status_code)
      self.send_header('Content-Type', 'text/plain')
      self.end_headers()
      self.wfile.write(b'error')

class StoppableServer(socketserver.TCPServer):

  # sigterm handler
  def sigterm_handler(self, signum, frame):
    print("Received SIGTERM. Stopping the service.")
    os.kill(os.getpid(), signal.SIGINT)   # CTRL+C が押されたことにする

  # service loop
  def run(self, cache_path, chrome_driver):
    
    self.cache_path = cache_path
    self.driver_path = chrome_driver

    os.makedirs(self.cache_path, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    self.driver = webdriver.Chrome(service=Service(self.driver_path), options=options)

    signal.signal(signal.SIGTERM, self.sigterm_handler)

    try:
      self.serve_forever()
    except KeyboardInterrupt:
      pass
    finally:
      self.server_close()
      self.driver.quit()
      print("Stopped.")

# main
def main():

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("cache_path", help="cache data path")
    parser.add_argument("--port", help="service port number", type=int, default=6803)
    parser.add_argument("--chrome_driver", help="chrome driver path", default="/usr/bin/chromedriver")
    args = parser.parse_args()

    # start service
    socketserver.TCPServer.allow_reuse_address = True
    with StoppableServer(("0.0.0.0", args.port), WebXpressHTTPRequestHandler) as server:
      print(f"Started at port {args.port}")
      server.run(args.cache_path, args.chrome_driver)

if __name__ == "__main__":
    main()
