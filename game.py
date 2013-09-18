#@+leo-ver=5-thin
#@+node:peckj.20130917090235.2648: * @file game.py
#@@language python

#@+<< imports >>
#@+node:peckj.20130917090235.2649: ** << imports >>
import libtcodpy as libtcod
import math
import textwrap
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
MAP_HEIGHT = 43
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

MAX_ROOM_MONSTERS = 3
#@+node:peckj.20130917090235.2678: *3* fov stuff
FOV_ALGO = libtcod.FOV_DIAMOND
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
#@+node:peckj.20130918082920.2698: *3* panel stuff
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
#@+node:peckj.20130918082920.2699: *3* message_bar stuff
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 2
#@-others
#@-<< definitions >>

#@+others
#@+node:peckj.20130917090235.2664: ** classes
#@+node:peckj.20130917090235.2654: *3* Object class
class Object:
  #@+others
  #@+node:peckj.20130917090235.2655: *4* __init__
  def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None):
    self.blocks = blocks
    self.name = name
    self.x = x
    self.y = y
    self.char = char
    self.color = color
    
    self.fighter = fighter
    if self.fighter:
      self.fighter.owner = self
      
    self.ai = ai
    if self.ai:
      self.ai.owner = self
  #@+node:peckj.20130917090235.2656: *4* move
  def move(self, dx, dy):
    newx = self.x + dx
    newy = self.y + dy
    if not is_blocked(newx, newy):
      self.x = newx
      self.y = newy
  #@+node:peckj.20130918082920.2690: *4* move_towards
  def move_towards(self, target_x, target_y):
    # vector from this object to the target, and distance
    dx = target_x - self.x
    dy = target_y - self.y
    distance = math.sqrt(dx ** 2 + dy ** 2)
    
    # normalize it to length 1 (preserving direction) then
    # round and convert to an integer
    dx = int(round(dx/distance))
    dy = int(round(dy/distance))
    self.move(dx, dy)
  #@+node:peckj.20130918082920.2691: *4* distance_to
  def distance_to(self, other):
    # return the distance to another object
    dx = other.x - self.x
    dy = other.y - self.y
    return math.sqrt(dx ** 2 + dy ** 2)
  #@+node:peckj.20130918082920.2696: *4* send_to_back
  def send_to_back(self):
    global objects
    objects.remove(self)
    objects.insert(0, self)
  #@+node:peckj.20130917090235.2657: *4* draw
  def draw(self):
    if libtcod.map_is_in_fov(fov_map, self.x, self.y):
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
#@+node:peckj.20130918082920.2686: *3* Fighter class
class Fighter:
  #@+others
  #@+node:peckj.20130918082920.2687: *4* __init__
  def __init__(self, hp, defense, power, death_function=None):
    self.max_hp = hp
    self.hp = hp
    self.defense = defense
    self.power = power
    self.death_function = death_function
  #@+node:peckj.20130918082920.2692: *4* take_damage
  def take_damage(self, damage):
    if damage > 0:
      self.hp -= damage
    if self.hp <= 0:
      function = self.death_function
      if function is not None:
        function(self.owner)
  #@+node:peckj.20130918082920.2693: *4* attack
  def attack(self, target):
    damage = self.power - target.fighter.defense
    if damage > 0:
      message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
      target.fighter.take_damage(damage)
    else:
      message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
  #@-others
#@+node:peckj.20130918082920.2688: *3* BasicMonster class
class BasicMonster:
  #@+others
  #@+node:peckj.20130918082920.2689: *4* take_turn
  def take_turn(self):
    monster = self.owner
    if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
      if monster.distance_to(player) >= 2:
        monster.move_towards(player.x, player.y)
      elif player.fighter.hp > 0:
        monster.fighter.attack(player)
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
      place_objects(new_room)
      (new_x, new_y) = new_room.center()
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
    if object != player:
      object.draw()
  player.draw()
  
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
  
  libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

  libtcod.console_set_default_background(panel, libtcod.black)
  libtcod.console_clear(panel)
  render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
  y = 1
  for (line, color) in game_msgs:
    libtcod.console_set_default_foreground(panel, color)
    libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    y += 1
  libtcod.console_set_default_foreground(panel, libtcod.light_gray)
  libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
  
  libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
