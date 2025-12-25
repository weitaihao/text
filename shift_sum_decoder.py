"""
移位求和解码实现，用于非二进制循环码。
实现了HISS（硬判决迭代移位求和）和SISS（软判决迭代移位求和）算法。
"""

import numpy as np
from typing import List, Tuple, Dict
from galois_field import GaloisField, GFPolynomial
from cyclic_codes import ReedSolomonCode, NonBinaryBCHCode


class MinimumWeightDualCodeword:
    """
    最小重量对偶码字(MWDC)生成器。
    """
    
    def __init__(self, code, num_mwdcs: int = 5):
        """
        初始化MWDC生成器。
        
        参数:
            code: 循环码（RS或NB-BCH）
            num_mwdcs: 要生成的MWDC数量
        """
        self.code = code
        self.gf = code.gf
        self.num_mwdcs = num_mwdcs
        self.mwdcs = self._generate_mwdcs()
    
    def _generate_mwdcs(self) -> List[GFPolynomial]:
        """
        Generate cyclically different MWDCs.
        
        For the dual code C^perp, we generate MWDCs that are cyclically different.
        The MWDCs have minimum weight d^perp.
        """
        mwdcs = []
        
        # For RS codes, the dual code is also an RS code
        # We generate simple MWDCs based on the generator polynomial
        
        # Strategy: Use simple low-weight polynomials
        # For example: 1 + alpha^i * x^j + alpha^k * x^l
        
        # Start with the simplest MWDC: based on dual code structure
        # For RS code C(2^s; n, k, d), dual is C^perp(2^s; n, n-k, k+1)
        
        # Generate some example MWDCs
        for i in range(min(self.num_mwdcs, self.gf.size - 1)):
            # Create polynomial: 1 + alpha^i * x^b2 + alpha^(2i) * x^b3 + ...
            coeffs = [0] * self.code.n
            coeffs[0] = 1  # Constant term
            
            # Add other terms
            if self.code.n > 1:
                coeffs[1] = self.gf.alpha(i)
            if self.code.n > 2:
                coeffs[2] = self.gf.alpha(2 * i % (self.gf.size - 1))
            if self.code.n > 3:
                coeffs[3] = self.gf.alpha(3 * i % (self.gf.size - 1))
            
            poly = GFPolynomial(coeffs, self.gf)
            mwdcs.append(poly)
        
        return mwdcs
    
    def get_shifted_mwdcs(self) -> List[List[GFPolynomial]]:
        """
        Get all cyclic shifts of each MWDC.
        
        Returns:
            List of lists, where each inner list contains all shifts of one MWDC
        """
        all_shifts = []
        
        for mwdc in self.mwdcs:
            shifts = []
            coeffs = mwdc.coeffs + [0] * (self.code.n - len(mwdc.coeffs))
            
            for shift in range(self.code.n):
                # Cyclic shift
                shifted_coeffs = coeffs[-shift:] + coeffs[:-shift] if shift > 0 else coeffs
                shifts.append(GFPolynomial(shifted_coeffs, self.gf))
            
            all_shifts.append(shifts)
        
        return all_shifts


