import math
import random
from functools import reduce

# 3D Math Library
# 
# Desc: This is a library to contain basic math helper classes and functions to
# help with basic 3D math.  (angles, degrees, radians, coordinate systems,
# lines, planes, vectors, matrices, etc.)
#
# This has not been created for speed but for ease of use.  It was initially
# created to be albe to use Python's immediate mode as a 3D calculator.
#
# By: Scott Nelson
# October 2004
#
#
# Revision History:
#
# April 2006
# * Added cVector2, cPolar2, NearestMultiple
# * Merged random math code I found in scattered scripts
# * A bit of reformatting
#
# Feb 2005
# * Added matrix class
# 
# Oct 2004
# * Initial creation



## TEST CODE
## a = gnipMath.cVector3(0, 0, 0); b = gnipMath.cVector3(2, 1, 0); c = gnipMath.cVector3(5, 2, 0)
##
##for u in range(11):
##  print gnipMath.QuadraticInterp(u, v, w, u/10.0)
##

########################################
######################################## Constants
########################################
ApproxEqualTolerance = 0.0001


########################################
######################################## General Math
########################################

def ApproxEqual(val1, val2):
    return abs(val1 - val2) < ApproxEqualTolerance
    
def NearestMultiple(num, target):
    '''
    Round given number to nearest multiple of target.  Useful as a "snap" value to regular "grid."
    NOTE: if the given num is halfway between multiples, the result will "round up" (ex: num=6, target=4, result=8)
    NOTE: only tested with integers
    
    >>> NearestMultiple(27, 90)
    0
    >>> NearestMultiple(-120, 90)
    -90
    >>> NearestMultiple(179, 90)
    180
    >>> NearestMultiple(181, 90)
    180
    >>> NearestMultiple(90, 90)
    90
    '''
    #return(int(num/target)*target) # Base Equation: the largest possible multiple of target that is less than or equal to num
    return int((num+(target//2))//target)*target  # (target/2) is an offset to the equation above

def _LCM(a, b):
    '''helper function for LCM'''
    return ( a * b ) / GCD(a, b)
   
def LCM(numbers):
    '''Lowest Common Multiple
    Reference: http://stackoverflow.com/questions/3681706/lowest-common-multiple-for-all-pairs-in-a-list'''
    return reduce(_LCM, numbers)
 
def GCD(a, b):
    '''Greatest Common Divisor
    Reference: http://stackoverflow.com/questions/3681706/lowest-common-multiple-for-all-pairs-in-a-list'''
    a = int(a)
    b = int(b)
    while b:
        a,b = b,a%b
    return a

def LinInterp(x1, x2, u):
    '''linearly interpolate between two values (can be floats or vectors)'''
    assert isinstance(x1, type(x2)), 'x1 and x2 must both be of the same type'
    return x1 + (x2 - x1)*u

# alias so I can phase LinInterp out
Lerp = LinInterp

def QuadraticInterp(x0, x1, x2, u):
    '''Quadratically interpolates between 3 values.  The 3 given values
    are assumed to exist at u=0,1/2,1 respectively.'''
    #TODO: Think about any degenerate cases that this could run into...
    assert isinstance(x1, type(x0)), 'x1 (%s) must be of same type as x0 (%s)' % (x1.__class__.__name__, x0.__class__.__name__)
    assert isinstance(x2, type(x0)), 'x2 (%s) must be of same type as x0 (%s)' % (x2.__class__.__name__, x0.__class__.__name__)
    assert isinstance(u, float), 'u must be of type float'
    return ((2.0*x0) - (4.0*x1) + (2.0*x2))*u**2 + ((-3.0*x0) + (4.0*x1) - x2)*u + x0


def BiLinInterp(a, b, c, d, u, v):
    '''Bilinear interpolation
    Clockwise winding (organized for pygame's coord system)
    a = top left
    b = top right
    c = bottom right
    d = bottom left
    u = interpolation between a&b, d&c
    v = interpolation between b&c, a&d
    '''
    v1 = LinInterp(a, b, u)
    v2 = LinInterp(d, c, u)
    return(LinInterp(v1, v2, v))

def InverseLerp(val, min, max):
    '''Inverse Linear Interpolation
    Given a value and a range, return the normalized value.  This basically
    returns a value between 0-1 that describes how far the given value is
    between the min and max.  If val is outside of the min/max range, the
    returned value will be outside of the 0-1 range.
    >>> InverseLerp(5, 0, 10)
    0.5
    >>> InverseLerp(10, 0, 20)
    0.5
    >>> InverseLerp(10, 5, 15)
    0.5
    >>> InverseLerp(75, 0, 100)
    0.75
    >>> InverseLerp(0.1, 0, 0.4)
    0.25
    >>> InverseLerp(50, 10, 20)
    4.0
    >>> InverseLerp(-3, 0, 4)
    -0.75
    >>> InverseLerp(25, 0, 100)
    0.25
    >>> InverseLerp(25, 100, 0)
    0.75
    '''
    offset = val - min
    delta = max - min
    return float(offset)/delta


def Clamp(val, min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val

def ClampHi(val, hi):
    '''clamp value to hi if it is greater than hi'''
    if (val > hi):
        return hi
    return val

def ClampLo(val, lo):
    '''clamp value to lo if is less than lo'''
    if (val < lo):
        return lo
    return val



########################################
######################################## Value generators
########################################
class cSineWave:
    '''a class that represents a sine wave
    >>> w = cSineWave(10.0, cRange(-3.0, 3.0))
    >>> '%.1f' % w.Get(-5.0)
    '-0.0'
    >>> '%.1f' % w.Get(0.0)
    '0.0'
    >>> '%.1f' % w.Get(2.5)
    '3.0'
    >>> '%.1f' % w.Get(5.0)
    '0.0'
    >>> '%.1f' % w.Get(7.5)
    '-3.0'
    >>> '%.1f' % w.Get(10.0)
    '-0.0'
    '''
    def __init__(self, wavelength, amplitudeRange, phaseShift = 0.0):
        assert phaseShift >= 0.0 and phaseShift <= 1.0, 'cSineWave\'s phaseShift is %f but it must be between 0 and 1.' % phaseShift
        self._wavelength = wavelength           # length of wave in units
        self._amplitudeRange = amplitudeRange   # min/max values that the amplitude will span
        self._phaseShift = phaseShift           # [0..1] percentage of phase shift
        
    def Get(self, t):
        # OPTIMIZE: cache static calculation results at ctor time
        amplitude = self._amplitudeRange.Span() / 2.0;
        #      amplitude * math.sin(  (2pi * t  / wavelength)       +        phase             ) + amplitudeOffset
        return(amplitude * math.sin(((2*math.pi * t) / self._wavelength) + (2*math.pi * self._phaseShift)) + self._amplitudeRange.Mid());


class cPulseWave:
    '''a class that represents a pulse wave
    TODO: doesnt seem to work properly if arguments are ints
    >>> w2 = cPulseWave(4.0, cRange(-5.0, 2.0))
    >>> '%.1f' % w2.Get(0.0)
    '-5.0'
    >>> '%.1f' % w2.Get(0.1)
    '-5.0'
    >>> '%.1f' % w2.Get(2.1)
    '2.0'
    >>> '%.1f' % w2.Get(4.1)
    '-5.0'
    '''
    def __init__(self, wavelength, amplitudeRange, phaseShift = 0.0, pulseWidth = 0.5):
        assert phaseShift >= 0.0 and phaseShift <= 1.0, 'cSineWave\'s phaseShift is %f but it must be between 0 and 1.' % phaseShift
        assert pulseWidth >= 0.0 and pulseWidth <= 1.0, 'cSineWave\'s pulseWidth is %f but it must be between 0 and 1.' % pulseWidth
        self._wavelength = wavelength           # length of wave in units
        self._amplitudeRange = amplitudeRange   # min/max values that the amplitude will span
        self._phaseShift = phaseShift           # [0..1] percentage of phase shift
        self._pulseWidth = pulseWidth           # [0..1] percentage of wavelength that wave remains at the low level
        # print 'AMP Range:', self._amplitudeRange
    
    def Get(self, t):
        # OPTIMIZE: cache static calculation results at ctor time
        # print 'GET AMP Range:', self._amplitudeRange
        fractional = math.modf(t / self._wavelength + self._phaseShift)[0] # get fractional portion from value
        if (fractional < self._pulseWidth):
            return self._amplitudeRange.lo
        else:
            return self._amplitudeRange.hi

## TODO: class cTriangleWave
## TODO: class cSawtoothWave



########################################
######################################## Range
########################################

class cRange:
    '''
    Range between two values

    Potential problem:  If you crate a cRange with the default ctor and set its hi/lo
    values manually, mIsInitialized will still be false, even though there are valid
    values.  mIsInitialized is used so that Include() can be called on a non-initialied
    cRange so I don't have to try to set hi/lo to some small/huge values to get things
    to work properly.

    TODO: change this so that the client can access .lo and .hi directly (and not ._lo and ._hi
    and all internal updates happen as necessary.  The crux is that this class needs to keep its
    uninitialized state so that you can create an "empty" range object that you then use
    Include() to populate.  Use __getattr__ and __setattr__ to implement this instead of
    traditional C++-ish accessors.  If client changes lo, makes sure it isn't greater
    than hi, etc.

    >>> r = cRange()
    >>> print(r)
    (<empty cRange>)
    >>> r = cRange(-5.0, 5.0)
    >>> print(r)
    (-5.000000 -> 5.000000)
    >>> r.Include(27.0)
    >>> print(r)
    (-5.000000 -> 27.000000)
    >>> r.Include(-15.0)
    >>> print(r)
    (-15.000000 -> 27.000000)
    >>> r.Span()
    42.0
    >>> r.Mid()
    6.0
    >>> r.Contains(-20.0)
    False
    >>> r.Contains(30.0)
    False
    >>> r.Contains(0.0)
    True
    >>> r.Contains(27.0)
    True
    >>> r.Clamp(99.0)
    27.0
    >>> r.Clamp(-99.0)
    -15.0
    >>> r.ClampHi(-30.0)
    -30.0
    >>> r.ClampHi(99.0)
    27.0
    >>> r.ClampLo(99.0)
    99.0
    >>> r.ClampLo(-30.0)
    -15.0
    >>> print(r.lo)
    -15.0
    >>> print(r.hi)
    27.0
    '''
    def __init__(self, lo = None, hi = None):
        self._isInitialized = False
        if lo == None and hi == None:
            self._isInitialized = False
        else:
            assert lo != None and hi != None, 'cRange() must either have zero or two arguments.'
            self.Include(lo)
            self.Include(hi)

    def __str__(self):
        if self._isInitialized:
            return '(%f -> %f)' % (self._lo, self._hi)
        else:
            return '(<empty cRange>)'

    def __getattr__(self, name):
        '''Called when an attribute lookup has not found the attribute in the usual places.'''
        assert self._isInitialized, 'cRange must be initialized before reading attribute "%s".' % name
        if name == 'lo':
            return(self._lo)
        elif name == 'hi':
            return(self._hi)
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        '''Called when an attribute assignment is attempted.
        Used to make .lo and .hi read-only.
        NOTE: it is still technically possible to reach in and directly modify the private ._lo and ._hi, but this would be "impolite".'''
        if name in ('lo', 'hi'):
            raise AttributeError('Attribute "%s" is read-only.' % name)
        self.__dict__[name] = value

    def Span(self):
        '''distance between lo and hi'''
        assert self._isInitialized, 'Calling cRange.Span() on an uninitialized cRange'
        return self._hi - self._lo

    def Mid(self):
        '''midpoint between lo and hi'''
        assert self._isInitialized, 'Calling cRange.Mid() on an uninitialized cRange'
        return (self._lo + self._hi) / 2.0

    def Include(self, val):
        '''expand range to include the given value
        TODO: potentially turn this into an operator+
        '''
        if (not self._isInitialized):
            self._lo = val
            self._hi = val
            self._isInitialized = True
        else:
            if (val < self._lo):
                self._lo = val
            if (val > self._hi):
                self._hi = val

    def IncludeRange(self, range):
        '''expand range to include extents of both ranges'''
        assert self._isInitialized, 'Calling cRange.IncludeRange() on an uninitialized cRange'
        assert range._isInitialized, 'Calling cRange.IncludeRange() using an uninitialized cRange'
        assert isinstance(range, cRange), 'Argument must be a cRange'
        self.Include(range._lo);
        self.Include(range._hi);

    def Contains(self, val):
        '''tests if given value is inside of range'''
        assert self._isInitialized, 'Calling cRange.Contains() on an uninitialized cRange'
        return val >= self._lo and val <= self._hi
    
    def Clamp(self, val):
        '''clamp value to range'''
        assert self._isInitialized, 'Calling cRange.Clamp() on an uninitialized cRange'
        return Clamp(val, self._lo, self._hi)

    def ClampHi(self, val):
        '''clamp value to only hi side of range'''
        assert self._isInitialized, 'Calling cRange.ClampHi() on an uninitialized cRange'
        return ClampHi(val, self._hi)

    def ClampLo(self, val):
        '''clamp value to only lo side of range'''
        assert self._isInitialized, 'Calling cRange.ClampLo() on an uninitialized cRange'
        return ClampLo(val, self._lo)



########################################
######################################## Geometry & Trig
########################################



########################################
######################################## cVector2
########################################
class cVector2:
    '''
    2D vector class
    '''
    def __init__(self, x = 0.0, y = 0.0):
        if isinstance(x, (list, tuple)):
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y

    def __str__(self):
        return '(%f, %f)' % (self.x, self.y)

    def __eq__(self, rhs):
        return(self.x == rhs.x and self.y == rhs.y)

    def __ne__(self, rhs):
        return(self.x != rhs.x or self.y != rhs.y)
    
    def __neg__(self):
        '''Unary negation'''
        return cVector2(-self.x, -self.y)
    
    def __add__(self, rhs):
        return(cVector2(self.x + rhs.x, self.y + rhs.y))

    def __sub__(self, rhs):
        return(cVector2(self.x - rhs.x, self.y - rhs.y))

    def Dot(self, rhs):
        '''Dot Product'''
        return self.x*rhs.x + self.y*rhs.y

    def SetFromPolar(self, angle, length):
        '''Set as a 2D vector given polar coordinates (angle in radians and length)'''
        self.x = math.cos(angle) * length
        self.y = math.sin(angle) * length
        
    def AsPolar(self):
        return cPolar2(math.atan2(self.y, self.x), self.Magnitude())

    def Rotate(self, angle):
        '''Rotates vector by given angle (in radians) in CCW direction.'''
        newx = self.x*math.cos(angle) - self.y*math.sin(angle)
        newy = self.y*math.cos(angle) + self.x*math.sin(angle)
        self.x = newx
        self.y = newy
        
    def AsTuple(self):
        return((self.x, self.y))

    def AsIntTuple(self):
        '''Cast values to int. Useful for Pygame'''
        return((int(self.x), int(self.y)))

    @staticmethod
    def Rand(*args):
        if len(args) == 2:
            xrange, yrange = args
            return cVector2(
                random.random() * xrange - (xrange / 2.0),
                random.random() * yrange - (yrange / 2.0)
            )
        elif len(args) == 4:
            xmin, xmax, ymin, ymax = args
            return cVector2(
                random.uniform(xmin, xmax),
                random.uniform(ymin, ymax),
            )
        else:
            raise Exception('cVector2.Random expects either two or four parameters. Got %d.' % len(args))

    @staticmethod
    def RandInRect(rect):
        """Given a pygame rect, return a random cVector2 in that rect"""
        return cVector2(
            (random.random() * rect.width) + rect.x,
            (random.random() * rect.height) + rect.y
        )

    @staticmethod
    def RandInCircle(*args):
        """Return random point in a circle
        Supported signatures:
         - centerx, centery, radius
         - cVector2, radius
         - tuple, radius

        Reference: http://stackoverflow.com/a/30564123
        """
        if len(args) == 3:
            centerx, centery, radius = args
        elif len(args) == 2:
            if isinstance(args[0], cVector2):
                centerx, centery, radius = (args[0].x, args[0].y, args[1])
            else:
                centerx, centery, radius = (args[0][0], args[0][1], args[1])

        # random angle
        alpha = 2 * math.pi * random.random()
        # random radius
        r = radius * random.random()
        # calculating coordinates
        return cVector2(
            r * math.cos(alpha) + centerx,
            r * math.sin(alpha) + centery
        )

    def Randomize(self, xrange = 10, yrange = 10, zrange = 10):
        """Sets current vector to new, randomize vector"""
        self.x = random.random() * xrange - (xrange / 2.0)
        self.y = random.random() * yrange - (yrange / 2.0)

    def Magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def SetMagnitude(self, newMagnitude):
        '''changes vector to have given magnitude with same direction'''
        # OPTIMIZE ME!
        v = self.Normalize() * newMagnitude
        self.x = v.x
        self.y = v.y
            
    def Normalize(self):
        '''Return a normalized instance of this vector'''
        assert self.Magnitude() != 0, 'Attempt to normalize vector with 0 magnitude'
        return self / self.Magnitude()

    def NormalizeSafe(self):
        '''if not safe to normalize (a zero vector), return the vector itself
        without normalization'''
        if self.x == 0.0 and self.y == 0.0:
            return self
        else:
            return self.Normalize()
        
    # TODO: I'm sure there is a better way to do this
    def NormalizeInPlace(self):
        '''Normalize current vector (no return value)'''
        assert self.Magnitude() != 0, 'Attempting to normalize a vector with 0 magnitude is unsupported.'
        normVect = self / self.Magnitude()
        self.x = normVect.x
        self.y = normVect.y
        self.z = normVect.z
        
    def __mul__(self, rhs):
        '''Scalar multiplication (vector * scalar)'''
        assert isinstance(rhs, (int, float)), 'rhs argument is not a scalar'
        return cVector2(rhs * self.x, rhs * self.y)

    def __rmul__(self, lhs):
        '''Scalar multiplication (reverse: scalar * vector)'''
        return self * lhs

    def __div__(self, rhs):
        '''Scalar division'''
        return self * (1.0 / rhs)

    def AngleBetween(self, rhs):
        '''Return the angle between the two vectors (using the dot product).
        NOTE: does not include direction (CW vs. CCW)'''
        return math.acos( self.Dot(rhs) / (self.Magnitude() * rhs.Magnitude()) )
        
    @staticmethod
    def RandomDirection():
        v = cVector2()
        angle = random.uniform(0, 2*math.pi)
        v.SetFromPolar(angle, 1.0)
        return(v)

    @staticmethod
    def RandomDirectionWithSpread(dir, halfAngleSpread):
        '''Return a random angle pointing in the direction of dir with a random spread
        of halfAngleSpread on either side.  Both parameters are angles in radians.
        '''
        offset = random.uniform(-halfAngleSpread, halfAngleSpread)
        v = cVector2()
        v.SetFromPolar(dir + offset, 1.0)
        return(v)
    
# TODO: create a method that generates random direction vectors given a primary angle
# and an offset from this angle.  Ex: RandomDirSpread(45deg, 5deg) would generate random
# direction vectors between 40deg and 50deg.  Need to handle the wrap-around case:
# ex: RandomDirSpread(350, 20) needs to generate vectors between 330 and 10 degrees.

########################################
######################################## cPolar2
########################################
class cPolar2:
    '''
    2D polar coordinate class
    '''
    def __init__(self, t = 0, r = 0):
        self.t = t # theta
        self.r = r # radius
        
    def __str__(self):
        return '(%f, %f)' % (self.t, self.r)

    def GetDegreeString(self):
        return '(%f, %f)' % (math.degrees(self.t), self.r)
    
    def AsVector(self):
        return cVector2(self.r * math.cos(self.t), self.r * math.sin(self.t))
            



########################################
######################################## cVector3
########################################
class cVector3:
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.set(x, y, z)

    def Set(self, x, y, z = 0.0):
        '''Convenience function for setting all 3 components.'''
        # Values are casted to floats to make sure all scalar math in this class is
        # done as float math and not int math.
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
    def __str__(self):
        return '%.4f %.4f %.4f' % (self.x, self.y, self.z)

    def SetFromPolar(self, angle, length):
        '''Set as a 2D vector given polar coordinates (angle in radians and length)'''
        self.x = math.cos(angle) * length
        self.y = math.sin(angle) * length
        self.z = 0

    def Randomize(self, xrange = 10, yrange = 10, zrange = 10):
        self.x = random.random() * xrange - (xrange / 2.0)
        self.y = random.random() * yrange - (yrange / 2.0)
        self.z = random.random() * zrange - (zrange / 2.0)
        
    def SetXAxis(self):
        self.x = 1
        self.y = 0
        self.z = 0

    def SetYAxis(self):
        self.x = 0
        self.y = 1
        self.z = 0

    def SetZAxis(self):
        self.x = 0
        self.y = 0
        self.z = 1
        
    def Magnitude(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)
        
    def Normalize(self):
        '''Return a normalized instance of this vector'''
        assert self.Magnitude() != 0, 'Attempt to normalize vector with 0 magnitude'
        return self / self.Magnitude()

    # TODO: I'm sure there is a better way to do this
    def NormalizeInPlace(self):
        '''Normalize current vector (no return value)'''
        assert self.Magnitude() != 0, 'Attempt to normalize vector with 0 magnitude'
        normVect = self / self.Magnitude()
        self.x = normVect.x
        self.y = normVect.y
        self.z = normVect.z

    def __neg__(self):
        '''Unary negation'''
        return vector3(-self.x, -self.y, -self.z)
    
    def __add__(self, rhs):
        assert isinstance(rhs, vector3), 'rhs argument is not a vector3'
        return vector3(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)

    def __sub__(self, rhs):
        return self + -rhs
        
    def __mul__(self, rhs):
        '''Scalar multiplication (vector * scalar)'''
        assert isinstance(rhs, (int, float)), 'rhs argument is not a scalar'
        return vector3(rhs * self.x, rhs * self.y, rhs * self.z)

    def __rmul__(self, lhs):
        '''Scalar multiplication (reverse: scalar * vector)'''
        return self * lhs
        
    def __div__(self, rhs):
        '''Scalar division'''
        return self * (1.0 / rhs)

    def Dot(self, rhs):
        '''Dot Product'''
        return self.x*rhs.x + self.y*rhs.y + self.z*rhs.z
        
    def Cross(self, rhs):
        '''Cross Product'''
        return vector3(self.y * rhs.z - self.z * rhs.y,
                       self.z * rhs.x - self.x * rhs.z,
                       self.x * rhs.y - self.y * rhs.x)

    def AngleBetween(self, rhs):
        '''Return the angle between the two vectors (using the dot product)'''
        return math.acos( self.Dot(rhs) / (self.Magnitude() * rhs.Magnitude()) )
    
    def ProjectOnto(self, rhs):
        '''Returns the vector resulting from projecting self onto rhs'''
        newVect = vector3()
        newVect = rhs * (self.Dot(rhs) / rhs.Dot(rhs))
        return newVect


########################################
######################################## cVector4
########################################
class cVector4(cVector3):
    def __init__(self, x = 0.0, y = 0.0, z = 0.0, w = 1.0):     
        self.set(x, y, z, w)

    def Set(self, x, y, z = 0.0, w = 1.0):
        '''Convenience function for setting all 4 components.'''
        # Values are casted to floats to make sure all scalar math in this class is
        # done as float math and not int math.  
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)
        
    def __str__(self):
        return '%.4f %.4f %.4f %.4f' % (self.x, self.y, self.z, self.w)


########################################
######################################## matrix
########################################
#
# self.m[row][column]
#
class cMatrix:
    def __init__(self):
        '''Constructor'''
        self.makeIdentity()

    def MakeIdentity(self):
        '''Convenience function for setting all 3 components.'''
        self.m =    (
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0]
                    )


    def MakeTranslate(self, v):
        '''Make a translation matrix from the given vector'''
        self.makeIdentity()
        self.m[0][3] = v.x
        self.m[1][3] = v.y
        self.m[2][3] = v.z

    def MakeRotateZ(self, theta):
        self.m =    (
                    [math.cos(theta),  math.sin(theta), 0, 0],
                    [-math.sin(theta), math.cos(theta), 0, 0],
                    [0,           0,          1, 0],
                    [0,           0,          0, 1]
                    )

    def __str__(self):
        formatString = '%7.3f %7.3f %7.3f %7.3f\n'
        s1 = formatString % (self.m[0][0], self.m[0][1], self.m[0][2], self.m[0][3])
        s2 = formatString % (self.m[1][0], self.m[1][1], self.m[1][2], self.m[1][3])
        s3 = formatString % (self.m[2][0], self.m[2][1], self.m[2][2], self.m[2][3])
        s4 = formatString % (self.m[3][0], self.m[3][1], self.m[3][2], self.m[3][3])
        return s1 + s2 + s3 + s4

    def __mul__(self, rhs):
        '''Matrix multiplication (matrix * matrix)'''
        if isinstance(rhs, matrix):
            return self.__MultiplyMatrixToMatrix(rhs)
        elif isinstance(rhs, vector4):
            return self.__MultiplyMatrixToVector4(rhs)
        else:
            assert True, 'rhs argument must be a matrix or vector3' 


    #################### PRIVATE METHODS
    def __MultiplyMatrixToMatrix(self, rhs):
        result = matrix()
        for c in range(4):
            for r in range(4):
                result.m[r][c] = self.m[r][0] * rhs.m[0][c] + self.m[r][1] * rhs.m[1][c] + self.m[r][2] * rhs.m[2][c] + self.m[r][3] * rhs.m[3][c];
        return result

    def __MultiplyMatrixToVector4(self, rhs):
        result = vector4()
        result.x = self.m[0][0]*rhs.x + self.m[0][1]*rhs.y + self.m[0][2]*rhs.z + self.m[0][3]*rhs.w;
        result.y = self.m[1][0]*rhs.x + self.m[1][1]*rhs.y + self.m[1][2]*rhs.z + self.m[1][3]*rhs.w;
        result.z = self.m[2][0]*rhs.x + self.m[2][1]*rhs.y + self.m[2][2]*rhs.z + self.m[2][3]*rhs.w;
        result.w = self.m[3][0]*rhs.x + self.m[3][1]*rhs.y + self.m[3][2]*rhs.z + self.m[3][3]*rhs.w;
        return result
    
# matrix * point
##r.dat[0] = d[0][0]*p.dat[0] + d[0][1]*p.dat[1] + d[0][2]*p.dat[2] + d[0][3]*p.dat[3];
##r.dat[1] = d[1][0]*p.dat[0] + d[1][1]*p.dat[1] + d[1][2]*p.dat[2] + d[1][3]*p.dat[3];
##r.dat[2] = d[2][0]*p.dat[0] + d[2][1]*p.dat[1] + d[2][2]*p.dat[2] + d[2][3]*p.dat[3];
##r.dat[3] = d[3][0]*p.dat[0] + d[3][1]*p.dat[1] + d[3][2]*p.dat[2] + d[3][3]*p.dat[3];
    



########################################
######################################## Doctest
########################################
# To enable the doctest on this module, uncomment the lines below and
# run the script from the command line.  Ex:
# python gnipMath.py

def RunDoctest():
    import doctest
    doctest.testmod(verbose=True, raise_on_error=True)

if __name__ == '__main__':
    print('*' * 40)
    print('* Running Doctest tests on this file...')
    print('* Remember, no news is good news')
    print('*' * 40)
    RunDoctest()



    
