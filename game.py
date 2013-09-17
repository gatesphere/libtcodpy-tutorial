#@+leo-ver=5-thin
#@+node:peckj.20130917090235.2648: * @file game.py
#@@language python

#@+<< imports >>
#@+node:peckj.20130917090235.2649: ** << imports >>
import libtcodpy as libtcod
#@-<< imports >>
#@+<< definitions >>
#@+node:peckj.20130917090235.2650: ** << definitions >>
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
#@-<< definitions >>

#@+others
#@+node:peckj.20130917090235.2651: ** setup
# set custom font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# initialize the window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'libtcod tutorial', False)

# set FPS
libtcod.sys_set_fps(LIMIT_FPS)

# set player position
playerx = SCREEN_WIDTH/2
playery = SCREEN_HEIGHT/2
#@+node:peckj.20130917090235.2653: ** handle_keys
def handle_keys():
  global playerx, playery
  
  # real-time games: check_for_keypress is non-blocking
  # key = libtcod.console_check_for_keypress()
  
  # turn-based games: wait_for_keypress is blocking
  key = libtcod.console_wait_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    # lalt+enter = fullscreen
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  
  elif key.vk == libtcod.KEY_ESCAPE:
    return True # exit game
  
  # movement keys
  if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    playery -= 1
    
  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    playery += 1

  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    playerx -= 1
    
  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    playerx += 1
#@+node:peckj.20130917090235.2652: ** main loop
while not libtcod.console_is_window_closed():
  # update screen
  libtcod.console_set_default_foreground(0, libtcod.white)
  libtcod.console_put_char(0, playerx, playery, '@', libtcod.BKGND_NONE)
  libtcod.console_flush()
  
  # prevent @ trails (will be apparent on next update)
  libtcod.console_put_char(0, playerx, playery, ' ', libtcod.BKGND_NONE) 
  
  # grab keys (blocking)
  exit = handle_keys()
  if exit:
    break
#@-others
#@-leo
