
from string import ascii_lowercase, digits
from itertools import combinations
from threading import Thread
from time import sleep
import curses
import requests


TIMEOUT = 2                                # Request Timeout in s
RPS = 2                                    # Requests per second
CHARS = ascii_lowercase + digits + '-'     # All possible subdomain chars
BASE_DOMAIN = 'google.com'                 # The base domain (e.g. google.com)


found = []

SCAN_RUNNING = True

def check_subdomain(sdm: str):
  try:
    r = requests.get(f'http://{sdm}.{BASE_DOMAIN}/', timeout=TIMEOUT)

    stdscr.addstr(4, 1, f"HTTP Response: {r.status_code}")

    if r.status_code is None: return False

    return True
  except Exception:
    return False


def subdomain_thread():
  i = 1

  while SCAN_RUNNING:
    for combination in combinations(CHARS, i):
      subdomain = ''.join(combination)

      clear()

      stdscr.addstr(3, 1, f"Checking subdomain: {subdomain} (at length: {i})")

      if check_subdomain(subdomain):
        found.append(subdomain)

      if len(found) > 0:
        stdscr.addstr(6, 1, "Subdomains found:", curses.color_pair(1))

      for j in range(len(found)):
        stdscr.addstr(7 + j, 1, found[j])

      stdscr.refresh()

      sleep(1 / RPS)
    
    i += 1


def init():
  stdscr.clear()
  curses.noecho()
  curses.cbreak()
  curses.curs_set(False)
  curses.start_color()
  curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
  curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

  stdscr.scrollok(True)
  stdscr.idlok(1)
  stdscr.scroll(100)


def clear():
  h, w = stdscr.getmaxyx()

  stdscr.clear()
  stdscr.addstr(1, 1, "Subdomain Scanner", curses.A_BOLD + curses.color_pair(4))
  stdscr.addstr(h - 2, w - 18, "Ctrl + C to exit", curses.color_pair(4))



def update():
  stdscr.nodelay(1)
  c = stdscr.getch()
  if c == 3:
      stdscr.addstr(2, 0, "Ctrl+C: Exiting")
      stdscr.refresh()
      raise KeyboardInterrupt
  else:
      curses.flushinp()


def main():
  global SCAN_RUNNING

  try:
    t = Thread(target=subdomain_thread)
    t.daemon = True
    t.start()

    while True:
      update()
  finally:
    SCAN_RUNNING = False

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

    print(f"All subdomains found ({len(found)}):")
    
    for f in found:
      print(f"> {f}.{BASE_DOMAIN}")


if __name__ == '__main__':
  stdscr = curses.initscr()

  init()
  main()
