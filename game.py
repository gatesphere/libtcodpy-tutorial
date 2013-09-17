#@+leo-ver=5-thin
#@+node:peckj.20130917090235.2648: * @file game.py
#@@language python

#@+<< imports >>
#@+node:peckj.20130917090235.2649: ** << imports >>
import libtcodpy as libtcod
#@-<< imports >>
#@+<< definitions >>
#@+node:peckj.20130917090235.2650: ** << definitions >>
#@+others
#@+node:peckj.20130917090235.2668: *3* screen stuff
# Screen stuff
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
#@+node:peckj.20130917090235.2669: *3* map size
# Map size
MAP_WIDTH = 80
MAP_HEIGHT = 45
#@+node:peckj.20130917090235.2667: *3* color scheme
# color scheme
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)
#@+node:peckj.20130917090235.2677: *3* dungeon generation
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
#@+node:peckj.20130917090235.2678: *3* fov stuff
FOV_ALGO = libtcod.FOV_DIAMOND
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
#@-others
#@-<< definitions >>

#@+others
#@+node:peckj.20130917090235.2664: ** classes
#@+node:peckj.20130917090235.2654: *3* Object class
class Object:
  #@+others
  #@+node:peckj.20130917090235.2655: *4* __init__
  def __init__(self, x, y, char, color):
    self.x = x
    self.y = y
    self.char = char
    self.color = color
  #@+node:peckj.20130917090235.2656: *4* move
  def move(self, dx, dy):
    if not map[self.x + dx][self.y + dy].blocked:
      self.x += dx
      self.y += dy
  #@+node:peckj.20130917090235.2657: *4* draw
  def draw(self):
    libtcod.console_set_default_foreground(con, self.color)
    libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
  #@+node:peckj.20130917090235.2658: *4* clear
  def clear(self):
    libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
  #@-others
#@+node:peckj.20130917090235.2659: *3* Tile class
class Tile:
  #@+others
  #@+node:peckj.20130917090235.2660: *4* __init__
  def __init__(self, blocked, block_sight = None):
    self.explored = False
    self.blocked = blocked
    
    #by default, if a tile is blocked, it also blocks sight
    if block_sight is None: block_sight = blocked
    self.block_sight = block_sight
  #@-others
  
#@+node:peckj.20130917090235.2665: *3* Rect class
class Rect:
  #@+others
  #@+node:peckj.20130917090235.2670: *4* __init__
  def __init__(self, x, y, w, h):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h
  #@+node:peckj.20130917090235.2675: *4* center
  def center(self):
    center_x = (self.x1 + self.x2) / 2
    center_y = (self.y1 + self.y2) / 2
    return (center_x, center_y)
  #@+node:peckj.20130917090235.2676: *4* intersect
  def intersect(self, other):
    #returns true if this rectangle intersects with another one
    return (self.x1 <= other.x2 and self.x2 >= other.x1 and
            self.y1 <= other.y2 and self.y2 >= other.y1)
  #@-others
#@+node:peckj.20130917090235.2666: ** helper functions
#@+node:peckj.20130917090235.2662: *3* make_map
# make the map
def make_map():
  global map
  
  # fill map with unblocked tiles
  map = [[ Tile(True) for y in range(MAP_HEIGHT) ] for x in range(MAP_WIDTH) ]
  
  # dungeon generation
  rooms = []
  num_rooms = 0
  
  for r in range(MAX_ROOMS):
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
    y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
    new_room = Rect(x, y, w, h)
    
    # intersection test
    failed = False
    for other_room in rooms:
      if new_room.intersect(other_room):
        failed = True
        break
    
    if not failed:
      create_room(new_room)
      (new_x, new_y) = new_room.center()
      room_no = Object(new_x, new_y, chr(65+num_rooms), libtcod.red)
      objects.insert(0, room_no)
      if num_rooms == 0: # first room
        player.x = new_x
        player.y = new_y
      else: # all other rooms
        (prev_x, prev_y) = rooms[num_rooms - 1].center()
        if libtcod.random_get_int(0, 0, 1) == 1:
          create_h_tunnel(prev_x, new_x, prev_y)
          create_v_tunnel(prev_y, new_y, new_x)
        else:
          create_v_tunnel(prev_y, new_y, prev_x)
          create_h_tunnel(prev_x, new_x, new_y)
      rooms.append(new_room)
      num_rooms += 1
      
#@+node:peckj.20130917090235.2663: *3* render_all
def render_all():
  global fov_recompute, fov_map
  
  if fov_recompute:
    #recompute FOV if needed (the player moved or something)
    fov_recompute = False
    libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
  
  for object in objects:
    if libtcod.map_is_in_fov(fov_map, object.x, object.y):
      object.draw()
  
  for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
      visible = libtcod.map_is_in_fov(fov_map, x, y)
      wall = map[x][y].block_sight
      if not visible:
        if map[x][y].explored:
          if wall:
            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
          else:
            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
      else:
        if wall:
          libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
        else:
          libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)
        map[x][y].explored = True
  
  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
#@+node:peckj.20130917090235.2671: *3* create_room
def create_room(room):
  global map
  for x in range(room.x1 + 1, room.x2):
    for y in range(room.y1 + 1, room.y2):
      map[x][y].blocked = False
      map[x][y].block_sight = False
#@+node:peckj.20130917090235.2672: *3* create_h_tunnel
def create_h_tunnel(x1, x2, y):
  global map
  for x in range(min(x1, x2), max(x1, x2) + 1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
#@+node:peckj.20130917090235.2674: *3* create_v_tunnel
def create_v_tunnel(y1, y2, x):
  global map
  for y in range(min(y1, y2), max(y1, y2) + 1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
#@+node:peckj.20130917090235.2653: *3* handle_keys
def handle_keys():
  global fov_recompute
  
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
    fov_recompute = True
    
  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    player.move(0,1)
    fov_recompute = True

  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    player.move(-1,0)
    fov_recompute = True
    
  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    player.move(1,0)
    fov_recompute = True
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
objects = [player]
player.x = 25
player.y = 23

# make map, set fov_recompute
make_map()
fov_recompute = True

# fov map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
  for x in range(MAP_WIDTH):
    libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
#@+node:peckj.20130917090235.2652: ** main loop
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
