import pygame
from gnp_pygame import gnipMath
import random
import os.path


########################################
######################################## General utilities
########################################
def rnd_point(xmax, ymax):
    x = random.randint(0, xmax)
    y = random.randint(0, ymax)
    return x, y


def rnd_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    a = 255
    return r, g, b, a


def random_no_repeat(items):
    """Iterator that chooses a random item from list without repeating a selection two times in a row"""
    # Note: Allowing random.choice to throw IndexError if "items" is empty
    last = random.choice(items)
    yield last
    while True:
        if len(items) == 1:
            last = items[0]
            yield last
        else:
            filtered = [item for item in items if item != last]
            last = random.choice(filtered)
            yield last


def cycle_through_items(items):
    """Iterator that returns items in order, cycling to front of list when done."""
    idx = 0
    while True:
        yield items[idx]
        idx += 1
        if idx >= len(items):
            idx = 0


########################################
######################################## Rect utilities
########################################
def clamp_point_to_rect(p, r):
    """Given a point, return it clamped to be inside the given rect.

        Note: The rect returned by get_surface().get_rect() is like ((0, 0), (648, 480)).  If
        you query the rect's "right" property, it will return 640 and if you query "bottom"
        it will return 480.  If you try to plot anything to those coordinates, they are obviously
        out of range.  If there is a rect with a width width of 1, it will contain 2 pixels.  Thus,
        if there is a rect with width of 640, it will contain 641 pixels.

        Thus, I reduce the right & bottom pixels by one to not have them fall on the rectangle
        boundaries of 640 & 480 (or whatever the resolution).

        Note: This might shed some more light on the issue above:
        r = Rect((0, 0), (640, 480))
        r.collidepoint((0, 0)) will return true (as expected)
        r.collidepoint((640, 480)) will return false (which seems a bit inconsistent since 0,0 is on
        the rect "edge" and still collides.  But, 640,480 is outside.)
        """
    return (
        gnipMath.Clamp(p[0], r.left, r.right - 1),
        gnipMath.Clamp(p[1], r.top, r.bottom - 1)
    )


def split_rect_horizontally(r, pieces):
    """NOTE: This doesn't quite do a 100% perfect job.  If the width of the
    given rect cant be evenly divided into the given number of pieces, there
    may be gaps inbetween the returned rects.
    Ex: <rect(0, 0, 8, 10)> divided into 3 pieces gives:
    <rect(0, 0, 2, 10)>
    <rect(2, 0, 2, 10)>
    <rect(5, 0, 2, 10)>
    At x=4, there is a gap
    """
    step = r.width / pieces # int math
    result = []
    for i in range(pieces):
        result.append(pygame.Rect(i * step + r.x, r.y, step, r.height))
    return result


def split_rect_vertically(r, pieces):
    """see documentation for SplitRectHoriz"""
    step = r.height / pieces # int math
    result = []
    for i in range(pieces):
        result.append(pygame.Rect(r.x, i * step + r.y, r.width, step))
    return result


########################################
######################################## Color utilities
########################################
# some color abbreviations
WHITE      = pygame.color.Color('white')
LIGHTGRAY  = pygame.color.Color('lightgray')
GRAY       = pygame.color.Color('gray')
DARKGRAY   = pygame.color.Color('darkgray')
BLACK      = pygame.color.Color('black')
IVORY      = pygame.color.Color('ivory')
MAROON     = pygame.color.Color('maroon')
RED        = pygame.color.Color('red')
GREEN      = pygame.color.Color('green')
BLUE       = pygame.color.Color('blue')
NAVYBLUE   = pygame.color.Color('navyblue')
CYAN       = pygame.color.Color('cyan')
MAGENTA    = pygame.color.Color('magenta')
YELLOW     = pygame.color.Color('yellow')
ORANGE     = pygame.color.Color('orange')
VIOLET     = pygame.color.Color('violet')
PURPLE     = pygame.color.Color('purple')
OLIVEDRAB  = pygame.color.Color('olivedrab')
BEIGE      = pygame.color.Color('beige')
BROWN      = pygame.color.Color('brown')
TAN        = pygame.color.Color('tan')
PINK       = pygame.color.Color('pink')
GOLD       = pygame.color.Color('gold')


########################################
######################################## Surface utilities
########################################

def dbg_print_surface_info(s, msg=''):
    print('Surface Info  ', msg)
    print('  Rect:      ', s.get_rect())
    print('  Alpha:     ', s.get_alpha())
    print('  BitSize:   ', s.get_bitsize())
    print('  ByteSize:  ', s.get_bytesize())
    print('  get_flags: ', s.get_flags())
    print('  get_pitch: ', s.get_pitch())
    print('  get_masks: ', s.get_masks())
    print('  get_shifts:', s.get_shifts())
    print('  get_losses:', s.get_losses())


def dbg_dump_surface(surface, subrect=None):
    """Debugging function that dumps the pixel info for a surface, (or portion of it)"""
    if not subrect:
        subrect = surface.get_rect()

    headers = [x for x in range(subrect.x, subrect.right)]
    headers = ['%8s' % num for num in headers]
    print('%4s %s' % ('', ' '.join(headers)))

    for y in range(subrect.y, subrect.bottom):
        pixs = []
        for x in range(subrect.x, subrect.right):
            clr = surface.get_at((x, y))
            pixs.append('%02x%02x%02x%02x' % tuple(clr))
        print('%4d' % y + ' ' + ' '.join(pixs))


