#@+leo-ver=5-thin
#@+node:peckj.20130917090235.2648: * @file game.py
#@@language python

#@+<< imports >>
#@+node:peckj.20130917090235.2649: ** << imports >>
import libtcodpy as libtcod
import math
import textwrap
import shelve
#import heapq
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
color_dark_wall = libtcod.dark_grey
color_light_wall = libtcod.light_grey
color_dark_ground = libtcod.darker_orange
color_light_ground = libtcod.dark_orange
#@+node:peckj.20130917090235.2677: *3* dungeon generation
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

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
#@+node:peckj.20130918082920.2706: *3* inventory stuff
INVENTORY_WIDTH = 50

#@+node:peckj.20130918082920.2736: *3* spells/scrolls/items
# spells
HEAL_AMOUNT = 40

LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5

CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8

FIREBALL_DAMAGE = 25
FIREBALL_RADIUS = 3
#@+node:peckj.20130918082920.2742: *3* character advancement
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

LEVEL_SCREEN_WIDTH = 40

CHARACTER_SCREEN_WIDTH = 30
#@+node:peckj.20130920123421.3486: *3* scheduler stuff
MAX_SCHEDULER_TICKS = 15
#@-others
#@-<< definitions >>

#@+others
#@+node:peckj.20130917090235.2664: ** classes
#@+node:peckj.20130917090235.2654: *3* Object class
class Object:
  #@+others
  #@+node:peckj.20130917090235.2655: *4* __init__
  def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, player=None, fighter=None, actor=None, ai=None, item=None, equipment=None):
    self.blocks = blocks
    self.name = name
    self.x = x
    self.y = y
    self.char = char
    self.color = color
    self.always_visible = always_visible
    
    self.fighter = fighter
    if self.fighter:
      self.fighter.owner = self
      
    self.ai = ai
    if self.ai:
      self.ai.owner = self
    
    self.item = item
    if self.item:
      self.item.owner = self
      
    self.equipment = equipment
    if self.equipment:
      self.equipment.owner = self
      self.item = Item()
      self.item.owner = self
    
    self.player = player
    if self.player:
      self.player.owner = self
    
    self.actor = actor
    if self.actor:
      self.actor.owner = self
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
  #@+node:peckj.20130918082920.2728: *4* distance
  def distance(self, x, y):
    return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
  #@+node:peckj.20130918082920.2696: *4* send_to_back
  def send_to_back(self):
    global objects
    objects.remove(self)
    objects.insert(0, self)
  #@+node:peckj.20130917090235.2657: *4* draw
  def draw(self):
    if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
      libtcod.console_set_default_foreground(con, self.color)
      libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
  #@+node:peckj.20130917090235.2658: *4* clear
  def clear(self):
    libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
  #@-others
#@+node:peckj.20130920123421.3482: *3* Component classes
#@+node:peckj.20130920123421.3483: *4* AI components
#@+node:peckj.20130918082920.2688: *5* BasicMonster class
class BasicMonster:
  #@+others
  #@+node:peckj.20130918082920.2689: *6* take_turn
  def take_turn(self):
    monster = self.owner
    if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
      if monster.distance_to(player) >= 2:
        monster.move_towards(player.x, player.y)
      elif player.fighter.hp > 0:
        monster.fighter.attack(player)
  #@-others
  
#@+node:peckj.20130918082920.2723: *5* ConfusedMonster class
class ConfusedMonster:
  #@+others
  #@+node:peckj.20130918082920.2725: *6* __init__
  def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
    self.old_ai = old_ai
    self.num_turns = num_turns
  #@+node:peckj.20130918082920.2724: *6* take_turn
  def take_turn(self):
    if self.num_turns > 0:
      self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
      self.num_turns -= 1
    else:
      self.owner.ai = self.old_ai
      message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
  #@-others
  
