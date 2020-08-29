"""
Emitter
* how long? how many?
    - burst -> # of particles (fires and goes away wieh all particles die)
    - infinite rate -> x spawns per sec (w/ start and stop from client)
    
* from where?
    - point
    - lineseg
    - rect
    - circle
    - attached to another object
    - animated
    - should I have all particles & other positions specified relative to the emitter position?  Yes!
    
* how does it look?
    - color -> fixed, random, random in range, random from given choices
    - lifetime -> constant, random range
    - type -> point, circle w/ radius, square, sprite
    
* what directions?
    - random within 360
    - constant (45deg)
    - random in range (direction w/ spread)
    
* what velocity?
    - constant
    - random in range
    
* what affects emitter after initial creation
    - animated (translation, rotation)
    - attached to other object's position/rotation
    
* what affects particles after being emitted
    - color/alpha changes (lerp between two colors)
    - affect velocity)
        - fields
            - turbulence
            - constant force (arbitrary vector, gravity)
            - black hole
            - vortex (rotational)
            - repulse from point
        - collision
            - axis, lines, boxes
        - drag/friction
    - lifetime
        - clip when outside of cir, rect
        - event on particle death
        - event on collision


TODO: Create a template that contains all of the components in it so that a
template can be assembled and reused to spawn lots of the same type of emitter.
The template class will have an EmitterFactory() function to create an emitter.
For the emitter components that have state (like cEmitterRate with the time
carryover and IsComplete), how do I split up logic and data across the template
and emitter?

Or, just ditch all this complexity of templates and make some util factory
functions gameside that create the emitters I want with the components
specified in the factory functions.

TODO: come up with way so that I can have an emitter that does its thing for a
given number of seconds and then stops and dies when its particles are gone.

OPTIMIZE: If it gets unweildy, see if I can make the code for the components
below more generic.  There is some redundant code where certain things are used
multiple times for different emitter values (constant values, random range of
values, choice from list, etc).

SPEED OPTIMIZATION:
I can't remember, but I seem to recall that if I run a long-running emitter
with *lots* of particles, it will "hitch" every few seconds.  My guess is this
is because of dynamic memory allocations/deallocations.  Particle objects
are created for each particle emitted and then destroyed when the particle
is done and is GC'ed.  So, I think the hitch is probably GC.  Instead of
dynamic particle allocations and using a growing/shrinking list, can I use
a static-sized list and allocate all particle slots up front and destroy
only when the emitter is destroyed.

How to do it:
- create a list and populate it with particle objects at emitter creation time
(the optimal size will need to be determined experimentally for each emitter type.)
Create some tools that allow me to create a large size and measure how much used/wasted
space there is (min/avg/max) values.
- can i use a tuple?  The size doesn't chnage but the objects inside do?
- Use this as a type of ring buffer. Have an index that cycles through the list.  It 
points to the slot where a new particle will be inserted.  After a particle is inserted,
the list is scanned from the current position to find the next empty slot.  If it gets
to the end, it starts over at the beginning (a ring buffer-ish datastructure).  This could
be a performance problem if I am always scanning over large chunks of used slots to find
an empty slot to create a new particle.  But, if the list is sized large enough and the
particle lifetimes are somewhat uniform, I can be pretty sure that the particles emitted early
have died off and all of their slots are open by the time the current index commes back
around to the beginning of the buffer again.
- this is the classic memory/speed tradeoff.  I'm probably gonna have wasted space,
but that will let me usually advance my index by one and rarely have a collision and have
to scan a big chunk of the list list looking for the next empty slot.
- For emitters with a known number of particles (emitter that spawns 50 particles at
start and just lets them die out wihout emitting any more... think of an explosion), you
can size the list to the exact number of particles you expect.  For continuously running
emitters, you need to run some experiments to see what hte optimal size is.
- How do I avoid/catch/handle the case where the buffer is actually full?
- What are pathological cases (particles with wildly differing lifetimes means there will
be more filled slots to step over.  But, the impact of this can be reduced by simply
making the buffer larger. :)  The memory/speed tradeoff again...
"""