########################################
######################################## Graphic utilities
########################################

class ScreenFader(object):
    def __init__(self, surf_size, color, length, start_alpha, end_alpha):
        assert 0 <= start_alpha <= 255, 'startAlpha of %d is invalid because it must be between 0-255' % start_alpha
        assert 0 <= end_alpha <= 255, 'endAlpha of %d is invalid because it must be between 0-255' % end_alpha
        assert length >= 0, 'Length must be equal or greater than zero.'
        self._color = color
        self._length = length
        self._start_alpha = start_alpha
        self._end_alpha = end_alpha
        self._fade_surf = pygame.Surface(surf_size)
        self._fade_surf.fill(color)
        self._fade_surf.set_alpha(self._start_alpha)
        self._elapsed_time = 0.0

    def draw(self, surface):
        surface.blit(self._fade_surf, (0, 0))

    def step(self, time_delta):
        """OPTIMIZE: can do an early out here to avoid the lerp and setting of alpha"""
        self._elapsed_time += time_delta
        new_alpha = gnipMath.LinInterp(self._start_alpha, self._end_alpha, gnipMath.Clamp(self._elapsed_time / self._length, 0.0, 1.0))
        self._fade_surf.set_alpha(new_alpha)

    def can_reap(self):
            return self._elapsed_time >= self._length


########################################
######################################## Prototype Particle System
########################################
class ParticleProto(object):
    """A simple prototype for a particle in a particle system"""
    def __init__(self, start_pos, velocity, lifetime, color):
        self._position = start_pos
        self._velocity = velocity
        self._lifetime_remaining = lifetime
        self._color = color

    def step(self, time_delta):
        assert not self.can_reap(), 'Should not be stepping a dead particle'
        self._position = self._position + (self._velocity * time_delta)
        self._lifetime_remaining -= time_delta
        if self._lifetime_remaining < 0.0:
            self._lifetime_remaining = 0.0
        
    def draw(self, surface):
        assert not self.can_reap(), 'Should not be drawing a dead particle'
        #pygame.display.get_surface().set_at(self._position.AsIntTuple(), self._color)
        pygame.draw.circle(surface, self._color, self._position.AsIntTuple(), 4)

    def can_reap(self):
        return (self._lifetime_remaining <= 0.0)


class ParticleSystemProto(object):
    """A simple particle system prototype.
    
    A color of None means to use a random color for each particle."""
    def __init__(self, start_pos, num_particles=100, lifetime_range=(0.1, 1.0), velocity_range=(0.1, 100.0), color=None):
        self._position = start_pos
        self._particles = []

        for count in range(num_particles):
            if color:
                self._particles.append(ParticleProto(self._position, gnipMath.cVector2.RandomDirection() * random.uniform(velocity_range[0], velocity_range[1]), random.uniform(lifetime_range[0], lifetime_range[1]), color))
            else:
                self._particles.append(ParticleProto(self._position, gnipMath.cVector2.RandomDirection() * random.uniform(velocity_range[0], velocity_range[1]), random.uniform(lifetime_range[0], lifetime_range[1]), rnd_color()))

    def step(self, time_delta):
        # deadParticles = []
        for particle in self._particles:
            if not particle.can_reap():
                particle.step(time_delta)

        ''' PERFORMANCE NOTE: I was previously deleting any dead particles out of the list the moment
        they died.  But, this would cause weird hitches in performance when particles started to die.
        I'm assuming this was because each time a particle was removed from the list, all memory
        caching, etc. was invalidated.  So, leaving that data structure as static as possible helps
        with performance.'''
        # deadParticles = []
        # for particle in self._particles:
        #     particle.step(time_delta)
        #     if particle.can_reap():
        #         deadParticles.append(particle)
        #
        # # delete dead particles
        # for particle in deadParticles:
        #     self._particles.remove(particle)

    def draw(self, surface):
        for particle in self._particles:
            if not particle.can_reap():
                particle.draw(surface)
            
    def can_reap(self):
        # BUG: can_reap isn't functioning because I don't remove the particles when they die
        return len(self._particles) == 0


########################################
######################################## Time Utilities
########################################

class TimerManager(object):
    """Manages timers that are set and calls the callbacks when the timer is up.

    Usage:
        Timers = cTimerManager()
        Timers.add(7, GlobalFunction)   # can use global functions as callbacks
        Timers.add(2.5, self.GotTimer)  # can use class member functions as callbacks

        Don't forget to call Timers.step(time_delta) each frame...
    """
    def __init__(self):
        self._elapsed_seconds = 0.0
        self._timers = []
        
    def add(self, timer_delay, callback):
        trigger_time = self._elapsed_seconds + timer_delay
        self._timers.append((trigger_time, callback))

    def step(self, time_delta):
        """OPTIMIZE: If their are a large number of timers, I could keep the timer list sorted
        in order of when they will be triggered.  This way, I can search the list for the expired
        timers, and the first non-expired timer I find I can stop looking thru the whole list."""
        self._elapsed_seconds += time_delta
        timers_to_del = []
        for timer in self._timers:
            if timer[0] < self._elapsed_seconds:
                timer[1]() # call callback
                timers_to_del.append(timer)
        # delete expired timers
        for t in timers_to_del:
            self._timers.remove(t)
            
    def dbg_print(self):
        for idx, timer in enumerate(self._timers):
            print('%d - %f -> %s' % (idx, timer[0], timer[1].__name__))