#@+node:peckj.20130920123421.3477: *4* Player class
class Player:
  #@+others
  #@+node:peckj.20130920123421.3478: *5* __init__
  def __init__(self, level=0):
    self.level = level
  #@+node:peckj.20130920123421.3480: *5* check_level_up
  def check_level_up(self):
    level_up_xp = LEVEL_UP_BASE + self.level * LEVEL_UP_FACTOR
    if self.owner.fighter.xp >= level_up_xp:
      self.level_up()
  #@+node:peckj.20130920123421.3481: *5* level_up
  def level_up(self):
    level_up_xp = LEVEL_UP_BASE + self.level * LEVEL_UP_FACTOR
    self.level += 1
    self.owner.fighter.xp -= level_up_xp
    message('Your battle skills grow stronger! You reached level ' + str(self.level) + '!', libtcod.yellow)
    
    choice = None
    while choice == None:
      choice = menu('Level up! Choose a stat to raise:\n',
        ['Constitution (+20 HP, from ' + str(self.owner.fighter.max_hp) + ')',
         'Strength (+1 attack, from ' + str(self.owner.fighter.power) + ')',
         'Agility (+1 defense, from ' + str(self.owner.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)
    if choice == 0:
      player.fighter.base_max_hp += 20
      player.fighter.hp += 20
    elif choice == 1:
      player.fighter.base_power += 1
    elif choice == 2:
      player.fighter.base_defense += 1
  #@-others
  
#@+node:peckj.20130918082920.2686: *4* Fighter class
class Fighter:
  #@+others
  #@+node:peckj.20130918082920.2687: *5* __init__
  def __init__(self, hp, defense, power, xp, death_function=None):
    self.base_max_hp = hp
    self.hp = hp
    self.base_defense = defense
    self.base_power = power
    self.xp = xp
    self.death_function = death_function
  #@+node:peckj.20130918082920.2692: *5* take_damage
  def take_damage(self, damage):
    if damage > 0:
      self.hp -= damage
    if self.hp <= 0:
      function = self.death_function
      if function is not None:
        function(self.owner)
      if self.owner != player:
        player.fighter.xp += self.xp
  #@+node:peckj.20130918082920.2693: *5* attack
  def attack(self, target):
    damage = self.power - target.fighter.defense
    if damage > 0:
      message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
      target.fighter.take_damage(damage)
    else:
      message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
  #@+node:peckj.20130918082920.2712: *5* heal
  def heal(self, amount):
    self.hp += amount
    if self.hp > self.max_hp:
      self.hp = self.max_hp
  #@+node:peckj.20130919090559.2751: *5* power
  @property
  def power(self):
    bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
    return self.base_power + bonus
  #@+node:peckj.20130919090559.2753: *5* defense
  @property
  def defense(self):
    bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
    return self.base_defense + bonus
  #@+node:peckj.20130919090559.2754: *5* max_hp
  @property
  def max_hp(self):
    bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
    return self.base_max_hp + bonus
  #@-others
#@+node:peckj.20130920123421.3487: *4* Actor class
class Actor:
  #@+others
  #@+node:peckj.20130920123421.3488: *5* __init__
  def __init__(self, speed=0, act_function=None, active=True, time=1):
    self.speed = speed
    self.active = active
    self.time = time
    self.act_function = act_function
  #@+node:peckj.20130920123421.3489: *5* act
  def act(self):
    function = self.act_function
    print 'acting'
    print 'scheduler.ticks: %s' % scheduler.ticks
    if function is None or not self.active:
      return True # prevent lockups forever
    if function is not None:
      result = function(self.owner)
    if result:
      my_ticks = MAX_SCHEDULER_TICKS - self.speed
      self.time = scheduler.ticks + my_ticks
      #print "new time: %s" % self.time
    return result
  #@+node:peckj.20130920123421.3492: *5* __cmp__
  def __cmp__(self, other):
    if self.time < other.time:
      return -1
    elif self.time == other.time:
      return 0
    else:
      return 1
  #@-others
#@+node:peckj.20130918082920.2702: *4* Item class
class Item:
  #@+others
  #@+node:peckj.20130918082920.2707: *5* __init__
  def __init__(self, use_function=None):
    self.use_function = use_function
  #@+node:peckj.20130918082920.2703: *5* pick_up
  def pick_up(self):
    if len(inventory) >= 26:
      message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
    else:
      inventory.append(self.owner)
      objects.remove(self.owner)
      message('You picked up a ' + self.owner.name + '!', libtcod.green)
      equipment = self.owner.equipment
      if equipment and get_equipped_in_slot(equipment.slot) is None:
        equipment.equip()
  #@+node:peckj.20130918082920.2731: *5* drop
  def drop(self):
    objects.append(self.owner)
    inventory.remove(self.owner)
    self.owner.x = player.x
    self.owner.y = player.y
    message('You dropped a ' + self.owner.name + '.', libtcod.yellow)
    if self.owner.equipment:
      self.owner.equipment.dequip()
  #@+node:peckj.20130918082920.2710: *5* use
  def use(self):
    if self.owner.equipment:
      self.owner.equipment.toggle_equip()
      return
    if self.use_function is None:
      message('The ' + self.owner.name + ' cannot be used.')
    else:
      if self.use_function() != 'cancelled':
        inventory.remove(self.owner)
  #@-others
  
#@+node:peckj.20130919090559.2745: *4* Equipment class
class Equipment:
  #@+others
  #@+node:peckj.20130919090559.2746: *5* __init__
  def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
    self.power_bonus = power_bonus
    self.defense_bonus = defense_bonus
    self.max_hp_bonus = max_hp_bonus
    self.slot = slot
    self.is_equipped = False
  #@+node:peckj.20130919090559.2747: *5* toggle_equip
  def toggle_equip(self):
    if self.is_equipped:
      self.dequip()
    else:
      self.equip()
  #@+node:peckj.20130919090559.2748: *5* equip
  def equip(self):
    old_equipment = get_equipped_in_slot(self.slot)
    if old_equipment is not None:
      old_equipment.dequip()
    self.is_equipped = True
    message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
  #@+node:peckj.20130919090559.2749: *5* dequip
  def dequip(self):
    if not self.is_equipped: return
    self.is_equipped = False
    message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)
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
#@+node:peckj.20130920123421.3484: *3* Scheduler class
class Scheduler:
  #@+others
  #@+node:peckj.20130920123421.3485: *4* __init__
  def __init__(self, schedule={}, ticks=-1L, tracked=[]):
    self.schedule = schedule
    self.tracked = tracked
    self.ticks = ticks
  #@+node:peckj.20130920123421.3490: *4* tick
  def tick(self):
    actors = []
    while actors == []:
      actors = self.schedule.pop(self.ticks, [])
      self.ticks += 1
    print self.ticks
    print actors
    for a in actors:
      r = a.act()
      while not r:
        r = a.act()
      self.push(a)
  #@+node:peckj.20130920123421.3493: *4* remove
  def remove(self, actor):
    print 'removing %s' % actor.owner.name
    if actor not in self.tracked:
      print 'actor not in scheduler'
      return
    for s in self.schedule.values():
      if actor in s:
        s.remove(actor)
        print s
    self.tracked.remove(actor)
  #@+node:peckj.20130920123421.3491: *4* push
  def push(self, actor):
    self.schedule.setdefault(actor.time, []).append(actor)
    if actor not in self.tracked: self.tracked.append(actor)
  #@-others
#@+node:peckj.20130917090235.2666: ** helper functions
#@+node:peckj.20130918082920.2713: *3* mapping
#@+node:peckj.20130917090235.2662: *4* make_map
# make the map
def make_map():
  global map, objects, stairs
  
  objects = [player]
  
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
  
  stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
  objects.append(stairs)
  stairs.send_to_back()
#@+node:peckj.20130917090235.2671: *4* create_room
def create_room(room):
  global map
  for x in range(room.x1 + 1, room.x2):
    for y in range(room.y1 + 1, room.y2):
      map[x][y].blocked = False
      map[x][y].block_sight = False
#@+node:peckj.20130917090235.2672: *4* create_h_tunnel
def create_h_tunnel(x1, x2, y):
  global map
  for x in range(min(x1, x2), max(x1, x2) + 1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
#@+node:peckj.20130917090235.2674: *4* create_v_tunnel
def create_v_tunnel(y1, y2, x):
  global map
  for y in range(min(y1, y2), max(y1, y2) + 1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
#@+node:peckj.20130917203359.2679: *4* place_objects
def place_objects(room):
  # set up the object placer
  max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
  monster_chances = {}
  monster_chances['orc'] = 80
  monster_chances['troll'] = from_dungeon_level([[15, 2], [30, 5], [60, 7]])
  max_items = from_dungeon_level([[1, 1], [2, 4]])
  item_chances = {}
  item_chances['heal'] = 35
  item_chances['lightning'] = from_dungeon_level([[25, 4]])
  item_chances['fireball'] = from_dungeon_level([[25, 6]])
  item_chances['confuse'] = from_dungeon_level([[10, 2]])
  item_chances['sword'] = from_dungeon_level([[5, 4]])
  item_chances['shield'] = from_dungeon_level([[15, 8]])
  
  #choose random number of monsters
  num_monsters = libtcod.random_get_int(0, 0, max_monsters)
  
  for i in range(num_monsters):
    #choose random spot for this monster
    x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
    y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

    if not is_blocked(x, y):
      choice = random_choice(monster_chances)
      if choice == 'orc':
        #create an orc
        fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
        ai_component = BasicMonster()
        actor_component = Actor(speed=2, act_function=monster_take_action)
        monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component, actor=actor_component)
      elif choice == 'troll':
        #create a troll
        fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
        ai_component = BasicMonster()
        actor_component = Actor(speed=5, act_function=monster_take_action)
        monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component, actor=actor_component)
  
      objects.append(monster)
      
  
  num_items = libtcod.random_get_int(0, 0, max_items)
  for i in range(num_items):
    x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
    y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
    if not is_blocked(x, y):
      choice = random_choice(item_chances)
      if choice == 'heal':
        item_component = Item(use_function=cast_heal)
        item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component, always_visible=True)
      elif choice == 'lightning':
        item_component = Item(use_function=cast_lightning)
        item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component, always_visible=True)
      elif choice == 'fireball':
        item_component = Item(use_function=cast_fireball)
        item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component, always_visible=True)
      elif choice == 'confuse':
        item_component = Item(use_function=cast_confuse)
        item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component, always_visible=True)
      elif choice == 'sword':
        equipment_component = Equipment(slot='right hand', power_bonus=3)
        item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
      elif choice == 'shield':
        equipment_component = Equipment(slot='left hand', defense_bonus=1)
        item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
        
      objects.append(item)
      item.send_to_back()