from gnp_pygame import gnppygame
from gnp_pygame import gnipMath
import random
import pygame


##########
########## Classes that determine the emit Rate (delay) of an Emitter
class EmitterRate(object):
    def how_many(self, deltaTime):
        """override me"""
        assert False, 'EmitterRate is not meant to be instantiated'

    def is_complete(self):
        """override me"""
        assert False, 'EmitterRate is not meant to be instantiated'


class EmitterRate_Burst(EmitterRate):
    """fires all particles at creation time of emitter and then dies"""
    def __init__(self, num_particles):
        self._num_particles = num_particles
        self._is_complete = False
        
    def how_many(self, delta_time):
        self._is_complete = True
        return(self._num_particles)
        
    def is_complete(self):
        """the burst should only fire once"""
        return self._is_complete


class EmitterRate_DelayBase(EmitterRate):
    """This is a base class for subclasses that handle the emit rate as a delay between emits.
    Not meant to be instantiated."""
    def __init__(self):
        self._delta_carryover = 0.0
        
    def how_many(self, delta_time):
        """Determine how much time wasn't used to spawn "emit_count" particles.  Take that time and
        carry it over to apply to next frame.  This is so that if there are emit delays that
        are larger than one frame delta, this will still emit a particle every few frames.
        This also makes the number of emits more accurate than just doing:
           number = int(total_time / emit_delay)"""
        total_time = delta_time + self._delta_carryover
        emit_delay = self._get_delay()
        emit_count = int(total_time / emit_delay)
        self._delta_carryover = total_time - (emit_count * emit_delay)
        return emit_count
    
    def _get_delay(self):
        """override me"""
        assert False, 'EmitterRate_DelayBase is not meant to be instantiated'


class EmitterRate_DelayConstant(EmitterRate_DelayBase):
    """spawns particles at a constant rate"""
    def __init__(self, emit_delay):
        EmitterRate_DelayBase.__init__(self)
        self._emitDelay = emit_delay  # time between the spawn of each particle (0.25 will be 4 particles a second)

    def is_complete(self):
        """always returns False, because it never is complete"""
        return False

    def _get_delay(self):
        return self._emitDelay


class EmitterRate_DelayRange(EmitterRate_DelayBase):
    def __init__(self, range_lo, range_hi):
        EmitterRate_DelayBase.__init__(self)
        self._lo = range_lo
        self._hi = range_hi

    def is_complete(self):
        """always returns False, because it never is complete"""
        return False

    def _get_delay(self):
        return random.uniform(self._lo, self._hi)


class EmitterRate_DelayRangeWithLifetime(EmitterRate_DelayBase):
    """specify how long the emitter will emit for"""
    def __init__(self, range_lo, range_hi, emitter_lifetime):
        EmitterRate_DelayBase.__init__(self)
        self._lo = range_lo
        self._hi = range_hi
        self._emitter_lifetime_remaining = emitter_lifetime

    def how_many(self, delta_time):
        self._emitter_lifetime_remaining -= delta_time
        return EmitterRate_DelayBase.how_many(self, delta_time)

    def is_complete(self):
        return self._emitter_lifetime_remaining <= 0.0

    def _get_delay(self):
        return random.uniform(self._lo, self._hi)


##########
########## Classes that determine the initial Speed of particles (not velocity because there is no direction)
class EmitterSpeed:
    def get_speed(self):
        pass


class EmitterSpeed_Constant(EmitterSpeed):
    def __init__(self, speed):
        self._speed = speed
        
    def get_speed(self):
        return self._speed


class EmitterSpeed_Range(EmitterSpeed):
    def __init__(self, range_lo, range_hi):
        self._lo = range_lo
        self._hi = range_hi

    def get_speed(self):
        return random.uniform(self._lo, self._hi)