########################################
######################################## Managers
########################################

class FontManager(object):
    """A simple class used to manage Font objects and provide a simple way to use
    them to draw text on any surface.

    Directly import this file to use the class, or run this file from the
    command line to see a trivial sample."""
    def __init__(self, list_of_font_names_and_sizes_as_tuple):
        """Pass in a tuple of 2-item tuples.  Each 2-item tuple is a fontname/size pair.
        To use the default font, pass in a None for the font name.  Font objects are
        created for each of the pairs and can then be used to draw text with the
        draw() method below.
        
        Ex: fontMgr = cFontManager(((None, 24), ('arial', 18), ('arial', 24), ('courier', 12), ('papyrus', 50)))

        TODO: add support for bold & italics"""
        self._font_dict = {}
        for pair in list_of_font_names_and_sizes_as_tuple:
            assert len(pair) == 2, 'Pair must be composed of a font name and a size  Ex:(\'arial\', 24)'
            if pair[0]:
                font_full_file_name = pygame.font.match_font(pair[0])
                assert font_full_file_name, 'Font: %s Size: %d is not available.' % pair
            else:
                font_full_file_name = None # use default font
            self._font_dict[pair] = pygame.font.Font(font_full_file_name, pair[1])

    def draw(self, surface, font_name, size, text, rect_or_pos_to_draw_to, color, align_horiz='left', align_vert='top', antialias=False):
        """draw text with the given parameters on the given surface.
        
        surface - Surface to draw the text onto.
        
        fontName - Font name that identifies what font to use to draw the text.
        This font name must have been specified in the cFontManager 
        
        rectOrPosToDrawTo - Where to render the text at.  This can be a 2 item tuple
        or a Rect.  If a position tuple is used, the align arguments will be ignored.
        
        color - Color to draw the text with.
        
        alignHoriz - Specifies horizontal alignment of the text in the
        rectOrPosToDrawTo Rect.  If rectOrPosToDrawTo isn't a Rect, the alignment is
        ignored.
        
        alignVert - Specifies vertical alignment of the text in the rectOrPosToDrawTo
        Rect.  If rectOrPosToDrawTo isn't a Rect, the alignment is ignored.

        antialias - Whether to draw the text anti-aliased or not."""
        pair = (font_name, size)
        assert pair in self._font_dict, 'Font: %s Size: %d is not available in cFontManager.' % pair
        font_surf = self._font_dict[(font_name, size)].render(text, antialias, color)
        if isinstance(rect_or_pos_to_draw_to, tuple):
            surface.blit(font_surf, rect_or_pos_to_draw_to)
        elif isinstance(rect_or_pos_to_draw_to, pygame.Rect):
            font_rect = font_surf.get_rect()
            # align horiz
            if align_horiz == 'center':
                font_rect.centerx = rect_or_pos_to_draw_to.centerx
            elif align_horiz == 'right':
                font_rect.right = rect_or_pos_to_draw_to.right
            else:
                font_rect.x = rect_or_pos_to_draw_to.x  # left
            # align vert
            if align_vert == 'center':
                font_rect.centery = rect_or_pos_to_draw_to.centery
            elif align_vert == 'bottom':
                font_rect.bottom = rect_or_pos_to_draw_to.bottom
            else:
                font_rect.y = rect_or_pos_to_draw_to.y  # top
                
            surface.blit(font_surf, font_rect)


class AudioManager(object):
    def __init__(self, audio_directory):
        """load any *.wav or *.ogg files in given directory"""
        self._enabled_sfx = True
        self._enabled_music = True
        self._obj_dict = {}
        self._group_dict = {}
        print(("Loading audio from directory: %s (cwd: %s)" % (audio_directory, os.getcwd())))
        files = os.listdir(audio_directory)
        for fname in files:
            full_path_name = os.path.join(audio_directory, fname)
            assert os.path.exists(full_path_name), 'The given file (%s) does not exist.' % full_path_name
            if os.path.isfile(full_path_name):
                filebasename = os.path.splitext(os.path.basename(fname))[0]  # filename without path or extension
                self._obj_dict[filebasename] = pygame.mixer.Sound(full_path_name)
        assert len(self._obj_dict.keys()) > 0, 'cAudioManager did not find any sounds to load from %s' % audio_directory

    def enable_sfx(self, is_enabled):
        self._enabled_sfx = is_enabled

    def enable_music(self, is_enabled):
        self._enabled_music = is_enabled
        
    # Sound object Adapters (design pattern) around the pygame.mixer.Sound class
    def play(self, tag, loops=0, maxtime=0):
        if self._enabled_sfx:
            assert tag in self._obj_dict, 'Sound Manager does not have a sound loaded with the tag %s' % tag
            return self._obj_dict[tag].play(loops, maxtime)
        else:
            return None

    def stop(self, tag):
        if self._enabled_sfx:
            assert tag in self._obj_dict, 'Sound Manager does not have a sound loaded with the tag %s' % tag
            self._obj_dict[tag].stop()

    def fadeout(self, tag, time):
        if self._enabled_sfx:
            assert tag in self._obj_dict, 'Sound Manager does not have a sound loaded with the tag %s' % tag
            self._obj_dict[tag].fadeout(time)

    def set_volume(self, tag, volume):
        if self._enabled_sfx:
            assert tag in self._obj_dict, 'Sound Manager does not have a sound loaded with the tag %s' % tag
            assert 0.0 >= volume <= 1.0, 'Can not set out of range volume (f) to %s' % (volume, tag)
            self._obj_dict[tag].set_volume(volume)

    def get_volume(self, tag):
        if self._enabled_sfx:
            assert tag in self._obj_dict, 'Sound Manager does not have a sound loaded with the tag %s' % tag
            return self._obj_dict[tag].get_volume()
        else:
            return 0.0
    ##### end of Sound class Adapters

    def add_group(self, group_key, sound_key_tuple):
        assert group_key not in self._group_dict, 'Sound Manager already has a Group with the key %s' % group_key
        assert len(sound_key_tuple) > 0, 'Sound Manager expects a non-empty tuple when creating a Group'
        for key in sound_key_tuple:
            assert key in self._obj_dict, 'Sound Manager can not create a Group with a sound key (%s) that does not exist' % key
        self._group_dict[group_key] = sound_key_tuple

    def play_group(self, group_key):
        assert group_key in self._group_dict, 'Sound Manager does not have a Group with the key: %s.' % group_key
        self.play(random.choice(self._group_dict[group_key]))

    @staticmethod
    def load_music(filename):
        # NOTE: I couldn't get mp3's to work.  I got an .ogg, .it and a .s3m working.  Didn't do too much more testing.
        assert os.path.exists(filename), 'The given file (%s) does not exist.' % filename
        pygame.mixer.music.load(filename)

    def play_music(self, loops=0):
        if self._enabled_music:
            pygame.mixer.music.play(loops)

    def pause(self):
        pygame.mixer.pause()

    @staticmethod
    def get_all_channels():
        num = pygame.mixer.get_num_channels()