#@+node:peckj.20130918082920.2714: *3* rendering
#@+node:peckj.20130917090235.2663: *4* render_all
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
  libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))
  for (line, color) in game_msgs:
    libtcod.console_set_default_foreground(panel, color)
    libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    y += 1
  libtcod.console_set_default_foreground(panel, libtcod.light_gray)
  libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
  
  libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
#@+node:peckj.20130918082920.2697: *4* render_bar
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
#@+node:peckj.20130918082920.2700: *4* message
def message(new_msg, color=libtcod.white):
  new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
  for line in new_msg_lines:
    if len(game_msgs) == MSG_HEIGHT:
      del game_msgs[0]
    game_msgs.append((line, color))
    
#@+node:peckj.20130918082920.2715: *3* menus
#@+node:peckj.20130918082920.2704: *4* menu
def menu(header, options, width):
  if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
  header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
  if header == '':
    header_height = 0
  height = len(options) + header_height
  
  window = libtcod.console_new(width, height)
  libtcod.console_set_default_foreground(window, libtcod.white)
  libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
  
  y = header_height
  letter_index = ord('a')
  for option_text in options:
    text = '(' + chr(letter_index) + ') ' + option_text
    libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
    y += 1
    letter_index += 1
  
  x = SCREEN_WIDTH / 2 - width/2
  y = SCREEN_HEIGHT / 2 - height/2
  libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
  
  libtcod.console_flush()
  key = libtcod.console_wait_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  index = key.c - ord('a')
  if index >= 0 and index < len(options): return index
  return None
