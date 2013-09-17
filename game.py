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

MAP_WIDTH = 80
MAP_HEIGHT = 45

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)
#@-<< definitions >>

#@+others
#@+node:peckj.20130917090235.2654: ** Object class
class Object:
  #@+others
  #@+node:peckj.20130917090235.2655: *3* __init__
  def __init__(self, x, y, char, color):
    self.x = x
    self.y = y
    self.char = char
    self.color = color
  #@+node:peckj.20130917090235.2656: *3* move
  def move(self, dx, dy):
    if not map[self.x + dx][self.y + dy].blocked:
      self.x += dx
      self.y += dy
  #@+node:peckj.20130917090235.2657: *3* draw
  def draw(self):
    libtcod.console_set_default_foreground(con, self.color)
    libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
  #@+node:peckj.20130917090235.2658: *3* clear
  def clear(self):
    libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
  #@-others
#@+node:peckj.20130917090235.2659: ** Tile class
class Tile:
  #@+others
  #@+node:peckj.20130917090235.2660: *3* __init__
  def __init__(self, blocked, block_sight = None):
    self.blocked = blocked
    
    #by default, if a tile is blocked, it also blocks sight
    if block_sight is None: block_sight = blocked
    self.block_sight = block_sight
  #@-others
  
#@+node:peckj.20130917090235.2651: ** setup
# set custom font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# initialize the window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'libtcod tutorial', False)

# off-screen console
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

# set FPS
libtcod.sys_set_fps(LIMIT_FPS)

# game objects
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
objects = [npc, player]
#@+node:peckj.20130917090235.2662: ** make_map
# make the map
def make_map():
  global map
  
  # fill map with unblocked tiles
  map = [[ Tile(False) for y in range(MAP_HEIGHT) ] for x in range(MAP_WIDTH) ]
  
  # pillars
  map[30][22].blocked = True
  map[30][22].block_sight = True
  map[50][22].blocked = True
  map[50][22].block_sight = True
#@+node:peckj.20130917090235.2663: ** render_all
def render_all():
  for object in objects:
    object.draw()
  
  for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
      wall = map[x][y].block_sight
      if wall:
        libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
      else:
        libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )
  
  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
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
    player.move(0,-1)
    
  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    player.move(0,1)

  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    player.move(-1,0)
    
  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    player.move(1,0)
#@+node:peckj.20130917090235.2652: ** main loop
make_map()

while not libtcod.console_is_window_closed():
  # update screen
  render_all()
  libtcod.console_flush()
  
  # prevent @ trails (will be apparent on next update)
  for object in objects:
    object.clear()
  
  # grab keys (blocking)
  exit = handle_keys()
  if exit:
    break
#@-others
#@-leo