#        print 'channels:', num
        channels = []
        for i in range(num):
            chan = pygame.mixer.Channel(i)
#            print '%d - %f %s' % (i, chan.get_volume(), chan)
            channels.append(chan)
        return channels
            
    def set_master_volume(self, volume):
        channels = self.get_all_channels()
        for chan in channels:
            chan.set_volume(volume)
        pygame.mixer.music.set_volume(volume)       


########################################
######################################## Actor/Scene
########################################

class Actor(object):
    """This is a template for what Actor-like objects should look like.
    I could derive all my actors from this class, but I'm just relying on
    duck-typing so far.  This class is here mostly as an example of what
    Actor-like objects should look like."""
    def __init__(self):
        assert False, 'Can not instantiate a cActor'
        
    def step(self, time_delta):
        pass
    
    def draw(self, surface):
        pass
    
    def can_reap(self):
        """Can this actor be destroyed?"""
        return False

    def reap(self):
        """Marks this actor so that it can be reaped the next time possible.
        
        This method is not necessary for most Actor-like objects.  But, it is a
        common addtion if an Actor's lifetime needs to be cut short from an outside
        client."""
        pass

        
class ActorList(list):
    """Design goal of cActorLists:  easy access to individual items with the auto step/draw/Reap
    feature thrown in.  It is intended that a game would have multiple cActorLists.  This is a
    simple tool that can be used in many different nimble ways (at least more nimble than my
    original implementation of cScene.
    
    I originally created a monolithic cScene that each game would have one instance of.  When actors
    were added to this, they would get step() and draw() called.  But, I would then have to have other lists
    external to cScene for other game operations (colliding projectiles with ships).  This would mean
    that when cScene would remove an actor from its internal list, the actor wouldn't get GC'ed because
    there were other references to the actor out in the wild.  So, I didn't want to have to go thru
    these external lists and manually clean up dead actors.  If I always use cActorLists, the dead
    actors will clean themselves up.  Now, the one issue I can think of is that if I need to uniquely
    identify a specific object in a list, I'll be tempted to do it by index.  But, when an actor gets
    reaped from the list, the index will be off.  So, in this not-so-common case, I'll have to come
    up with a different way to identifying this object."""
    def step(self, time_delta):
        """NOTE: Just because this class removes an actor from its list does not mean that
        actor will immediately be destroyed.  There can be other objects in the game
        that are still holding references to it.  So, this is not a guarantee the actor
        will be destroyed, just that it won't get step() and draw() called for it."""
        actors_to_delete = []
        for actor in self:
            actor.step(time_delta)
            if actor.can_reap():
                actors_to_delete.append(actor)
        for actor_to_del in actors_to_delete:
            self.remove(actor_to_del)

    def draw(self, surface):
        for actor in self:
            actor.draw(surface)

    def reap(self):
        for actor in self:
            actor.reap()
        del self[:]