#@+node:peckj.20130918082920.2740: *4* msgbox
def msgbox(text, width=50):
  menu(text, [], width)
#@+node:peckj.20130918082920.2705: *4* inventory_menu
def inventory_menu(header):
  if len(inventory) == 0:
    options = ['Inventory is empty.']
  else:
    #options = [item.name for item in inventory]
    options = []
    for item in inventory:
      text = item.name
      if item.equipment and item.equipment.is_equipped:
        text = text + ' (on ' + item.equipment.slot + ')'
      options.append(text)
    
  index = menu(header, options, INVENTORY_WIDTH)
  if index is None or len(inventory) == 0: return None
  return inventory[index].item
#@+node:peckj.20130918082920.2737: *4* main_menu
def main_menu():
  img = libtcod.image_load('menu_background1.png')
  while not libtcod.console_is_window_closed():
    libtcod.image_blit_2x(img, 0, 0, 0)
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'TOMBS OF THE ANCIENT KINGS')
    libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Jake Peck (following Jotaf\'s tutorial)')
    choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
    if choice == 0:
      new_game()
      play_game()
    elif choice == 1:
      try:
        load_game()
      except:
        msgbox('\n No saved game to load.\n', 24)
        continue
      play_game()
    elif choice == 2:
      break
#@+node:peckj.20130918082920.2716: *3* items
#@+node:peckj.20130918082920.2711: *4* cast_heal
def cast_heal():
  if player.fighter.hp == player.fighter.max_hp:
    message('You are already at full health.', libtcod.red)
    return 'cancelled'
  message('Your wounds start to feel better!', libtcod.light_violet)
  player.fighter.heal(HEAL_AMOUNT)
