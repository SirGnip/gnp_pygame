"""
Module with some simple actor-like objects.  Useful for debugging or simple graphic
work.  Currently, most of these actor's are simple geometric shapes with lifetimes.

TODO: have actors that mimic the functions in pygame.draw
"""
import pygame
from gnp_pygame import gnipMath


class LifetimeActor(object):
    def __init__(self, lifetime):
        self.lifetime_remaining = lifetime

    def step(self, time_delta):
        self.lifetime_remaining -= time_delta

    def can_reap(self):
        return self.lifetime_remaining <= 0.0

    def reap(self):
        self.lifetime_remaining = 0.0


class Dot(LifetimeActor):
    def __init__(self, position, color, lifetime):
        LifetimeActor.__init__(self, lifetime)
        self._position = position
        self._color = color

    def draw(self, surface):
        surface.set_at(self._position.AsIntTuple(), self._color)


class Circle(LifetimeActor):
    def __init__(self, position, radius, color, lifetime):
        LifetimeActor.__init__(self, lifetime)
        self._position = position
        self._radius = radius
        self._color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self._color, self._position.AsIntTuple(), self._radius)


class Line(LifetimeActor):
    def __init__(self, pos1, pos2, color, lifetime):
        LifetimeActor.__init__(self, lifetime)
        self._pos1 = pos1
        self._pos2 = pos2
        self._color = color

    def draw(self, surface):
        pygame.draw.line(surface, self._color, self._pos1.AsIntTuple(), self._pos1.AsIntTuple())


class Rect(LifetimeActor):
    def __init__(self, rect, color, lifetime):
        LifetimeActor.__init__(self, lifetime)
        self._rect = rect
        self._color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, self._rect)


class AlphaRect(object):
    """draw rectangle that has alpha"""
    def __init__(self, rect, color):
        self._rect = rect
        self._color = color # any way to use per-surface alpha? I think I'm using per-pixel alpha here
        self._surface = pygame.Surface(rect.size, pygame.SRCALPHA, 32)
        self._surface.fill(color)

    def step(self, time_delta):
        pass

    def draw(self, surface):
        surface.blit(self._surface, self._rect.topleft)

    def can_reap(self):
        return False

    def reap(self):
        pass


class GrowingCircle(LifetimeActor):
    """Growing/shrinking circle actor"""
    def __init__(self, position, starting_radius, ending_radius, color, lifetime):
        super(GrowingCircle, self).__init__(lifetime)
        self._position = position
        self._starting_radius = float(starting_radius)
        self._radius = starting_radius
        self._ending_radius = float(ending_radius)
        self._color = color
        self._total_lifetime = lifetime

    def step(self, time_delta):
        super(GrowingCircle, self).step(time_delta)
        u = float(self.lifetime_remaining) / self._total_lifetime
        self._radius = gnipMath.Lerp(self._ending_radius, self._starting_radius, u)

    def draw(self, surface):
        pygame.draw.circle(surface, self._color, self._position.AsIntTuple(), int(self._radius))


class PulseCircle(object):
    def __init__(self, pos, radiusAnimCurve, color, lifetime = 0.0):
        self._looping = bool(lifetime == 0.0)
        self._position = pos
        self._radius_anim_curve = radiusAnimCurve
        self._color = color
        self._lifetime_remaining = lifetime
        self._lifetime_elapsed = 0.0
        
    def step(self, time_delta):
        self._lifetime_remaining -= time_delta
        self._lifetime_elapsed += time_delta

    def draw(self, surface):
        radius = int(self._radius_anim_curve.Get(self._lifetime_elapsed))
        pygame.draw.circle(surface, self._color, self._position.AsIntTuple(), radius)
        
    def can_reap(self):
        if self._looping:
            return False
        else:
            return self._lifetime_remaining <= 0.0
    
    def reap(self):
        self._lifetime_remaining = 0.0
        
               
# TODO: Add a polyline actor
