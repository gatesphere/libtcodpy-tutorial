<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo (http://leoeditor.com/leo_toc.html) -->
<?xml-stylesheet ekr_test?>
<leo_file xmlns:leo="http://www.leo-editor.org/2011/leo" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="peckj.20130917090235.2648" a="E"
expanded="peckj.20130917090235.2650,peckj.20130917090235.2664,peckj.20130918082920.2688,peckj.20130918082920.2723,peckj.20130927083040.3224,peckj.20130920123421.3484,peckj.20130917090235.2666,peckj.20130918082920.2734,"><vh>@file game.py</vh></v>
<v t="peckj.20130925095856.4438" a="E"><vh>Architecture docs</vh>
<v t="peckj.20130925095856.4439"><vh>Objects</vh>
<v t="peckj.20130925095856.4440"><vh>Components</vh>
<v t="peckj.20130925095856.4441"><vh>Actor</vh>
<v t="peckj.20130925095856.4447"><vh>act_functions</vh></v>
</v>
<v t="peckj.20130925095856.4442"><vh>AI</vh></v>
<v t="peckj.20130925095856.4443"><vh>Player</vh></v>
<v t="peckj.20130925095856.4444"><vh>Fighter</vh>
<v t="peckj.20130925095856.4448"><vh>death_functions</vh></v>
</v>
<v t="peckj.20130925095856.4445"><vh>Item</vh>
<v t="peckj.20130925095856.4449"><vh>use_functions</vh></v>
</v>
<v t="peckj.20130925095856.4446"><vh>Equipment</vh></v>
</v>
</v>
<v t="peckj.20130927083040.3214"><vh>Mapping classes</vh>
<v t="peckj.20130927083040.3220"><vh>Tile</vh></v>
<v t="peckj.20130927083040.3221"><vh>Rect</vh></v>
</v>
<v t="peckj.20130927083040.3215"><vh>Scheduler</vh></v>
<v t="peckj.20130927083040.3217"><vh>Global Variables</vh>
<v t="peckj.20130927083040.3218"><vh>Definitions</vh></v>
<v t="peckj.20130927083040.3219"><vh>Dynamic Globals</vh></v>
</v>
<v t="peckj.20130927083040.3225"><vh>Helper functions</vh></v>
<v t="peckj.20130927083040.3216"><vh>Combat</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="peckj.20130925095856.4438"></t>
<t tx="peckj.20130925095856.4439">Objects represent something visible on the screen.

They have location (obj.x, obj.y), color (obj.color), a name (obj.name), a character (obj.char),
a few properties (obj.blocks, obj.always_visible), and several optional components (see child nodes).</t>
<t tx="peckj.20130925095856.4440">Mix ins for Object classes.</t>
<t tx="peckj.20130925095856.4441">An Actor is something that does something.  An Object *needs* an Actor component
to be scheduled in the Scheduler.

# Actor docs:

## Fields:
actor.speed        -&gt; act every SCHEDULER_MAX_TICKS - actor.speed ticks.
actor.active       -&gt; boolean: if False, prevent from acting and rescheduling
actor.time         -&gt; tick in scheduler to schedule next action
actor.act_function -&gt; function to call when act() called

## Functions:
actor.act()        -&gt; called by scheduler - calls actor.act_function() 
                      and updates next action time only if actor.active = True</t>
<t tx="peckj.20130925095856.4442">AI components allow Objects to act.

# Structure of an AI component

AI components are a class that contain at least a `take_turn()` method, which describes what
the object with that AI does on it's turn.

## Defined AI components

BasicMonster    -&gt; Only acts if the player can see them.  Moves niavely towards the player,
                   and attacks blindly until it's dead.
ConfusedMonster -&gt; Moves in a random direction for CONFUSE_NUM_TURNS turns, and then replaces
                   itself with the original AI.  Also possible to change number of turns with
                   the `num_turns` constructor paramater.</t>
<t tx="peckj.20130925095856.4443">The Player component is special.  There should be only one of these.

The Player component tracks the player's character level, as well as handles levelling up.

# Player documentation

## Fields
player.level            -&gt; the player's character level

## Methods
player.check_level_up() -&gt; checks if the player has levelled up yet, and if it has, calls 
                           player.level_up() to handle it
player.level_up()       -&gt; levels up the player, with an interactive menu</t>
<t tx="peckj.20130925095856.4444">If an object has this component, it can take part in combat, take damage, deal damage, etc.

# Figher documentation

## Fields
fighter.base_max_hp           -&gt; fighter's inherent max hp (increases per level, per player.hd)
fighter.hp                    -&gt; fighter's current hp
fighter.base_max_energy       -&gt; fighter's inherent max energy (increases per level, per player.ed)
fighter.energy                -&gt; fighter's current energy
fighter.base_power            -&gt; fighter's inherent physical might
fighter.base_magic            -&gt; fighter's inherent magical power
fighter.base_defense          -&gt; fighter's inherent physical resistance
fighter.base_magic_resistance -&gt; fighter's inherent resistance to magic
fighter.base_hp_recovery      -&gt; fighter's inherent hp recovered per turn
fighter.base_energy_recovery  -&gt; fighter's inherent energy recovered per turn
fighter.hd                    -&gt; fighter's hit dice
fighter.ed                    -&gt; fighter's energy dice
fighter.xp                    -&gt; fighter's xp: Player = current XP, Monster = reward for killing
fighter.death_function        -&gt; function that is triggered when the fighter's hp reaches 0

## Properties
All of these are logically named and share the same behavior: they return the value requested, composed of
the fighter's base value, and bonuses from any equipment.

fighter.max_hp
fighter.max_energy
fighter.power
fighter.defense
fighter.magic
fighter.magic_resistance
fighter.hp_recovery
fighter.energy_recovery

## Methods
fighter.take_damage(damage)   -&gt; reduce fighter.hp by damage, call fighter.death_function if dead
fighter.attack(target)        -&gt; attack target (an object, not a fighter)
fighter.heal(amount)          -&gt; increase fighter.hp by amount, up to fighter.max_hp
</t>
<t tx="peckj.20130925095856.4445">An Item is something that can be picked up, dropped, and used.

# Item documentation

## Fields
item.use_function -&gt; the function called when the item is used

## Methods
item.pick_up()    -&gt; adds the item to the inventory and removes it from the map
item.drop()       -&gt; removes the item from the inventory and adds it to the map
item.use()        -&gt; uses the item up, calling use_function</t>
<t tx="peckj.20130925095856.4446">Equipment are items that can be equipped and dequipped, which provide different bonuses
to a character.  Weapons and armor are good examples.

# Equipment documentation

## Fields
equipment.power_bonus            -&gt; bonus to fighter.power
equipment.defense_bonus          -&gt; bonus to fighter.defense
equipment.max_hp_bonus           -&gt; bonus to fighter.max_hp
equipment.max_energy_bonus       -&gt; bonus to fighter.max_energy
equipment.magic_bonus            -&gt; bonus to fighter.magic
equipment.magic_resistance_bonus -&gt; bonus to fighter.magic_resistance
equipment.hp_recovery_bonus      -&gt; bonus to fighter.hp_recovery
equipment.energy_recovery_bonus  -&gt; bonus to fighter.energy_recovery
equipment.slot                   -&gt; slot the equipment occupies
equipment.is_equipped            -&gt; boolean: True if equipped

## Methods
equipment.toggle_equip()         -&gt; equips if not self.is_equipped, dequips if self.is_equipped
equipment.equip()                -&gt; equips item to self.slot; if item already in slot, dequips that item first
equipment.dequip()               -&gt; dequips item from self.slot

## Valid slots
equipment.slot is just a string, so anything is a valid slot.  Common slots (the set to be used by
my games) are:

  Accessories:
    - ring
    - neck/amulet
    - gloves
  Weapons:
    - weapon (melee)
    - weapon (ranged)
    - ammo
  Armor:
    - armor (chest)
    - armor (legs)
    - armor (helm)</t>
<t tx="peckj.20130925095856.4447">An act_function is a global function that determines what actor.act() does.

The following act_functions are defined:

## player_take_action()

A special action function that simply freezes the scheduler by setting 
game_state = 'playing-waiting-for-input'.  Used by Player's Actor.

## moster_take_action()

Calls the object's AI to take a turn per it's own instructions.  Despite
the name, is usable for any object with an AI component.

# defining an act_function:

act_functions are global functions that take a single parameter named
`self` that will be the acting Object.  They perform some action (often
calling self.ai.take_turn()) and then return True on success.  act_functions
returning False should indicate something going wrong.</t>
<t tx="peckj.20130925095856.4448">death_functions are global functions that define what happens when self.hp &lt;= 0.

The following death_functions are defined:

# monster_death()

- The object's actor is deactivated
- The object's ai and fighter components are removed
- The object stops blocking movement
- The object's char and color become dark red %, to represent a corpse
- The object's name changes to "remains of $name"
- A message is printed on screen

# player_death()

- The game_state changes to 'dead'
- The object's char and color become dark red %, to represent a corpse
- The object's actor is deactivated
- A message is printed on screen

# Structure of a death_function

A death_function is a global function which takes an object as a parameter.  
Typical actions are replacing the dying object with different characters,
and deactivating the object's actor.
</t>
<t tx="peckj.20130925095856.4449">Items have use_functions which define what the item does when used.

The following use_functions are defined:

# cast_heal()

Heals player.fighter.hp by HEAL_AMOUNT.

# cast_lightning()

Deals LIGHTNING_DAMAGE points of damage to the closest enemy within LIGHTNING_RANGE.

# cast_fireball()

Asks the player for a target tile in which to ignite the fireball.  The fireball deals
FIREBALL_DAMAGE to all objects within FIREBALL_RADIUS of the target tile, including the 
player.

# cast_confuse()

Asks the player to target a monster within CONFUSE_RANGE.  Targeted monster's ai is replaced
with ConfusedMonster for CONFUSE_NUM_TURNS turns.

# Building a use_function

A use_function is a global function with no parameters.  It often operates on the objects list, and
occasionally requires input from the player.</t>
<t tx="peckj.20130927083040.3214"></t>
<t tx="peckj.20130927083040.3215">The Scheduler class is used to keep everything organized in a time-based manner.  It wraps
a dictionary composed of entries like {some_time_integer: [some_actor_to_act, some_other_actor_to_act]}.

# Fields
scheduler.ticks       -&gt; The current time of the scheduler, expressed as an integer.
scheduler.schedule    -&gt; The scheduler's map.

# Methods
scheduler.push(actor) -&gt; Pushes the actor into scheduler.schedule, at actor.time.
scheduler.tick()      -&gt; Finds the next tick with actors scheduled, pops that list off of scheduler.schedule,
                         and iterates through the list, calling actor.act() on each actor.  Will retry an
                         actor's act() until it returns True.  Afterwards, it reschedules that actor with a call
                         to scheduler.push(actor).</t>
<t tx="peckj.20130927083040.3216"></t>
<t tx="peckj.20130927083040.3217"></t>
<t tx="peckj.20130927083040.3218">The following definitions are needed for the game to operate:

# Screen stuff
SCREEN_WIDTH
SCREEN_HEIGHT
LIMIT_FPS

# Map size
MAP_WIDTH
MAP_HEIGHT

# color scheme
color_dark_wall
color_light_wall
color_dark_ground
color_light_ground

# dungeon generation
ROOM_MAX_SIZE
ROOM_MIN_SIZE
MAX_ROOMS

# FOV stuff
FOV_ALGO
FOV_LIGHT_WALLS
TORCH_RADIUS

# Panel stuff
BAR_WIDTH
PANEL_HEIGHT
PANEL_Y

# Message Bar stuff
MSG_X
MSG_WIDTH
MSG_HEIGHT

# Inventory stuff
INVENTORY_WIDTH

# spells/scrolls/items
HEAL_AMOUNT
LIGHTNING_DAMAGE
LIGHTNING_RANGE
CONFUSE_NUM_TURNS
CONFUSE_RANGE
FIREBALL_DAMAGE
FIREBALL_RADIUS

# character advancement
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

# scheduler stuff
MAX_SCHEDULER_TICKS = 15
</t>
<t tx="peckj.20130927083040.3219">The following globals contain important game information:

player        -&gt; the player object (also in objects)
objects       -&gt; list of game objects on the current level
game_state    -&gt; a string representing the state of the game
  valid game_state values:
    'playing'
    'playing-waiting-for-input'
    'dead'
game_msgs     -&gt; a list of strings in the message buffer
dungeon_level -&gt; current level of the dungeon
stairs        -&gt; the stairs object (also in objects)
scheduler     -&gt; the scheduler object
key           -&gt; object representing keyboard events
mouse         -&gt; object representing mouse events
con           -&gt; off-screen console for the map portion of the interface
panel         -&gt; off-screen console for the information portion of the interface</t>
<t tx="peckj.20130927083040.3220">Tiles are representations of a cell of the game map.

# Fields

tile.blocked     -&gt; Boolean: True if tile blocks movement (i.e. walls)
tile.block_sight -&gt; Boolean: True if tile blocks sight
tile.explored    -&gt; Boolean: True if tile has been explored</t>
<t tx="peckj.20130927083040.3221">A Rect is a simple representation of a rectangle.  They're used to build rooms
in the map maker.

# Fields
rect.x1 -&gt; Upper left x
rect.y1 -&gt; Upper left y
rect.x2 -&gt; Lower right x
rect.y2 -&gt; Lower right y

# Methods
rect.center()              -&gt; Returns the center of the rectangle as a tuple (x, y)
rect.intersect(other_rect) -&gt; Returns True if rect intersects with other_rect
</t>
<t tx="peckj.20130927083040.3225"></t>
</tnodes>
</leo_file>
