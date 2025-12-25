"""
非二进制循环码实现。
包括Reed-Solomon (RS)码和非二进制BCH (NB-BCH)码。
"""

import numpy as np
from typing import List, Tuple
from galois_field import GaloisField, GFPolynomial


class ReedSolomonCode:
    """
    Reed-Solomon码实现。
    
    一个RS码 C(2^s; n, k, d_RS) 其中:
    - n: 码字长度
    - k: 消息长度
    - d_RS: 最小汉明距离
    """
    
    def __init__(self, s: int, n: int, k: int, b: int = 0):
        """
        初始化RS码。
        
        参数:
            s: 域参数 (域大小 = 2^s)
            n: 码字长度
            k: 消息长度 (维度)
            b: 第一个根的指数 (默认为0)
        """
        self.s = s
        self.n = n
        self.k = k
        self.b = b
        self.d = n - k + 1  # 最小距离
        
        # 初始化伽罗华域
        self.gf = GaloisField(s)
        
        # 生成多项式系数
        self.gen_poly = self._compute_generator_polynomial()
    
    def _compute_generator_polynomial(self) -> List[int]:
        """
        计算RS码的生成多项式 g(x)。
        g(x) = (x - alpha^b)(x - alpha^(b+1))...(x - alpha^(b+d-2))
        """
        # 从 g(x) = 1 开始
        g = GFPolynomial([1], self.gf)
        
        # 乘以 (x - alpha^i) for i = b to b+d-2
        for i in range(self.b, self.b + self.d - 1):
            alpha_i = self.gf.alpha(i)
            # (x - alpha^i)
            factor = GFPolynomial([self.gf.subtract(0, alpha_i), 1], self.gf)
            g = g * factor
        
        return g.coeffs
    
    def encode(self, message: List[int]) -> List[int]:
        """
        使用系统编码方式编码消息。
        
        参数:
            message: k个来自GF(2^s)的符号
        
        返回:
            长度为n的码字
        """
        if len(message) != self.k:
            raise ValueError(f"消息长度必须为 {self.k}")
        
        # 系统编码: 码字 = [校验位 | 消息]
        # 构造 m(x)*x^(n-k)
        msg_coeffs = message + [0] * (self.n - self.k)
        msg_poly = GFPolynomial(msg_coeffs, self.gf)
        gen_poly = GFPolynomial(self.gen_poly, self.gf)
        
        # 计算余数 r(x) = m(x)*x^(n-k) mod g(x)
        remainder = msg_poly % gen_poly
        r_coeffs = remainder.coeffs
        
        # 确保余数有正确的长度
        while len(r_coeffs) < self.n - self.k:
            r_coeffs.append(0)
        r_coeffs = r_coeffs[:self.n - self.k]
        
        # 码字 = [校验位 | 消息]
        # 其中校验位使得整个码字能被g(x)整除
        # 在GF(2^m)中，-r(x) = r(x) (因为每个元素是自己的加法逆)
        codeword = r_coeffs + message
        
        return codeword
    
    def compute_syndrome(self, received: List[int]) -> List[int]:
        """
        计算接收字的校验子。
        
        参数:
            received: 接收字 (可能有错误)
        
        返回:
            校验子值 [S_b, S_(b+1), ..., S_(b+2t-1)]
        """
        r_poly = GFPolynomial(received, self.gf)
        syndromes = []
        
        # 在 alpha^b, alpha^(b+1), ..., alpha^(b+2t-1) 处求值
        # 其中 2t = d - 1 = n - k
        for i in range(self.b, self.b + self.n - self.k):
            alpha_i = self.gf.alpha(i)
            s_i = r_poly.evaluate(alpha_i)
            syndromes.append(s_i)
        
        return syndromes


class NonBinaryBCHCode:
    """
    Non-Binary BCH Code implementation.
    
    An NB-BCH code with length n = 2^s - 1, dimension k, and minimum distance d.
    """
    
    def __init__(self, s: int, n: int, k: int, designed_distance: int):
        """
        Initialize NB-BCH code.
        
        Args:
            s: Field parameter (field size = 2^s)
            n: Codeword length (typically 2^s - 1)
            k: Message length (dimension)
            designed_distance: Designed minimum distance
        """
        self.s = s
        self.n = n
        self.k = k
        self.d = designed_distance
        
        # Initialize Galois Field
        self.gf = GaloisField(s)
        
        # Generator polynomial
        self.gen_poly = self._compute_generator_polynomial()
    
    def _compute_generator_polynomial(self) -> List[int]:
        """
        Compute generator polynomial for NB-BCH code.
        The generator has consecutive roots at alpha^1, alpha^2, ..., alpha^(d-1)
        """
        # Start with g(x) = 1
        g = GFPolynomial([1], self.gf)
        
        # Find minimal polynomials for consecutive powers of alpha
        used_roots = set()
        
        for i in range(1, self.d):
            if i in used_roots:
                continue
            
            # Find conjugates (for binary extension fields)
            conjugates = self._find_conjugates(i)
            used_roots.update(conjugates)
            
            # Multiply by minimal polynomial for this conjugacy class
            min_poly = self._minimal_polynomial(conjugates)
            g = g * min_poly
        
        return g.coeffs
    
    def _find_conjugates(self, i: int) -> List[int]:
        """Find conjugacy class of alpha^i."""
        conjugates = [i]
        current = i
        
        for _ in range(self.s - 1):
            current = (current * 2) % (self.gf.size - 1)
            if current == i:
                break
            conjugates.append(current)
        
        return conjugates
    
    def _minimal_polynomial(self, roots: List[int]) -> GFPolynomial:
        """Compute minimal polynomial with given roots (as powers of alpha)."""
        poly = GFPolynomial([1], self.gf)
        
        for root_power in roots:
            alpha_root = self.gf.alpha(root_power)
            # Multiply by (x - alpha^root_power)
            factor = GFPolynomial([self.gf.subtract(0, alpha_root), 1], self.gf)
            poly = poly * factor
        
        return poly
    
    def encode(self, message: List[int]) -> List[int]:
        """
        Encode message using systematic encoding.
        
        Args:
            message: k symbols from GF(2^s)
        
        Returns:
            Codeword of length n
        """
        if len(message) != self.k:
            raise ValueError(f"Message length must be {self.k}")
        
        # Systematic encoding
        shifted_msg = [0] * (self.n - self.k) + message
        msg_poly = GFPolynomial(shifted_msg, self.gf)
        gen_poly = GFPolynomial(self.gen_poly, self.gf)
        remainder_poly = msg_poly % gen_poly
        
        parity = remainder_poly.coeffs + [0] * ((self.n - self.k) - len(remainder_poly.coeffs))
        codeword = parity[:self.n - self.k] + message
        
        return codeword
    
    def compute_syndrome(self, received: List[int]) -> List[int]:
        """
        Compute syndrome for received word.
        
        Args:
            received: Received word
        
        Returns:
            Syndrome values
        """
        r_poly = GFPolynomial(received, self.gf)
        syndromes = []
        
        for i in range(1, self.d):
            alpha_i = self.gf.alpha(i)
            s_i = r_poly.evaluate(alpha_i)
            syndromes.append(s_i)
        
        return syndromes
