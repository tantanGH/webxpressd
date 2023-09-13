import os
import argparse
import signal
import socketserver
import http.server
import requests
import io

from bs4 import BeautifulSoup
from PIL import Image

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

#
#  Custom Exception class
#
class HttpException(Exception):
  def __init__(self, code):
    self.code = code
  def __str__(self):
    return repr(self.code)

#
#  Custom HTTP Request Handler class
#
class WebXpressHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

  #
  #  HEAD handler
  #
  def do_HEAD(self):

    protocol = None
    status_code = None
    content_type = None
    content_length = None
    last_modified = None

    try:

      if self.path[:7] == "/?http=":
        protocol = "http"
        url = self.path[7:]
      elif self.path[:8] == "/?https=":
        protocol = "https"
        url = self.path[8:]
      else:
        raise HttpException(404)

      res = requests.head(protocol + "://" + url)
      status_code = res.status_code
      if 'Content-Type' in res.headers:
        content_type = res.headers['Content-Type'].split(';')[0]
      if 'Content-Length' in res.headers:
        content_length = res.headers['Content-Length']
      if 'Last-Modified' in res.headers:
        last_modified = res.headers['Last-Modified']
      self.send_response(status_code)
      if content_type:
        self.send_header('Content-Type', content_type)
      if content_length:
        self.send_header('Content-Length', content_length)
      if last_modified:
        self.send_header('Last-Modified', last_modified)
      self.end_headers()

    except HttpException as e:
      self.send_response(e.code)

  #
  #  GET handler
  #
  def do_GET(self):

    protocol = None
    url = None
    status_code = None
    content_type = None
    content = None

    try:

      if self.path[:7] == "/?http=":
        protocol = "http"
        url = self.path[7:]
      elif self.path[:8] == "/?https=":
        protocol = "https"
        url = self.path[8:]
      else:
        raise HttpException(404)

      res = requests.get(protocol + "://" + url)
      status_code = res.status_code
      content_type = res.headers['Content-Type']
      if content_type[:9] == "image/svg":
        svg = svg2rlg(io.BytesIO(res.content))
        pngImgByteArr = io.BytesIO()
        renderPM.drawToFile(svg, pngImgByteArr, fmt="PNG")
        image = Image.open(pngImgByteArr).convert('RGB')
        if image.width >= 2048:
          image = image.resize((image.width // 4, image.height // 4))
        elif image.width >= 1024:
          image = image.resize((image.width // 2, image.height // 2))
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format="JPEG", quality=self.server.image_quality)
        content_type = "image/jpeg"
        content = imgByteArr.getvalue()        
      elif content_type[:6] == "image/":
        image = Image.open(io.BytesIO(res.content)).convert('RGB')
        if image.width >= 2048:
          image = image.resize((image.width // 4, image.height // 4))
        elif image.width >= 1024:
          image = image.resize((image.width // 2, image.height // 2))
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format="JPEG", quality=self.server.image_quality)
        content_type = "image/jpeg"
        content = imgByteArr.getvalue()
      elif content_type[:9] == "text/html":
        content_type = "text/html"
        content = res.content
      elif content_type[:10] == "text/plain":
        content_type = "text/plain"
        content = res.content
      else:
        raise HttpException(404)

      if content_type == "text/html":

        soup = BeautifulSoup(content, 'html.parser')

#        for tag in soup.findAll(['meta', 'link', 'style', 'script', 'iframe', 'picture']):
        for tag in soup.findAll(['meta', 'link', 'style', 'script', 'iframe']):
          tag.decompose()

        # special hack for xbeeing.com
        if 'xbeeing.com' in url:
          for div in soup.findAll('div', attrs={'id':'sidebar'}):
            div.decompose()
          for div in soup.findAll('div', attrs={'id':'related-box'}):
            div.decompose()

        for a in soup.findAll('a', href=True):
          href = a["href"].strip()
          if href[:7] == "http://":
            a["href"] = "http://webxpressd/?http=" + href[7:]
          elif href[:8] == "https://":
            a["href"] = "http://webxpressd/?https=" + href[8:]
          elif href[:1] == "/":
            if self.path[:7] == "/?http=":
              pos = self.path[7:].find('/')
              a["href"] = "http://webxpressd/?http=" + self.path[7:7+pos+1] + href[1:]
            elif self.path[:8] == "/?https=":
              pos = self.path[8:].find('/')
              a["href"] = "http://webxpressd/?https=" + self.path[8:8+pos+1] + href[1:]
          else:
            if self.path[:7] == "/?http=":
              pos = self.path[7:].rfind('/')
              a["href"] = "http://webxpressd/?http=" + self.path[7:7+pos+1] + href
            elif self.path[:8] == "/https=":
              pos = self.path[8:].rfind('/')
              a["href"] = "http://webxpressd/?https=" + self.path[8:8+pos+1] + href 

        for img in soup.findAll('img', attrs={"srcset":True}):
          del img["srcset"]

        for img in soup.findAll('img', attrs={"data-origin":True}):
          img["src"] = img["data-origin"].strip()
          del img["data-origin"]

        for img in soup.findAll('img', attrs={"data-original":True}):
          img["src"] = img["data-original"].strip()
          del img["data-original"]

        for img in soup.findAll('img', src=True):
          src = img["src"].strip()
          if src[:5] == "data:":
            img.decompose()
          elif src[:7] == "http://":
            img["src"] = "http://webxpressd/?http=" + src[7:]
          elif src[:8] == "https://":
            img["src"] = "http://webxpressd/?https=" + src[8:]
          elif src[:1] == "/":
            pos = url.find('/')
            img["src"] = "http://webxpressd/?" + protocol + "=" + url[:pos+1] + src[1:]
          else:
            pos = url.rfind('/')
            img["src"] = "http://webxpressd/?" + protocol + "=" + url[:pos+1] + src

        content = soup.encode('cp932', 'ignore')

      self.send_response(status_code)
      self.send_header('Content-Type', content_type)
      self.end_headers()
      self.wfile.write(content)

    except HttpException as e:
      self.send_response(e.code)
      self.send_header('Content-Type', 'text/plain')
      self.end_headers()
      self.wfile.write(b'error')

#
#  Server class
#
class StoppableServer(socketserver.TCPServer):

  # sigterm handler
  def sigterm_handler(self, signum, frame):
    print("Received SIGTERM. Stopping the service.")
    os.kill(os.getpid(), signal.SIGINT)   # emulate CTRL+C

  # service loop
  def run(self, image_quality, chrome_driver):
    
    self.image_quality = image_quality
    self.driver_path = chrome_driver
    self.driver = None

    #os.makedirs(self.cache_path, exist_ok=True)

    if self.driver_path:
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
      if self.driver:
        self.driver.quit()
      print("Stopped.")

# main
def main():

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="service port number", type=int, default=6803)
    parser.add_argument("--image_quality", help="image quality", type=int, default=20)
    args = parser.parse_args()

    # start service
    socketserver.TCPServer.allow_reuse_address = True
    with StoppableServer(("0.0.0.0", args.port), WebXpressHTTPRequestHandler) as server:
      print(f"Started at port {args.port}")
      server.run(args.image_quality, None)

if __name__ == "__main__":
    main()