##########
########## Classes that determine the initial Direction of particles
class EmitterDirection:
    """return a normalized vector describing which direction the particle will fly"""
    def get_direction(self):
        """override me"""
        assert False, 'EmitterDirection is not meant to be instantiated'


class EmitterDirection_360(EmitterDirection):
    def get_direction(self):
        return gnipMath.cVector2.RandomDirection()


class EmitterDirection_Constant(EmitterDirection):
    def __init__(self, dir_vect):
        assert isinstance(dir_vect, gnipMath.cVector2), 'The dir argument must be a cVector2'
        self._dir = dir_vect.Normalize()
        
    def get_direction(self):
        return self._dir


class EmitterDirection_AngleWithSpread(EmitterDirection):
    def __init__(self, dir_angle, half_angle_spread):
        self._dir = dir_angle
        self._half_angle_spread = half_angle_spread
        
    def get_direction(self):
        return gnipMath.cVector2.RandomDirectionWithSpread(self._dir, self._half_angle_spread)


##########
########## Classes that determine the initial Lifetime of particles
class EmitterLifetime:
    def get_lifetime(self):
        """override me"""
        assert False, 'EmitterLifetime is not meant to be instantiated'


class EmitterLifetime_Constant(EmitterLifetime):
    def __init__(self, lifetime):
        self._lifetime = lifetime

    def get_lifetime(self):
        return self._lifetime


class EmitterLifetime_Range(EmitterLifetime):
    def __init__(self, range_lo, range_hi):
        self._lo = range_lo
        self._hi = range_hi

    def get_lifetime(self):
        return random.uniform(self._lo, self._hi)


##########
########## Classes that determine the initial Color of particles
class EmitterColor:
    def get_color(self):
        """override me"""
        assert False, 'EmitterColor is not meant to be instantiated'


class EmitterColor_Constant(EmitterColor):
    def __init__(self, color):
        self._color = color
        
    def get_color(self):
        return self._color


class EmitterColor_Choice(EmitterColor):
    def __init__(self, color_choices):
        """Pass in a tuple of colors to choose from."""
        assert isinstance(color_choices, tuple), 'The color choices to cEmitterColor_Choice must be passed in as a tuple'
        for idx, color in enumerate(color_choices):
            assert isinstance(color, (tuple, pygame.Color)), 'The items in the tuple passed to cEmitterColor_Choice must be tuples of RGB color values or instances of pygame.Color.  The item at index #%d is type: %s.' % (idx, type(color))
        self.colorChoices = color_choices
        
    def get_color(self):
##      print type(self.colorChoices)
##      print self.colorChoices
##      c = random.choice(self.colorChoices)
##      print(c)
##      print('-----')
##      return(c)
        return random.choice(self.colorChoices)


##########
########## Classes that define a field attached to the emitter
class EmitterField:
    def get_accel_vector(self, position, cur_vel):
        """override me"""
        assert False, 'cEmitterDirection is not meant to be instantiated'

class cEmitterField_Constant(EmitterField):
    def __init__(self, acceleration_vector):
        self._accel_vect = acceleration_vector
        
    def get_accel_vector(self, position, cur_vel):
        return self._accel_vect


class EmitterField_TrubulenceHACK(EmitterField):
    """This is just a temp version of the turbulence field.  This one isn't frame-rate independent."""
    def __init__(self, freq_percentage, magnitude):
        self._freq_percentage = freq_percentage
        self._magnitude = magnitude

    def get_accel_vector(self, position, cur_vel):
        dir_vect = gnipMath.cVector2.RandomDirection()
        if random.random() < self._freq_percentage:
            return dir_vect * self._magnitude
        else:
            return gnipMath.cVector2(0.0, 0.0)


class EmitterField_Drag(EmitterField):
    """Slows the particle down over its lifetime.  A value of 0.0 means no drag.  As
    the value increases, so does the drag."""
    def __init__(self, percent_per_second = 0.99):
        self._percent_per_second = percent_per_second

    def get_accel_vector(self, position, cur_vel):
        """implicitly converting velocity to acceleration here"""
        return -(cur_vel * self._percent_per_second)


