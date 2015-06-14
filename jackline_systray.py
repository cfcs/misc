#!/usr/bin/env python2

## apt-get install python-gtk2

import gtk
import gobject
import sys
import threading
import os
import socket
import select

class TrayIcon(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.icon = gtk.status_icon_new_from_stock(gtk.STOCK_ABOUT)
    self.icon.set_visible(False)
    self.icon.connect('activate', self.on_left_click)

  def run(self):
    loop = select.epoll()
    print 'opening', self.pipe
    self.fd = open(self.pipe, 'r')
    loop.register(self.fd, select.EPOLLIN)
    print '.. registered', self.pipe
    while True:
      ret = loop.poll()
      print ret
      for (fd, event) in ret:
        print fd
        if event == select.EPOLLHUP:
          ## fifo closed, TODO handle that
          loop.unregister(fd)
          self.fd = open(self.pipe, 'r')
          loop.register(self.fd, select.EPOLLIN)
          continue
        status = os.read(fd, 4096).strip()
        ## possible states:
        # let to_string = function
        # | Q -> "quit"
        # | D -> "disconnected"
        # | C -> "connected"
        # | D_N -> "disconnected_notifications"
        # | C_N -> "connected_notifications"
        if 'connected_notifications' in status \
        or 'disconnected_notifications' in status:
          self.icon.set_from_stock(gtk.STOCK_ABOUT)
          self.icon.set_visible(True)
        elif 'connected' in status:
          self.icon.set_visible(False)
        elif 'quit' in status:
          self.icon.set_from_stock(gtk.STOCK_DELETE)
          print 'we have quit'
        elif 'disconnected' in status:
          print 'we have disconnected'
          self.icon.set_from_stock(gtk.STOCK_DELETE)
        else:
          print 'unknown status: ', status

  def on_left_click(self, event):
    self.icon.set_visible(False)
 
if __name__ == "__main__":
  if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
    print('argv[1:] must be the names of the fifos')
    sys.exit(1)

  gobject.threads_init()
  for pipe in sys.argv[1:]:
    t = TrayIcon()
    t.pipe = pipe
    t.start()

  try:
    gtk.main()
  except KeyboardInterrupt:
    os._exit(0)