## cScene is DEPRECATED in favor of using individual cActorList's.
##  
##class cScene:
##  '''This class assumes the objects it stores are Actor-like objects.  See the
##  sample cActor class above.'''
##  def __init__(self, numberOfLayers):
##      self._numLayers = numberOfLayers
##      self._layersOfActors = tuple([[] for x in range(self._numLayers)]) # make this a tuple, assuming a tuple will be faster than a list
##
##  def add(self, actor, layerNumber):
##      '''TODO: Add an assert so the same actor doesn't get added twice'''
##      assert layerNumber >= 0 and layerNumber < self._numLayers, 'Layer number must be between %d-%d' % (0, self._numLayers - 1)
##      self._layersOfActors[layerNumber].append(actor)
##
##  def step(self, time_delta):
##      '''Layers are stepped in order by layer number.  This is not necessary, but it
##      is just the way it currently happens.
##      NOTE: Just because the scene removes an actor from its list does not mean that
##      actor will immediately be destroyed.  There can be other objects in the game
##      that are still holding references to it.  So, this is not a guarantee the actor
##      will be destroyed, just that it won't get step() and draw() called for it.'''
##      for layer in self._layersOfActors:
##          actorsToDelete = []
##          for actor in layer:
##              actor.step(time_delta)
##              if actor.can_reap():
##                  actorsToDelete.append(actor)
##          for actorToDel in actorsToDelete:
##              layer.remove(actorToDel)
##                      
##  def dbg_print(self):
##      print '-----cScene.dbg_print-----'
##      for layerIdx, layer in enumerate(self._layersOfActors):
##          print('%d actors in layer %d' % (len(layer), layerIdx))
##
##  def draw(self, surface):
##      '''The layers are drawn in order of the layer number.  Layer 0 is drawn first
##      and will be the background.  The largest layer number will be the foreground.'''
##      for layer in self._layersOfActors:
##          for actor in layer:
##              actor.draw(surface)


########################################
######################################## Others
########################################
        
class FrameTimer(object):
    """Used to calculate frame deltas"""
    TICKS_PER_SEC = 1000.0
    
    def __init__(self):
        self.__ticks = 0
        self.__start_time = pygame.time.get_ticks()
        self.__last_time = self.__start_time

    def tick(self):
        """returns delta in seconds"""
        self.__ticks += 1
        cur_time = pygame.time.get_ticks()
        delta = (cur_time - self.__last_time) / self.TICKS_PER_SEC
        self.__last_time = cur_time
        return delta

    def get_total_time(self):
        """returns total time the timer has been running, in seconds"""
        return (self.__last_time - self.__start_time) / self.TICKS_PER_SEC

    def get_total_ticks(self):
        return self.__ticks

    def get_total_fps(self):
        """returns Frames Per Second for the entire time the timer has been running"""
        assert self.get_total_time() > 0, 'Can not calculate FPS until some time has elapsed'
        return self.__ticks / self.get_total_time()


class Stopwatch(object):
    """Used to time how long something takes"""
    _TICKS_PER_SEC = 1000.0

    def __init__(self):
        self.reset()

    def reset(self):
        self._start_time = pygame.time.get_ticks()

    def get_elapsed(self):
        """Return elapsed seconds"""
        return (pygame.time.get_ticks() - self._start_time) / self._TICKS_PER_SEC