#@+node:peckj.20130918082920.2721: *4* cast_lightning
def cast_lightning():
  monster = closest_monster(LIGHTNING_RANGE)
  if monster is None:
    message('No enemy is close enough to strike.', libtcod.red)
    return 'cancelled'
  message('A lightning bold strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
  monster.fighter.take_damage(LIGHTNING_DAMAGE)
#@+node:peckj.20130918082920.2726: *4* cast_confuse
def cast_confuse():
  message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
  monster = target_monster(CONFUSE_RANGE)
  if monster is None: return 'cancelled'
  else:
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)
#@+node:peckj.20130918082920.2729: *4* cast_fireball
def cast_fireball():
  message('Left-click a target tile for the fireball, or right-click to cance.', libtcod.light_cyan)
  (x, y) = target_tile()
  if x is None: return 'cancelled'
  message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
  for obj in objects:
    if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
      message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
      obj.fighter.take_damage(FIREBALL_DAMAGE)
#@+node:peckj.20130918082920.2717: *3* ai
#@+node:peckj.20130918082920.2695: *4* monster_death
def monster_death(monster):
  global scheduler
  scheduler.remove(monster.actor)
  monster.actor.active = False
  message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)
  monster.char = '%'
  monster.color = libtcod.dark_red
  monster.blocks = False
  monster.fighter = None
  monster.ai = None
  monster.name = 'remains of ' + monster.name
  monster.send_to_back()
#@+node:peckj.20130918082920.2694: *4* player_death
def player_death(player):
  global game_state
  message('You died!', libtcod.red)
  game_state = 'dead'
  
  player.char = '%'
  player.color = libtcod.dark_red
  scheduler.remove(player.actor)
  player.actor.active = False
#@+node:peckj.20130918082920.2718: *3* query
#@+node:peckj.20130917203908.2680: *4* is_blocked
def is_blocked(x, y):
  if map[x][y].blocked:
    return True
  for object in objects:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False
