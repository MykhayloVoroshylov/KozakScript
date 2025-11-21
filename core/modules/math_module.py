"""Math module for KozakScript"""
import math

class MathModule:
    """Provides mathematical functions and constants"""
    
    # Constants
    @property
    def pi(self):
        """Pi constant (π ≈ 3.14159...)"""
        return math.pi
    
    @property
    def e(self):
        """Euler's number (e ≈ 2.71828...)"""
        return math.e
    
    @property
    def tau(self):
        """Tau constant (τ = 2π ≈ 6.28318...)"""
        return math.tau
    
    @property
    def inf(self):
        """Positive infinity"""
        return math.inf
    
    @property
    def nan(self):
        """Not a Number (NaN)"""
        return math.nan
    
    # Trigonometric functions
    def sin(self, x):
        """Sine of x (x in radians)"""
        return math.sin(x)
    
    def cos(self, x):
        """Cosine of x (x in radians)"""
        return math.cos(x)
    
    def tan(self, x):
        """Tangent of x (x in radians)"""
        return math.tan(x)
    
    def asin(self, x):
        """Arc sine of x, in radians"""
        return math.asin(x)
    
    def acos(self, x):
        """Arc cosine of x, in radians"""
        return math.acos(x)
    
    def atan(self, x):
        """Arc tangent of x, in radians"""
        return math.atan(x)
    
    def atan2(self, y, x):
        """Arc tangent of y/x, in radians"""
        return math.atan2(y, x)
    
    # Hyperbolic functions
    def sinh(self, x):
        """Hyperbolic sine of x"""
        return math.sinh(x)
    
    def cosh(self, x):
        """Hyperbolic cosine of x"""
        return math.cosh(x)
    
    def tanh(self, x):
        """Hyperbolic tangent of x"""
        return math.tanh(x)
    
    def asinh(self, x):
        """Inverse hyperbolic sine of x"""
        return math.asinh(x)
    
    def acosh(self, x):
        """Inverse hyperbolic cosine of x"""
        return math.acosh(x)
    
    def atanh(self, x):
        """Inverse hyperbolic tangent of x"""
        return math.atanh(x)
    
    # Angle conversion
    def degrees(self, x):
        """Convert angle x from radians to degrees"""
        return math.degrees(x)
    
    def radians(self, x):
        """Convert angle x from degrees to radians"""
        return math.radians(x)
    
    # Power and logarithmic functions
    def exp(self, x):
        """e raised to the power x"""
        return math.exp(x)
    
    def log(self, x, base=None):
        """Logarithm of x to the given base (natural log if base not specified)"""
        if base is None:
            return math.log(x)
        return math.log(x, base)
    
    def log10(self, x):
        """Base-10 logarithm of x"""
        return math.log10(x)
    
    def log2(self, x):
        """Base-2 logarithm of x"""
        return math.log2(x)
    
    def sqrt(self, x):
        """Square root of x"""
        return math.sqrt(x)
    
    def pow(self, x, y):
        """x raised to the power y"""
        return math.pow(x, y)
    
    # Rounding and absolute value
    def ceil(self, x):
        """Smallest integer >= x"""
        return math.ceil(x)
    
    def floor(self, x):
        """Largest integer <= x"""
        return math.floor(x)
    
    def trunc(self, x):
        """Truncate x to an integer"""
        return math.trunc(x)
    
    def round(self, x, ndigits=None):
        """Round x to ndigits decimal places"""
        if ndigits is None:
            return round(x)
        return round(x, ndigits)
    
    def abs(self, x):
        """Absolute value of x"""
        return abs(x)
    
    def fabs(self, x):
        """Absolute value of x (as float)"""
        return math.fabs(x)
    
    # Special functions
    def factorial(self, x):
        """Factorial of x (x!)"""
        return math.factorial(x)
    
    def gcd(self, a, b):
        """Greatest common divisor of a and b"""
        return math.gcd(a, b)
    
    def lcm(self, a, b):
        """Least common multiple of a and b"""
        return math.lcm(a, b)
    
    def copysign(self, x, y):
        """Return x with the sign of y"""
        return math.copysign(x, y)
    
    def fmod(self, x, y):
        """Floating point remainder of x/y"""
        return math.fmod(x, y)
    
    def modf(self, x):
        """Return fractional and integer parts of x"""
        return math.modf(x)
    
    def isnan(self, x):
        """Check if x is NaN"""
        return math.isnan(x)
    
    def isinf(self, x):
        """Check if x is infinite"""
        return math.isinf(x)
    
    def isfinite(self, x):
        """Check if x is finite"""
        return math.isfinite(x)
    
    # Distance and norm
    def hypot(self, *args):
        """Euclidean norm, sqrt(sum of squares)"""
        return math.hypot(*args)
    
    def dist(self, p, q):
        """Euclidean distance between two points (as lists/tuples)"""
        return math.dist(p, q)
    
    # Min/Max
    def min(self, *args):
        """Return the minimum value"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return min(args[0])
        return min(args)
    
    def max(self, *args):
        """Return the maximum value"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return max(args[0])
        return max(args)
    
    def sum(self, iterable):
        """Sum of all elements in iterable"""
        return sum(iterable)
    
    # Combinatorics
    def comb(self, n, k):
        """Number of ways to choose k items from n items (binomial coefficient)"""
        return math.comb(n, k)
    
    def perm(self, n, k=None):
        """Number of ways to choose k items from n items with order"""
        if k is None:
            k = n
        return math.perm(n, k)