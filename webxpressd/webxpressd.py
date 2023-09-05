import os
import argparse
import signal
import socketserver
import http.server

from selenium import webdriver

class WebXpressHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

  def do_GET(self):
    if self.path[:7] == "/?http=":
      self.server.driver.get("http://" + self.path[7:])
    elif self.path[:8] == "/?https=":
      self.server.driver.get("https://" + self.path[8:])
    else:
      self.send_response(400)
      self.send_header('Content-Type', 'text/plain')
      self.end_headers()
      self.wfile.write(b'400 Bad Request')
      return

    html = self.server.driver.page_source
    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(html.encode('cp932', 'ignore'))

class StoppableServer(socketserver.TCPServer):

  # sigterm handler
  def sigterm_handler(self, signum, frame):
    print("Received SIGTERM. Stopping the service.")
    os.kill(os.getpid(), signal.SIGINT)   # CTRL+C が押されたことにする

  # service loop
  def run(self):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    self.driver = webdriver.Chrome(options=options)

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
    parser.add_argument("--port", help="service port number", type=int, default=8080)
    args = parser.parse_args()

    # start service
    socketserver.TCPServer.allow_reuse_address = True
    with StoppableServer(("0.0.0.0", args.port), WebXpressHTTPRequestHandler) as server:
      print(f"Started at port {args.port}")
      server.run()

if __name__ == "__main__":
    main()