#@+node:peckj.20130918082920.2697: *3* render_bar
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
  bar_width = int(float(value) / maximum * total_width)
  libtcod.console_set_default_background(panel, back_color)
  libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
  libtcod.console_set_default_background(panel, bar_color)
  if bar_width > 0:
    libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
  libtcod.console_set_default_foreground(panel, libtcod.white)
  libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                           name + ': ' + str(value) + '/' + str(maximum))
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
  global fov_recompute, key

  if key.vk == libtcod.KEY_ENTER and key.lalt:
    # lalt+enter = fullscreen
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit' # exit game
    
  if game_state == 'playing':
    # movement keys
    if key.vk == libtcod.KEY_UP:
      player_move_or_attack(0, -1)
      
    elif key.vk == libtcod.KEY_DOWN:
      player_move_or_attack(0, 1)
  
    elif key.vk == libtcod.KEY_LEFT:
      player_move_or_attack(-1, 0)
      
    elif key.vk == libtcod.KEY_RIGHT:
      player_move_or_attack(1, 0)
    
    else:
      return 'didnt-take-turn'
#@+node:peckj.20130918082920.2701: *3* get_names_under_mouse
def get_names_under_mouse():
  global mouse
  (x, y) = (mouse.cx, mouse.cy)
  names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
  names = ', '.join(names)
  return names.capitalize()
#@+node:peckj.20130917203359.2679: *3* place_objects
def place_objects(room):
  #choose random number of monsters
  num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
  
  for i in range(num_monsters):
    #choose random spot for this monster
    x = libtcod.random_get_int(0, room.x1, room.x2)
    y = libtcod.random_get_int(0, room.y1, room.y2)

    if not is_blocked(x, y):
      if libtcod.random_get_int(0, 0, 100) < 80:  #80% chance of getting an orc
        #create an orc
        fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
      else:
        #create a troll
        fighter_component = Fighter(hp=16, defense=1, power=4, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component)
  
      objects.append(monster)
#@+node:peckj.20130917203908.2680: *3* is_blocked
def is_blocked(x, y):
  if map[x][y].blocked:
    return True
  for object in objects:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False
#@+node:peckj.20130917203908.2681: *3* player_move_or_attack
def player_move_or_attack(dx, dy):
  global fov_recompute

  # the coordinates the player is moving to/attacking
  x = player.x + dx
  y = player.y + dy

  # try to find an attackable object there
  target = None
  for object in objects:
    if object.fighter and object.x == x and object.y == y:
      target = object
      break

  # attack if target found, move otherwise
  if target is not None:
    player.fighter.attack(target)
  else:
    player.move(dx, dy)
    fov_recompute = True
#@+node:peckj.20130918082920.2694: *3* player_death
def player_death(player):
  global game_state
  message('You died!', libtcod.red)
  game_state = 'dead'
  
  player.char = '%'
  player.color = libtcod.dark_red
#@+node:peckj.20130918082920.2695: *3* monster_death
def monster_death(monster):
  message(monster.name.capitalize() + ' is dead!', libtcod.orange)
  monster.char = '%'
  monster.color = libtcod.dark_red
  monster.blocks = False
  monster.fighter = None
  monster.ai = None
  monster.name = 'remains of ' + monster.name
  monster.send_to_back()
#@+node:peckj.20130918082920.2700: *3* message
def message(new_msg, color=libtcod.white):
  new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
  for line in new_msg_lines:
    if len(game_msgs) == MSG_HEIGHT:
      del game_msgs[0]
    game_msgs.append((line, color))
    
#@+node:peckj.20130917090235.2651: ** setup
# set custom font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# initialize the window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'libtcod tutorial', False)

# off-screen consoles
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

# set FPS
libtcod.sys_set_fps(LIMIT_FPS)

# game objects
fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)
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

# game state
game_state = 'playing'
player_action = None

# messages
game_msgs = []
message('Welcome stranger! Prepare to parish in the Tombs of the Ancient Kings.', libtcod.red)

# set up mouse and keyboard
mouse = libtcod.Mouse()
key = libtcod.Key()
#@+node:peckj.20130917090235.2652: ** main loop
while not libtcod.console_is_window_closed():
  # update screen
  libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
  render_all()
  libtcod.console_flush()
  
  # prevent @ trails (will be apparent on next update)
  for object in objects:
    object.clear()
  
  # grab keys (blocking)
  player_action = handle_keys()
  if player_action == 'exit':
    break
  
  #let monsters take their turn
  if game_state == 'playing' and player_action != 'didnt-take-turn':
    for object in objects:
      if object.ai:
        object.ai.take_turn()
#@-others
#@-leo