class Joy(object):
##  # values for XBox360 joystick
##  Joy1AxisX = 0
##  Joy1AxisY = 1
##  Joy2AxisX = 4
##  Joy2AxisY = 3
    # values for PS2 SuperDualBoxPro
    JOY1AXIS_X = 0
    JOY1AXIS_Y = 1
    JOY2AXIS_X = 2
    JOY2AXIS_Y = 3

    @staticmethod
    def joy_factory(id=0):
        print('# of joysticks %d' % pygame.joystick.get_count())
        if id > (pygame.joystick.get_count() - 1):
            return None
        else:
            return Joy(id)

    def __init__(self, id=0):
        assert id < pygame.joystick.get_count(), 'Trying to create a joystick that does not exit: ID: %d' % id
        self._joy = pygame.joystick.Joystick(id)
        self._joy.init()
        self._deadzone = 0.15
        print('Found joystick id:%d name:%s numButtons:%d numAxes:%d numHats:%s' % (
            self._joy.get_id(),
            self._joy.get_name(),
            self._joy.get_numbuttons(),
            self._joy.get_numaxes(),
            self._joy.get_numhats()))
        self._map_buttons()

    def _map_buttons(self):
        joy = self._joy
        if joy.get_name() == 'ZD-V' and joy.get_numbuttons() == 13:
            print('Buttons mapped on id:%d as ZD-V "red"' % joy.get_id())
            self.btn_face_left = 3
            self.btn_face_right = 1
            self.btn_face_up = 0
            self.btn_face_down = 2
            self.btn_shoulder_left1 = 4
            self.btn_shoulder_left2 = 6
            self.btn_shoulder_right1 = 5
            self.btn_shoulder_right2 = 7
            self.btn_hat_left = None
            self.btn_hat_right = None
            self.btn_hat_up = None
            self.btn_hat_down = None
        elif joy.get_name() == 'ZD-V' and joy.get_numbuttons() == 15:
            print('Buttons mapped on id:%d as ZD-V "purple"' % joy.get_id())
            self.btn_face_left = 3
            self.btn_face_right = 1
            self.btn_face_up = 4
            self.btn_face_down = 0
            self.btn_shoulder_left1 = 6
            self.btn_shoulder_left2 = 8
            self.btn_shoulder_right1 = 7
            self.btn_shoulder_right2 = 9
            self.btn_hat_left = None
            self.btn_hat_right = None
            self.btn_hat_up = None
            self.btn_hat_down = None
        elif joy.get_name() == 'Controller (ZD Game For Windows)' and joy.get_numbuttons() == 10:
            print('Buttons mapped on id:%d as ZD Game "blue"' % joy.get_id())
            self.btn_face_left = 2
            self.btn_face_right = 1
            self.btn_face_up = 3
            self.btn_face_down = 0
            self.btn_shoulder_left1 = 4
            self.btn_shoulder_left2 = None
            self.btn_shoulder_right1 = 5
            self.btn_shoulder_right2 = None
            self.btn_hat_left = None
            self.btn_hat_right = None
            self.btn_hat_up = None
            self.btn_hat_down = None
        elif joy.get_name() == 'USB Joystick          ':
            print('Buttons mapped on id:%d as USB Joystick' % joy.get_id())
            self.btn_face_left = 3
            self.btn_face_right = 1
            self.btn_face_up = 0
            self.btn_face_down = 2
            self.btn_shoulder_left1 = 4
            self.btn_shoulder_left2 = 6
            self.btn_shoulder_right1 = 5
            self.btn_shoulder_right2 = 7
            self.btn_hat_left = None
            self.btn_hat_right = None
            self.btn_hat_up = None
            self.btn_hat_down = None
        else:
            print('Buttons mapped on id:%d as default/PS2' % joy.get_id())
            self.btn_face_left = 3
            self.btn_face_right = 1
            self.btn_face_up = 0
            self.btn_face_down = 2
            self.btn_shoulder_left1 = 6
            self.btn_shoulder_left2 = 4
            self.btn_shoulder_right1 = 7
            self.btn_shoulder_right2 = 5
            self.btn_hat_left = 15
            self.btn_hat_right = 13
            self.btn_hat_up = 12
            self.btn_hat_down = 14

    def QueryAxisStart(self):
        """call when you want to start querying the joystick for an axis"""
        self._query_num_axes = self._joy.get_numaxes()
        self._query_axis_ranges = [[None, None] for x in range(self._query_num_axes)] # [[min, max], [min, max], etc...]
        self.query_axis_step()
        
    def query_axis_step(self):
        """call each tick"""
        for axis_id in range(self._query_num_axes):
            val = self._joy.get_axis(axis_id)
            # min
            if self._query_axis_ranges[axis_id][0] is not None:
                if val < self._query_axis_ranges[axis_id][0]:
                    self._query_axis_ranges[axis_id][0] = val
            else:
                self._query_axis_ranges[axis_id][0] = val
            # max
            if self._query_axis_ranges[axis_id][1] is not None:
                if val > self._query_axis_ranges[axis_id][1]:
                    self._query_axis_ranges[axis_id][1] = val
            else:
                self._query_axis_ranges[axis_id][1] = val
                
    def query_axis_end_and_get_id(self):
        """Returns the id of the axis that has moved most."""
        self.query_axis_step()
        best_axis_id = None
        largest_spread = 0
        for axis_id in range(self._query_num_axes):
            spread = self._query_axis_ranges[axis_id][1] - self._query_axis_ranges[axis_id][0]
            if best_axis_id is None:
                best_axis_id = axis_id
                largest_spread = spread
            else:
                if spread > largest_spread:
                    best_axis_id = axis_id
                    largest_spread = spread
        assert best_axis_id is not None, 'Did not find a suitable axis ID when querying all axes of the joystick'
        return best_axis_id
        
    def __del__(self):
        if self._joy:
            self._joy = None
            
    def is_valid(self):
        if self._joy:
            return True
        else:
            return False

    def set_deadzone(self, deadzone):
        self._deadzone = deadzone

    def get_stick1_vector(self):
        v = gnipMath.cVector2(self._joy.get_axis(self.JOY1AXIS_X), self._joy.get_axis(self.JOY1AXIS_Y))
        if v.Magnitude() < self._deadzone:
            return gnipMath.cVector2()
        else:
            return v

    def get_stick2_vector(self):
        v = gnipMath.cVector2(self._joy.get_axis(self.JOY2AXIS_X), self._joy.get_axis(self.JOY2AXIS_Y))
        if v.Magnitude() < self._deadzone:
            return gnipMath.cVector2()
        else:
            return v
        
    def get_button(self, button_id):
        if self._joy:
            return self._joy.get_button(button_id)

    def received_button_event(self, button_id):
        """This seems a bit of a hacky way to do this.  This requires the joystick to
        continually poll for this event every step, otherwise this event will be lost."""
        if self._joy:
            result = False
            events = pygame.event.get(pygame.JOYBUTTONDOWN)
            for e in events:
                if self._joy.get_id() == e.joy and button_id == e.button:
                    result = True
            return result
        else:
            return False


########################################
######################################## Game framework
########################################

class Game(object):
    ##### PUBLIC
    def __init__(self, caption='PyGame Game', screen_dimensions=(800, 600), fullscreen=False):
        """screenDimensions should be a tuple like (640, 480)"""
        pygame.init()
        if fullscreen:
            pygame.display.set_mode(screen_dimensions, pygame.FULLSCREEN)
            pygame.mouse.set_visible(False) # hide the mouse cursor
        else:
            pygame.display.set_mode(screen_dimensions)
        pygame.display.set_caption(caption)
        self._frame_timer = FrameTimer()
        self._request_exit = False

        # only allow the QUIT and JOYBUTTONDOWN events on the input queue
        pygame.event.set_allowed(None) # disallow all events from the queue
        pygame.event.set_allowed((pygame.QUIT, pygame.JOYBUTTONDOWN))

    def step(self, time_delta):
        """intended to be overridden by client"""
        pass

    def request_exit(self):
        self._request_exit = True
        
    def run_game_loop(self):
        self._frame_timer.tick() # this prevents a long delta from getting passed the first frame
        while not self._request_exit:
            delta = self._frame_timer.tick()
            self.base_input()
            self.base_step(delta)
            # makes sure app doesn't freeze by touching the event queue.  Also, by
            # clearing it, this prevents the queue from filling up (127 events) and
            # silently not accepting any more events.