#@+node:peckj.20130918082920.2722: *4* closest_monster
def closest_monster(max_range):
  closest_enemy = None
  closest_dist = max_range + 1
  for object in objects:
    if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
      dist = player.distance_to(object)
      if dist < closest_dist:
        closest_enemy = object
        closest_dist = dist
  return closest_enemy
#@+node:peckj.20130918082920.2719: *3* actions
#@+node:peckj.20130918082920.2701: *4* get_names_under_mouse
def get_names_under_mouse():
  global mouse
  (x, y) = (mouse.cx, mouse.cy)
  names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
  names = ', '.join(names)
  return names.capitalize()
#@+node:peckj.20130918082920.2727: *4* target_tile
def target_tile(max_range=None):
  global key, mouse
  while True:
    libtcod.console_flush()
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
    render_all()
    
    (x, y) = (mouse.cx, mouse.cy)
    
    if mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and (max_range is None or player.distance(x, y) <= max_range):
      return (x, y)
    if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
      return (None, None)
#@+node:peckj.20130918082920.2730: *4* target_monster
def target_monster(max_range=None):
  while True:
    (x, y) = target_tile(max_range)
    if x is None:
      return None
    for obj in objects:
      if obj.x == x and obj.y == y and obj.fighter and obj != player:
        return obj
#@+node:peckj.20130917090235.2653: *4* handle_keys
def handle_keys():
  global fov_recompute, key
  
  print 'called handle_keys'
  #key = libtcod.console_wait_for_keypress(True)
  print 'key = %s' % chr(key.c)

  if key.vk == libtcod.KEY_ENTER and key.lalt:
    # lalt+enter = fullscreen
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit' # exit game
    
  if game_state == 'playing':
    # movement keys
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
      player_move_or_attack(0, -1)
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
      player_move_or_attack(0, 1)
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      player_move_or_attack(-1, 0)
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      player_move_or_attack(1, 0)
    elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
      player_move_or_attack(-1, -1)
    elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
      player_move_or_attack(1, -1)
    elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
      player_move_or_attack(-1, 1)
    elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
      player_move_or_attack(1, 1)
    elif key.vk == libtcod.KEY_KP5:
      pass  #do nothing ie wait for the monster to come to you
    
    else:
      # test for other keys
      key_char = chr(key.c)
      if key_char == 'g':
        for object in objects:
          if object.x == player.x and object.y == player.y and object.item:
            object.item.pick_up()
            break
      if key_char == 'i':
        chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
        if chosen_item is not None:
          chosen_item.use()
      if key_char == 'd':
        chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
        if chosen_item is not None:
          chosen_item.drop()
      if key_char == '<':
        if stairs.x == player.x and stairs.y == player.y:
          next_level()
      if key_char == 'c':
        level_up_xp = LEVEL_UP_BASE + player.player.level * LEVEL_UP_FACTOR
        msgbox('Character Information\n\nLevel: ' + str(player.player.level) + '\nExperience: ' + str(player.fighter.xp) +
               '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
               '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense), CHARACTER_SCREEN_WIDTH)
      return 'didnt-take-turn'
#@+node:peckj.20130917203908.2681: *4* player_move_or_attack
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
#@+node:peckj.20130919090559.2750: *4* get_equipped_in_slot
def get_equipped_in_slot(slot):
  for obj in inventory:
    if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
      return obj.equipment
  return None
#@+node:peckj.20130919090559.2752: *4* get_all_equipped
def get_all_equipped(obj):
  if obj == player:
    equipped_list = []
    for item in inventory:
      if item.equipment and item.equipment.is_equipped:
        equipped_list.append(item.equipment)
    return equipped_list
  else:
    return []
#@+node:peckj.20130920123421.3494: *4* player_take_action
def player_take_action(self):
  global game_state, player_action
  
  player_action = handle_keys()
  if player_action == 'exit':
    game_state = 'exit'
    return True
    
  if game_state == 'playing' and player_action == 'didnt-take-turn':
    return False
  
  return True
#@+node:peckj.20130920123421.3496: *4* monster_take_action
def monster_take_action(self):
  self.ai.take_turn()
  return True
#@+node:peckj.20130918082920.2734: *3* game loop
#@+node:peckj.20130919090559.2744: *4* from_dungeon_level
def from_dungeon_level(table):
  for (value, level) in reversed(table):
    if dungeon_level >= level:
      return value
  return 0
#@+node:peckj.20130919090559.2742: *4* random_choice_index
def random_choice_index(chances):
  dice = libtcod.random_get_int(0, 1, sum(chances))
  running_sum = 0
  choice = 0
  for w in chances:
    running_sum += w
    if dice <= running_sum:
      return choice
    choice += 1
#@+node:peckj.20130919090559.2743: *4* random_choice
def random_choice(chances_dict):
  chances = chances_dict.values()
  strings = chances_dict.keys()
  return strings[random_choice_index(chances)]
  
#@+node:peckj.20130918082920.2732: *4* new_game
def new_game():
  global player, inventory, game_msgs, game_state, dungeon_level, scheduler
  
  # create player
  fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
  player_component = Player(level=1)
  actor_component = Actor(speed=5, act_function=player_take_action, time=0)
  player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, player=player_component, actor=actor_component)
  
  # generate map
  dungeon_level = 1
  make_map()
  
  # initialize fov
  initialize_fov()
  
  # game state
  game_state = 'playing'
  inventory = []
  
  # messages
  game_msgs = []
  message('Welcome stranger! Prepare to parish in the Tombs of the Ancient Kings.', libtcod.red)

  # equip the player
  equipment_component = Equipment(slot='right hand', power_bonus=2)
  obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
  inventory.append(obj)
  equipment_component.equip()
  obj.always_visible = True
  
  # set up the scheduler
  scheduler = Scheduler()
  #scheduler.push(player.actor)
  for a in objects:
    if a.actor is not None:
      scheduler.push(a.actor)
  
