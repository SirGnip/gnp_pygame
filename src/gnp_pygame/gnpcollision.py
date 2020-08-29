# BILLIARD BALL COLLISION
# See http://www.gamasutra.com/features/20000516/lander_01.htm for discussion & equations for billiard ball collision discussion


########## Collision detection
def point_to_cirlce(point, center1, radius1):
    """Returns True if a point and a circle are touching"""
    dist_vect = point - center1
    dist = dist_vect.Magnitude()
    return dist <= radius1


def circle_to_circle(center1, radius1, center2, radius2):
    """Returns True if two circles are touching"""
    dist_vect = center1 - center2
    dist = dist_vect.Magnitude()
    return dist <= radius1 + radius2


########## Collision Resolution
def resolve_circle_to_circle(center1, radius1, vel1, center2, radius2, vel2):
    """Resolves collision between to moving circles of equal mass.
    HACK: Just swapping the two velocities right now with some dampening.  Not
    sure what signature this function eventually will need to have and what it
    will need to return."""
    return vel2 * 0.5, vel1 * 0.5


def resolve_circle_to_static_circle(center, radius, vel, staticCenter2, staticRadius2):
    """Resolves collision between a moving circle and a static circle.
    HACK: Just inverts the velocity right now with some dampening.  Not sure
    what signature will eventually look like or what it will need to return."""
    return -(vel * 0.5)