# try removing this because it seems to eat up the JOYBUTTONDOWN events that I'm trying to capture on the queue
#          pygame.event.clear() (not needed because of pygame.event.peek in base_input?)

    def get_screen_rect(self):
        """Get a rect that defines the boundaries of the screen.
        Note: The rect returned by get_surface().get_rect() is ((0, 0), (648, 480)).  If
        you query the rect's "right" property, it will return 640 and if you query "bottom"
        it will return 480.  If you try to plot anything to those coordinates, they are obviously
        out of range.  If there is a rect with a width width of 1, it will contain 2 pixels.  Thus,
        if there is a rect with width of 640, it will contain 641 pixels."""
        r = pygame.display.get_surface().get_rect()
        return r

    def base_input(self):
        """Do not override. Not meant to be called by child or client"""
        if pygame.event.peek(pygame.QUIT):
            self.request_exit()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.request_exit()
        
    def base_step(self, frame_delta):
        """Do not override. Not meant to be called by child or client"""
        self.step(frame_delta) # call client update hook


class GameWithStates(Game):
    ##### PUBLIC
    def __init__(self, caption='PyGame Game', screen_dimensions=(640, 480), fullscreen=False):
        # NOTE: Seems like on one machine I tested it on, fullscreen is a bit offset when in resolutions under 1024x768
        Game.__init__(self, caption, screen_dimensions, fullscreen)
        self.__state = None
        self.__pending_state = None

    def change_state(self, new_state):
        assert self.__pending_state is None, 'Trying to change to a new state when there is already a change_state pending.'
        self.__pending_state = new_state

    def step(self, time_delta):
        """State change is deferred until the end of the step so that a state can complete all its
        processing before the new state takes over."""
        if self.__state:
            self.__state.step(time_delta)
        else:
            # TODO: Currently, the initial state of an application will go thru step() once without a current state
            print('WARNING: skipping step because there is no state')
        self._do_state_change()

    def _do_state_change(self):
        if self.__pending_state:
            # print 'Switching from %s to %s' % (self.__state.__class__.__name__, self.__pendingState.__class__.__name__)
            self.__state = self.__pending_state
            self.__pending_state = None
            self.__state.begin_state()


class GameState(object):
    def __init__(self, owner):
        self.__owner = owner

    def begin_state(self):
        """meant to be overridden by clients
        
        Do not override the __init__ method in states.  Do any initialization in this begin_state
        method.  This is so that the state's initialization can be under cGameWithStates's control.  Previously,
        I relied on the states __init__ method, but the new states __init__ was called before the old state's
        step() was completed causing things to happen out of expected order.  Using begin_state() for state
        initialization allows things to happen in this expected order:
            state 1's Begin State is called
            state 1's step() is called
            state 1's step() completes
            state switches to state 2
            state 2's begin_state() is called
            state 2's step() is called
            etc...
        """
        pass
    
    def owner(self):
        return self.__owner
    
    def change_state(self, new_state):
        assert self.__owner, 'State must have an owner'
        self.__owner.change_state(new_state)

    def step(self, time_delta):
        """override me"""
        pass


########################################
######################################## Demos/tests
########################################

class DemoGame(GameWithStates):
    def __init__(self):
        # call parent ctor
        GameWithStates.__init__(
                self,
                'PygameUtils Demo',
                (640, 480),
                False)
        
        # set initial state
        self.change_state(DemoFontState(self))
        self.font_mgr = FontManager((('arial', 16), ('arial', 48)))
        pygame.event.set_allowed((pygame.QUIT, pygame.KEYDOWN))
        
    def step(self, time_delta):
        GameWithStates.step(self, time_delta) # step the parent game class last because it can trigger a state transition

    def draw_title(self, msg):
        self.font_mgr.draw(pygame.display.get_surface(), 'arial', 48, msg, self.get_screen_rect(), BLUE, 'center', 'center', True)
        self.draw_spacebar_message()
        
    def draw_spacebar_message(self):
        self.font_mgr.draw(pygame.display.get_surface(), 'arial', 16, 'Press spacebar to continue...', self.get_screen_rect(), BLUE, 'center', 'bottom', True)

    def hit_spacebar(self):
        spacebar_down_events = [event for event in pygame.event.get() if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE]
        return bool(spacebar_down_events)


class DemoFontState(GameState):
    def begin_state(self):
        # a font of None means to use the default font
        self.font_mgr = FontManager(((None, 24), (None, 48), ('arial', 24)))

    def step(self, time_delta):
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))

        self.font_mgr.draw(screen, None, 48, 'Default font, 48', (0, 50), WHITE)
        self.font_mgr.draw(screen, None, 24, 'Default font, 24', (0, 0), WHITE)

        rect = pygame.Rect(0, 100, 640, 60)
        pygame.draw.rect(screen, GRAY, rect)
        self.font_mgr.draw(screen, 'arial', 24, 'Arial 24 top left', rect, WHITE, 'left', 'top')
        rect.top += 75
        
        pygame.draw.rect(screen, GRAY, rect)
        self.font_mgr.draw(screen, 'arial', 24, 'Arial 24 centered', rect, WHITE, 'center', 'center')
        rect.top += 75

        pygame.draw.rect(screen, GRAY, rect)
        self.font_mgr.draw(screen, 'arial', 24, 'Arial 24 bottom right', rect, WHITE, 'right', 'bottom')
        rect.top += 75

        pygame.draw.rect(screen, GRAY, rect)
        self.font_mgr.draw(screen, 'arial', 24, 'Arial 24 left center, anti-aliased', rect, WHITE, 'left', 'center', True)
        rect.top += 75

        pygame.display.update()
        if self.owner().hit_spacebar():
            self.change_state(DemoJoystickState(self.owner()))
            