#@+node:peckj.20130918082920.2733: *4* initialize_fov
def initialize_fov():
  global fov_recompute, fov_map
  fov_recompute = True
  
  libtcod.console_clear(con)
  fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
  for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
      libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
#@+node:peckj.20130918082920.2735: *4* play_game
def play_game():
  global key, mouse
  
  player_action = None
  
  mouse = libtcod.Mouse()
  key = libtcod.Key()
  while not libtcod.console_is_window_closed():
    #libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
    render_all()
    
    libtcod.console_flush()
    player.player.check_level_up()
    
    for object in objects:
      object.clear()
    
    scheduler.tick()
    
    if game_state == 'exit':
      save_game()
      break
#@+node:peckj.20130918082920.2738: *4* save_game
def save_game():
  file = shelve.open('savegame', 'n')
  file['map'] = map
  file['objects'] = objects
  file['player_index'] = objects.index(player)
  file['inventory'] = inventory
  file['game_msgs'] = game_msgs
  file['game_state'] = game_state
  file['stairs_index'] = objects.index(stairs)
  file['dungeon_level'] = dungeon_level
  file.close()
#@+node:peckj.20130918082920.2739: *4* load_game
def load_game():
  global map, objects, player, inventory, game_msgs, game_state, stairs, dungeon_level
  
  file = shelve.open('savegame', 'r')
  map = file['map']
  objects = file['objects']
  player = objects[file['player_index']]
  inventory = file['inventory']
  game_msgs = file['game_msgs']
  game_state = file['game_state']
  stairs = objects[file['stairs_index']]
  dungeon_level = file['dungeon_level']
  file.close()
  
  initialize_fov()
#@+node:peckj.20130918082920.2741: *4* next_level
def next_level():
  global dungeon_level
  message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
  player.fighter.heal(player.fighter.max_hp / 2)
  message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
  dungeon_level += 1
  make_map()
  initialize_fov()
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
#@+node:peckj.20130917090235.2652: ** main logic
main_menu()
#@-others
#@-leo