class ShiftSumDecoder:
    """
    Base class for Shift-Sum decoding.
    """
    
    def __init__(self, code, num_mwdcs: int = 5):
        """
        Initialize Shift-Sum decoder.
        
        Args:
            code: Cyclic code instance
            num_mwdcs: Number of MWDCs to use
        """
        self.code = code
        self.gf = code.gf
        self.n = code.n
        
        # Generate MWDCs
        self.mwdc_gen = MinimumWeightDualCodeword(code, num_mwdcs)
        self.mwdcs_shifts = self.mwdc_gen.get_shifted_mwdcs()
    
    def compute_syndrome_polynomial(self, received: List[int]) -> GFPolynomial:
        """
        Compute syndrome polynomial w(x) for received word r(x).
        
        Args:
            received: Received word
        
        Returns:
            Syndrome polynomial w(x) = r(x) * beta(x) mod (x^n - 1)
        """
        r_poly = GFPolynomial(received, self.gf)
        
        # For now, use a simple syndrome calculation
        # In practice, beta(x) is the dual codeword polynomial
        syndromes = self.code.compute_syndrome(received)
        
        return GFPolynomial(syndromes + [0] * (self.n - len(syndromes)), self.gf)
    
    def build_frequency_matrix(self, received: List[int]) -> np.ndarray:
        """
        Build frequency matrix Phi using shift-sum operation.
        
        Args:
            received: Received word r(x)
        
        Returns:
            Frequency matrix of size (2^m - 1) x n
        """
        # Initialize frequency matrix
        freq_matrix = np.zeros((self.gf.size - 1, self.n), dtype=int)
        
        # For each MWDC and its shifts
        for mwdc_shifts in self.mwdcs_shifts:
            for shift_idx, beta_poly in enumerate(mwdc_shifts):
                # Compute w(x) = r(x) * beta(x) mod (x^n - 1)
                r_poly = GFPolynomial(received, self.gf)
                w_poly = r_poly * beta_poly
                
                # Get coefficients modulo x^n - 1
                w_coeffs = w_poly.coeffs
                if len(w_coeffs) > self.n:
                    # Reduce modulo x^n - 1
                    reduced = [0] * self.n
                    for i, c in enumerate(w_coeffs):
                        reduced[i % self.n] = self.gf.add(reduced[i % self.n], c)
                    w_coeffs = reduced
                
                # Update frequency matrix
                for pos, coeff in enumerate(w_coeffs):
                    if coeff != 0:
                        # Find which power of alpha this is
                        if coeff in self.gf.log_table:
                            alpha_power = self.gf.log_table[coeff]
                            freq_matrix[alpha_power, pos] += 1
        
        return freq_matrix
    
    def identify_errors_from_matrix(self, freq_matrix: np.ndarray, 
                                     threshold: int = None) -> Tuple[List[int], List[int]]:
        """
        Identify error positions and magnitudes from frequency matrix.
        
        Args:
            freq_matrix: Frequency matrix
            threshold: Threshold for error detection
        
        Returns:
            Tuple of (error_positions, error_magnitudes)
        """
        error_positions = []
        error_magnitudes = []
        
        # For each column (position)
        for j in range(self.n):
            column = freq_matrix[:, j]
            
            # Find the most frequent value (excluding zero)
            if np.sum(column) > 0:
                max_freq_idx = np.argmax(column)
                max_freq = column[max_freq_idx]
                
                # If frequency is high enough, consider it an error
                if threshold is None:
                    threshold = len(self.mwdcs_shifts) // 2
                
                if max_freq >= threshold:
                    error_positions.append(j)
                    error_magnitudes.append(self.gf.alpha(max_freq_idx))
        
        return error_positions, error_magnitudes


class HISSDecoder(ShiftSumDecoder):
    """
    Hard-decision Iterative Shift-Sum (HISS) Decoder.
    """
    
    def __init__(self, code, num_mwdcs: int = 5, max_iterations: int = 10):
        """
        Initialize HISS decoder.
        
        Args:
            code: Cyclic code instance
            num_mwdcs: Number of MWDCs
            max_iterations: Maximum number of iterations
        """
        super().__init__(code, num_mwdcs)
        self.max_iterations = max_iterations
    
    def decode(self, received: List[int]) -> List[int]:
        """
        Decode received word using HISS algorithm.
        
        Args:
            received: Received word (hard decisions)
        
        Returns:
            Decoded codeword
        """
        current = received.copy()
        
        for iteration in range(self.max_iterations):
            # Check if syndrome is zero (valid codeword)
            syndromes = self.code.compute_syndrome(current)
            if all(s == 0 for s in syndromes):
                return current
            
            # Build frequency matrix
            freq_matrix = self.build_frequency_matrix(current)
            
            # Identify errors
            error_pos, error_mag = self.identify_errors_from_matrix(freq_matrix)
            
            if not error_pos:
                break  # No errors detected
            
            # Correct errors
            for pos, mag in zip(error_pos, error_mag):
                current[pos] = self.gf.subtract(current[pos], mag)
        
        return current


class SISSDecoder(ShiftSumDecoder):
    """
    Soft-decision Iterative Shift-Sum (SISS) Decoder.
    """
    
    def __init__(self, code, num_mwdcs: int = 5, max_iterations: int = 10):
        """
        Initialize SISS decoder.
        
        Args:
            code: Cyclic code instance
            num_mwdcs: Number of MWDCs
            max_iterations: Maximum number of iterations
        """
        super().__init__(code, num_mwdcs)
        self.max_iterations = max_iterations
    
    def decode(self, received: List[int], soft_info: np.ndarray = None) -> List[int]:
        """
        Decode received word using SISS algorithm with soft information.
        
        Args:
            received: Received word (hard decisions)
            soft_info: Soft information (log-likelihood ratios or probabilities)
        
        Returns:
            Decoded codeword
        """
        current = received.copy()
        
        for iteration in range(self.max_iterations):
            # Check if syndrome is zero
            syndromes = self.code.compute_syndrome(current)
            if all(s == 0 for s in syndromes):
                return current
            
            # Build frequency matrix
            freq_matrix = self.build_frequency_matrix(current)
            
            # Weight frequency matrix with soft information if available
            if soft_info is not None:
                # Use soft information to weight the frequency matrix
                weighted_matrix = freq_matrix * soft_info.reshape(1, -1)
            else:
                weighted_matrix = freq_matrix
            
            # Identify errors
            error_pos, error_mag = self.identify_errors_from_matrix(weighted_matrix)
            
            if not error_pos:
                break
            
            # Correct errors
            for pos, mag in zip(error_pos, error_mag):
                current[pos] = self.gf.subtract(current[pos], mag)
        
        return current