class DemoJoystickState(GameState):
    def begin_state(self):
        self.joys = []
        self.joys.append(Joy.joy_factory(0))
        self.joys.append(Joy.joy_factory(1))

        # Temp Axis Query test
        self.timer_mgr = TimerManager()
        self.query_start()

    def query_start(self):
        if self.joys[0]:
            self.joys[0].QueryAxisStart()
            self.timer_mgr.add(3.0, self.query_end)

    def query_end(self):
        print('You moved Axis ID: %d' % self.joys[0].query_axis_end_and_get_id())
        self.query_start()
        
    def step(self, time_delta):
        self.timer_mgr.step(time_delta)
        if self.joys[0]:
            self.joys[0].query_axis_step()
        
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 64))

        self.owner().draw_title('Joystick Test')

        ypos = 75
        for joy in self.joys:
            if joy:
                for buttonId in range(10):
                    if joy.get_button(buttonId):
                        pygame.draw.circle(screen, RED, (buttonId * 40 + 50, ypos), 15)
                stickCenter1 = gnipMath.cVector2(100, ypos)
                stickCenter2 = gnipMath.cVector2(540, ypos)
                stickVect1 = joy.get_stick1_vector() * 50.0
                stickVect2 = joy.get_stick2_vector() * 50.0
                pygame.draw.line(screen, WHITE, stickCenter1.AsIntTuple(), (stickCenter1 + stickVect1).AsIntTuple(), 2)
                pygame.draw.line(screen, WHITE, stickCenter2.AsIntTuple(), (stickCenter2 + stickVect2).AsIntTuple(), 2)
            ypos += 100
            
        pygame.display.update()
        if self.owner().hit_spacebar():
            self.change_state(DemoScreenFader(self.owner()))


class DemoScreenFader(GameState):
    def begin_state(self):
        self.fader = None
        self.fade_state = 0
        
    def step(self, time_delta):
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        self.owner().draw_title('ScreenFader Test')
        
        if not self.fader:
            if self.fade_state == 0:
                self.fader = ScreenFader(screen.get_size(), BLUE, 0.3, 0, 255)
            elif self.fade_state == 1:
                self.fader = ScreenFader(screen.get_size(), BLUE, 0.5, 255, 0)
            elif self.fade_state == 2:
                self.fader = ScreenFader(screen.get_size(), WHITE, 2, 0, 255)
            elif self.fade_state == 3:
                self.fader = ScreenFader(screen.get_size(), WHITE, 3, 255, 0)
            self.fade_state = (self.fade_state + 1) % 4
            
        self.fader.step(time_delta)
        self.fader.draw(screen)
        if self.fader.can_reap():
            self.fader = None

        pygame.display.update()
        if self.owner().hit_spacebar():
            self.change_state(DemoTimerManager(self.owner()))


class DemoTimerManager(GameState):
    def begin_state(self):
        self.timer_mgr = TimerManager()
        self.timer_mgr.add(1.0, self.timer_fired)
        self.display_stuff = True
        
    def step(self, time_delta):
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        if self.display_stuff:
            self.owner().draw_title('TimerManager Test')
        self.timer_mgr.step(time_delta)
        
        pygame.display.update()
        if self.owner().hit_spacebar():
            self.change_state(DemoParticleSystemProto(self.owner()))

    def timer_fired(self):
        print('timer fired after 1 second...')
        self.timer_mgr.add(1.0, self.timer_fired)
        self.display_stuff = not self.display_stuff


class DemoParticleSystemProto(GameState):
    def begin_state(self):
        self.timer_mgr = TimerManager()
        self.emitter = None
        self.make_new_emitter()
        
    def step(self, time_delta):
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        self.owner().draw_title('ParticleSystemProto Test')

        self.emitter.step(time_delta)
        self.timer_mgr.step(time_delta)
        self.emitter.draw(screen)
        
        pygame.display.update()
        if self.owner().hit_spacebar():
            self.change_state(DemoAudioState(self.owner()))

    def make_new_emitter(self):
        self.emitter = ParticleSystemProto(gnipMath.cVector2(320, 240))
        self.timer_mgr.add(2.0, self.make_new_emitter)


class DemoAudioState(GameState):
    def begin_state(self):
        self.timer_mgr = TimerManager()
        self.add_timer()

        print('starting to load')
        self.audio_mgr = AudioManager('sounds')
        print('done loading')
        self.audio_mgr.play('ARROW')

    def step(self, time_delta):
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        self.timer_mgr.step(time_delta)
        self.owner().draw_title('AudioManager Test')

        pygame.display.update()
        if self.owner().hit_spacebar():
            self.owner().request_exit()

    def add_timer(self):
        self.timer_mgr.add(2.0, self.timer_fired)

    def timer_fired(self):
        self.audio_mgr.play('LASER')
        self.add_timer()


if __name__ == '__main__':
    game = DemoGame()
    game.run_game_loop()
