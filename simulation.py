"""
信道模拟和仿真框架
用于测试移位求和解码算法的性能
"""

import numpy as np
from typing import List, Tuple, Callable
from galois_field import GaloisField
from cyclic_codes import ReedSolomonCode, NonBinaryBCHCode
from shift_sum_decoder import HISSDecoder, SISSDecoder


class AWGNChannel:
    """
    加性高斯白噪声(AWGN)信道模拟
    """
    
    def __init__(self, snr_db: float, modulation: str = 'BPSK'):
        """
        初始化AWGN信道
        
        参数:
            snr_db: 信噪比(dB)
            modulation: 调制方式 ('BPSK', 'QPSK', 等)
        """
        self.snr_db = snr_db
        self.snr_linear = 10 ** (snr_db / 10)
        self.modulation = modulation
    
    def transmit(self, codeword: List[int], gf: GaloisField) -> Tuple[List[int], np.ndarray]:
        """
        通过AWGN信道传输码字
        
        参数:
            codeword: 发送的码字
            gf: 伽罗华域
        
        返回:
            (接收到的硬判决, 软信息)
        """
        # 将GF符号映射到调制符号
        modulated = self._modulate(codeword, gf)
        
        # 添加高斯噪声
        noise_power = 1.0 / self.snr_linear
        noise = np.random.normal(0, np.sqrt(noise_power), len(modulated))
        received_signal = modulated + noise
        
        # 解调得到硬判决和软信息
        hard_decision = self._demodulate(received_signal, gf)
        soft_info = self._compute_soft_info(received_signal, modulated)
        
        return hard_decision, soft_info
    
    def _modulate(self, symbols: List[int], gf: GaloisField) -> np.ndarray:
        """
        调制GF符号
        
        对于非二进制符号，使用简单的映射方案
        """
        # 简单映射: 将GF(2^m)元素映射到实数
        modulated = np.zeros(len(symbols))
        for i, sym in enumerate(symbols):
            # 映射到[-1, 1]区间
            modulated[i] = (sym / (gf.size - 1)) * 2 - 1
        
        return modulated
    
    def _demodulate(self, received: np.ndarray, gf: GaloisField) -> List[int]:
        """
        解调得到GF符号的硬判决
        """
        hard_decision = []
        for r in received:
            # 反向映射
            symbol = int((r + 1) / 2 * (gf.size - 1))
            symbol = np.clip(symbol, 0, gf.size - 1)
            hard_decision.append(symbol)
        
        return hard_decision
    
    def _compute_soft_info(self, received: np.ndarray, transmitted: np.ndarray) -> np.ndarray:
        """
        计算软信息（可靠性度量）
        """
        # 基于接收信号与发送信号的距离
        soft_info = 1.0 / (1.0 + np.abs(received - transmitted))
        return soft_info


class BinarySymmetricChannel:
    """
    二进制对称信道(BSC)
    """
    
    def __init__(self, error_prob: float):
        """
        初始化BSC信道
        
        参数:
            error_prob: 比特错误概率
        """
        self.error_prob = error_prob
    
    def transmit(self, codeword: List[int], gf: GaloisField) -> List[int]:
        """
        通过BSC信道传输
        
        参数:
            codeword: 发送的码字
            gf: 伽罗华域
        
        返回:
            接收到的码字
        """
        received = codeword.copy()
        
        for i in range(len(received)):
            # 以概率error_prob添加错误
            if np.random.random() < self.error_prob:
                # 随机选择一个错误值（非零）
                error_value = np.random.randint(1, gf.size)
                received[i] = gf.add(received[i], error_value)
        
        return received