class EmitterField_PointAttract(EmitterField):
    def __init__(self, attract_point, accel_magnitude, falloff_radius=None):
        """Can turn this into a "PointRepulse" if you provide a negative magnitude"""
        self._attract_point = attract_point
        self._accel_mag = accel_magnitude
        self._falloff_radius = falloff_radius

    def get_accel_vector(self, position, cur_vel):
        attract_dir = (self._attract_point - position).NormalizeSafe()
        if self._falloff_radius == None:
            return attract_dir * self._accel_mag
        else:
            assert self._falloff_radius > 0.0, 'The given falloff_radius (%f) was not greater than 0.0' % self._falloff_radius
            distance = (self._attract_point - position).Magnitude()
            if distance > self._falloff_radius:
                return gnipMath.cVector2(0.0, 0.0)
            else:
                multiplier = (self._falloff_radius - distance) / self._falloff_radius
                return attract_dir * (multiplier * self._accel_mag)


##########
########## Core classes
class Particle:
    def __init__(self, position, velocity, lifetime, color, size):
        self._position = position
        self._velocity = velocity
        self._lifetime_remaining = lifetime
        self._color = color
        self._size = size

    def can_reap(self):
        return self._lifetime_remaining <= 0.0
    
    def step(self, time_delta):
        assert not self.can_reap(), 'Should not be stepping a dead particle'
        self._position = self._position + (self._velocity * time_delta)
        self._lifetime_remaining -= time_delta
        if self._lifetime_remaining < 0.0:
            self._lifetime_remaining = 0.0

    def draw(self, surface):
        assert not self.can_reap(), 'Should not be drawing a dead particle'
        if self._size == 0:
            surface.set_at(self._position.AsIntTuple(), self._color)
        else:
            pygame.draw.circle(surface, self._color, self._position.AsIntTuple(), self._size)
        

class Emitter:
    """Object that spawns and manages individual particles"""
    def __init__(self, position, rate_obj, speed_obj, direction_obj, lifetime_obj, color_obj, size, field_obj=None):
        self._position = position
        self._particles = gnppygame.ActorList()
        
        self._rate_obj = rate_obj             # how often to spawn
        self._speed_obj = speed_obj           # initial speed (a speed, no direction)
        self._direction_obj = direction_obj   # initial direction (a direction, no speed)
        self._lifetime_obj = lifetime_obj     # starting lifetime for a particle
        self._color_obj = color_obj           # initial color
        self._start_size = size
        self._field_obj = field_obj           # field attached to emitter
        
        self._can_emit = True                 # controlled by start()/stop()

    def set_position(self, pos):
        self._position = pos
        
    def step(self, time_delta):
        assert not self.can_reap(), 'Should not be stepping a dead emitter'
        if self._can_emit:
            self._emit(time_delta)
        # update particle from field
        if self._field_obj:
            for p in self._particles:
                p._velocity += self._field_obj.get_accel_vector(p._position, p._velocity) * time_delta
        # step
        self._particles.step(time_delta)

    def draw(self, surface):
        assert not self.can_reap(), 'Should not be drawing a dead emitter'
        self._particles.draw(surface)
            
    def can_reap(self):
        """emitter is dead when it is done emitting particles and all living particles die off"""
        pending_particles = bool(len(self._particles))
        return not pending_particles and self._rate_obj.is_complete()

    def start(self):
        self._can_emit = True
        
    def stop(self):
        self._can_emit = False
        
    def _emit(self, time_delta):
        """Emit particles"""
        if not self._rate_obj.is_complete():
            for x in range(self._rate_obj.how_many(time_delta)):
                speed = self._speed_obj.get_speed()
                dir = self._direction_obj.get_direction()
                velocity = dir * speed # make a vector
                lifetime = self._lifetime_obj.get_lifetime()
                color = self._color_obj.get_color()
                p = Particle(self._position, velocity, lifetime, color, self._start_size)
                self._particles.append(p)
