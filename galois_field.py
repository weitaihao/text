"""
Galois Field (Finite Field) implementation for non-binary cyclic codes.
Implements GF(2^m) arithmetic operations.
"""

import numpy as np
from typing import List, Tuple


class GaloisField:
    """
    Galois Field GF(2^m) implementation.
    
    Attributes:
        m: The extension degree (field size = 2^m)
        size: The number of elements in the field (2^m)
        primitive_poly: The primitive polynomial coefficients
        exp_table: Exponential lookup table (alpha^i)
        log_table: Logarithm lookup table (log_alpha(i))
    """
    
    def __init__(self, m: int, primitive_poly: int = None):
        """
        Initialize Galois Field GF(2^m).
        
        Args:
            m: Extension degree
            primitive_poly: Primitive polynomial as integer (if None, use default)
        """
        self.m = m
        self.size = 2 ** m
        self.primitive_poly = primitive_poly or self._get_default_primitive_poly(m)
        
        # Build lookup tables
        self.exp_table = np.zeros(self.size * 2, dtype=int)
        self.log_table = np.zeros(self.size, dtype=int)
        self._build_tables()
    
    def _get_default_primitive_poly(self, m: int) -> int:
        """Get default primitive polynomial for common field sizes."""
        # Primitive polynomials for GF(2^m)
        primitives = {
            2: 0b111,      # x^2 + x + 1
            3: 0b1011,     # x^3 + x + 1
            4: 0b10011,    # x^4 + x + 1
            5: 0b100101,   # x^5 + x^2 + 1
            6: 0b1000011,  # x^6 + x + 1
            7: 0b10001001, # x^7 + x^3 + 1
            8: 0b100011101 # x^8 + x^4 + x^3 + x^2 + 1
        }
        if m not in primitives:
            raise ValueError(f"No default primitive polynomial for GF(2^{m})")
        return primitives[m]
    
    def _build_tables(self):
        """Build exponential and logarithm lookup tables."""
        # exp_table[i] = alpha^i
        value = 1
        for i in range(self.size - 1):
            self.exp_table[i] = value
            self.log_table[value] = i
            
            # Multiply by alpha (shift left and reduce)
            value <<= 1
            if value & self.size:  # If overflow
                value ^= self.primitive_poly
        
        # Extend exp_table for easier computation
        for i in range(self.size - 1, self.size * 2):
            self.exp_table[i] = self.exp_table[i - (self.size - 1)]
    
    def add(self, a: int, b: int) -> int:
        """Addition in GF(2^m) is XOR."""
        return a ^ b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtraction in GF(2^m) is same as addition (XOR)."""
        return a ^ b
    
    def multiply(self, a: int, b: int) -> int:
        """Multiplication in GF(2^m)."""
        if a == 0 or b == 0:
            return 0
        return self.exp_table[self.log_table[a] + self.log_table[b]]
    
    def divide(self, a: int, b: int) -> int:
        """Division in GF(2^m)."""
        if b == 0:
            raise ZeroDivisionError("Division by zero in Galois Field")
        if a == 0:
            return 0
        log_result = self.log_table[a] - self.log_table[b]
        return self.exp_table[log_result % (self.size - 1)]
    
    def power(self, a: int, n: int) -> int:
        """Raise element a to power n in GF(2^m)."""
        if a == 0:
            return 0 if n > 0 else 1
        if n == 0:
            return 1
        log_result = (self.log_table[a] * n) % (self.size - 1)
        return self.exp_table[log_result]
    
    def inverse(self, a: int) -> int:
        """Multiplicative inverse in GF(2^m)."""
        if a == 0:
            raise ZeroDivisionError("Zero has no multiplicative inverse")
        return self.exp_table[(self.size - 1) - self.log_table[a]]
    
    def alpha(self, i: int) -> int:
        """Get alpha^i (primitive element to power i)."""
        return self.exp_table[i % (self.size - 1)]


class GFPolynomial:
    """Polynomial over Galois Field."""
    
    def __init__(self, coeffs: List[int], gf: GaloisField):
        """
        Initialize polynomial over GF.
        
        Args:
            coeffs: Coefficients [c0, c1, ..., cn] representing c0 + c1*x + ... + cn*x^n
            gf: Galois Field instance
        """
        self.gf = gf
        self.coeffs = self._trim(coeffs)
    
    def _trim(self, coeffs: List[int]) -> List[int]:
        """Remove leading zeros from coefficient list."""
        coeffs = list(coeffs)
        while len(coeffs) > 1 and coeffs[-1] == 0:
            coeffs.pop()
        return coeffs if coeffs else [0]
    
    @property
    def degree(self) -> int:
        """Degree of the polynomial."""
        return len(self.coeffs) - 1
    
    def __add__(self, other: 'GFPolynomial') -> 'GFPolynomial':
        """Add two polynomials."""
        max_len = max(len(self.coeffs), len(other.coeffs))
        result = [0] * max_len
        
        for i in range(len(self.coeffs)):
            result[i] = self.gf.add(result[i], self.coeffs[i])
        for i in range(len(other.coeffs)):
            result[i] = self.gf.add(result[i], other.coeffs[i])
        
        return GFPolynomial(result, self.gf)
    
    def __mul__(self, other: 'GFPolynomial') -> 'GFPolynomial':
        """Multiply two polynomials."""
        result = [0] * (len(self.coeffs) + len(other.coeffs) - 1)
        
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                result[i + j] = self.gf.add(result[i + j], self.gf.multiply(a, b))
        
        return GFPolynomial(result, self.gf)
    
    def __mod__(self, other: 'GFPolynomial') -> 'GFPolynomial':
        """Polynomial modulo operation."""
        dividend = self.coeffs.copy()
        divisor = other.coeffs
        
        while len(dividend) >= len(divisor) and dividend[-1] != 0:
            # Get leading coefficient ratio
            ratio = self.gf.divide(dividend[-1], divisor[-1])
            
            # Subtract divisor * ratio from dividend
            for i in range(len(divisor)):
                pos = len(dividend) - len(divisor) + i
                dividend[pos] = self.gf.subtract(
                    dividend[pos],
                    self.gf.multiply(divisor[i], ratio)
                )
            
            dividend.pop()
        
        return GFPolynomial(dividend, self.gf)
    
    def evaluate(self, x: int) -> int:
        """Evaluate polynomial at point x using Horner's method."""
        result = 0
        for coeff in reversed(self.coeffs):
            result = self.gf.add(self.gf.multiply(result, x), coeff)
        return result
    
    def __repr__(self) -> str:
        return f"GFPolynomial({self.coeffs})"