class PerformanceSimulator:
    """
    性能仿真器，用于评估不同解码算法的性能
    """
    
    def __init__(self, code, decoder_type: str = 'HISS'):
        """
        初始化仿真器
        
        参数:
            code: 循环码实例
            decoder_type: 解码器类型 ('HISS' 或 'SISS')
        """
        self.code = code
        self.gf = code.gf
        
        # 创建解码器
        if decoder_type == 'HISS':
            self.decoder = HISSDecoder(code)
        elif decoder_type == 'SISS':
            self.decoder = SISSDecoder(code)
        else:
            raise ValueError(f"未知的解码器类型: {decoder_type}")
        
        self.decoder_type = decoder_type
    
    def simulate_ber_vs_snr(self, snr_range: List[float], 
                           num_trials: int = 1000) -> Tuple[List[float], List[float]]:
        """
        仿真误码率(BER)与信噪比(SNR)的关系
        
        参数:
            snr_range: SNR范围(dB)
            num_trials: 每个SNR点的试验次数
        
        返回:
            (SNR列表, BER列表)
        """
        ber_results = []
        
        for snr_db in snr_range:
            print(f"仿真 SNR = {snr_db} dB...")
            
            channel = AWGNChannel(snr_db)
            total_bits = 0
            error_bits = 0
            
            for trial in range(num_trials):
                # 生成随机消息
                message = [np.random.randint(0, self.gf.size) for _ in range(self.code.k)]
                
                # 编码
                codeword = self.code.encode(message)
                
                # 通过信道传输
                if self.decoder_type == 'SISS':
                    received, soft_info = channel.transmit(codeword, self.gf)
                    decoded = self.decoder.decode(received, soft_info)
                else:
                    received, _ = channel.transmit(codeword, self.gf)
                    decoded = self.decoder.decode(received)
                
                # 计算错误
                for i in range(len(codeword)):
                    total_bits += 1
                    if decoded[i] != codeword[i]:
                        error_bits += 1
            
            ber = error_bits / total_bits if total_bits > 0 else 0
            ber_results.append(ber)
            print(f"  BER = {ber:.6f}")
        
        return snr_range, ber_results
    
    def simulate_fer_vs_snr(self, snr_range: List[float], 
                           num_trials: int = 1000) -> Tuple[List[float], List[float]]:
        """
        仿真帧错误率(FER)与信噪比(SNR)的关系
        
        参数:
            snr_range: SNR范围(dB)
            num_trials: 每个SNR点的试验次数
        
        返回:
            (SNR列表, FER列表)
        """
        fer_results = []
        
        for snr_db in snr_range:
            print(f"仿真 SNR = {snr_db} dB...")
            
            channel = AWGNChannel(snr_db)
            total_frames = 0
            error_frames = 0
            
            for trial in range(num_trials):
                # 生成随机消息
                message = [np.random.randint(0, self.gf.size) for _ in range(self.code.k)]
                
                # 编码
                codeword = self.code.encode(message)
                
                # 通过信道传输
                if self.decoder_type == 'SISS':
                    received, soft_info = channel.transmit(codeword, self.gf)
                    decoded = self.decoder.decode(received, soft_info)
                else:
                    received, _ = channel.transmit(codeword, self.gf)
                    decoded = self.decoder.decode(received)
                
                # 检查是否有帧错误
                total_frames += 1
                if decoded != codeword:
                    error_frames += 1
            
            fer = error_frames / total_frames if total_frames > 0 else 0
            fer_results.append(fer)
            print(f"  FER = {fer:.6f}")
        
        return snr_range, fer_results


def run_example_simulation():
    """
    运行示例仿真
    """
    print("=" * 60)
    print("移位求和解码算法仿真示例")
    print("=" * 60)
    
    # 创建RS(8; 7, 3, 5)码
    print("\n创建 RS(8; 7, 3, 5) 码...")
    s = 3  # GF(2^3) = GF(8)
    n = 7
    k = 3
    rs_code = ReedSolomonCode(s, n, k)
    print(f"码参数: n={n}, k={k}, d={rs_code.d}")
    
    # 测试编码
    print("\n测试编码:")
    message = [1, 2, 3]
    print(f"消息: {message}")
    codeword = rs_code.encode(message)
    print(f"码字: {codeword}")
    
    # 测试解码
    print("\n测试HISS解码器:")
    decoder = HISSDecoder(rs_code, num_mwdcs=3, max_iterations=5)
    
    # 添加错误
    received = codeword.copy()
    received[0] = rs_code.gf.add(received[0], 1)  # 在位置0添加错误
    print(f"接收字: {received}")
    
    decoded = decoder.decode(received)
    print(f"解码后: {decoded}")
    print(f"解码{'成功' if decoded == codeword else '失败'}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_example_simulation()
