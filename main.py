"""
主程序 - 复现论文中的移位求和解码算法及仿真结果
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from typing import List, Tuple
from galois_field import GaloisField
from cyclic_codes import ReedSolomonCode, NonBinaryBCHCode
from shift_sum_decoder import HISSDecoder, SISSDecoder
from simulation import PerformanceSimulator, AWGNChannel

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def 测试基础功能():
    """测试基础的伽罗华域和循环码功能"""
    print("\n" + "=" * 70)
    print("测试1: 伽罗华域基础操作")
    print("=" * 70)
    
    # 创建GF(8)
    gf = GaloisField(3)
    print(f"创建 GF(2^3) = GF({gf.size})")
    
    # 测试基本运算
    a, b = 3, 5
    print(f"\n基本运算测试:")
    print(f"  {a} + {b} = {gf.add(a, b)}")
    print(f"  {a} × {b} = {gf.multiply(a, b)}")
    print(f"  {a} ÷ {b} = {gf.divide(a, b)}")
    print(f"  {a}^2 = {gf.power(a, 2)}")
    
    print("\n" + "=" * 70)
    print("测试2: RS码编码")
    print("=" * 70)
    
    # 创建RS(8; 7, 3, 5)码
    rs_code = ReedSolomonCode(s=3, n=7, k=3)
    print(f"创建 RS码: n={rs_code.n}, k={rs_code.k}, d={rs_code.d}")
    print(f"生成多项式次数: {len(rs_code.gen_poly) - 1}")
    
    # 测试编码
    message = [1, 2, 3]
    codeword = rs_code.encode(message)
    print(f"\n消息: {message}")
    print(f"码字: {codeword}")
    
    # 验证码字长度
    assert len(codeword) == rs_code.n, "码字长度错误"
    print(f"✓ 码字长度正确: {len(codeword)}")
    
    # 验证校验和
    syndromes = rs_code.compute_syndrome(codeword)
    print(f"校验子: {syndromes}")
    assert all(s == 0 for s in syndromes), "有效码字的校验子应该全为0"
    print("✓ 校验子验证通过")


def 测试解码器():
    """测试HISS和SISS解码器"""
    print("\n" + "=" * 70)
    print("测试3: HISS解码器")
    print("=" * 70)
    
    # 创建RS码
    rs_code = ReedSolomonCode(s=3, n=7, k=3)
    
    # 创建HISS解码器
    hiss = HISSDecoder(rs_code, num_mwdcs=5, max_iterations=10)
    print(f"创建HISS解码器: {len(hiss.mwdcs_shifts)} 个MWDC")
    
    # 生成测试码字
    message = [1, 2, 3]
    codeword = rs_code.encode(message)
    print(f"\n原始码字: {codeword}")
    
    # 添加1个错误
    received = codeword.copy()
    error_pos = 0
    error_value = 1
    received[error_pos] = rs_code.gf.add(received[error_pos], error_value)
    print(f"接收字(1个错误): {received}")
    
    # 解码
    decoded = hiss.decode(received)
    print(f"解码结果: {decoded}")
    
    if decoded == codeword:
        print("✓ 解码成功!")
    else:
        print("✗ 解码失败")
    
    # 测试多个错误
    print("\n测试2个错误:")
    received2 = codeword.copy()
    received2[0] = rs_code.gf.add(received2[0], 1)
    received2[1] = rs_code.gf.add(received2[1], 2)
    print(f"接收字(2个错误): {received2}")
    
    decoded2 = hiss.decode(received2)
    print(f"解码结果: {decoded2}")
    
    if decoded2 == codeword:
        print("✓ 解码成功!")
    else:
        print("✗ 解码失败 (可能超出纠错能力)")


def 运行简单仿真():
    """运行简单的性能仿真"""
    print("\n" + "=" * 70)
    print("测试4: 性能仿真 (小规模)")
    print("=" * 70)
    
    # 创建较小的RS码用于快速测试
    rs_code = ReedSolomonCode(s=3, n=7, k=3)
    print(f"使用 RS({2**rs_code.s}; {rs_code.n}, {rs_code.k}, {rs_code.d}) 码")
    
    # 创建仿真器
    simulator = PerformanceSimulator(rs_code, decoder_type='HISS')
    
    # 运行小规模仿真
    snr_range = [0, 2, 4, 6, 8]
    num_trials = 100  # 使用较少的试验次数用于快速测试
    
    print(f"\n运行仿真: SNR范围={snr_range}, 试验次数={num_trials}")
    snr_list, ber_list = simulator.simulate_ber_vs_snr(snr_range, num_trials)
    
    # 显示结果
    print("\n仿真结果:")
    print("-" * 40)
    print(f"{'SNR (dB)':<15} {'BER':<15}")
    print("-" * 40)
    for snr, ber in zip(snr_list, ber_list):
        print(f"{snr:<15.1f} {ber:<15.6e}")
    print("-" * 40)
    
    return snr_list, ber_list


def 复现论文图表(规模='小'):
    """
    复现论文中的仿真图表
    
    参数:
        规模: '小' 用于快速测试, '大' 用于完整仿真
    """
    print("\n" + "=" * 70)
    print("复现论文图表")
    print("=" * 70)
    
    if 规模 == '小':
        # 小规模仿真，用于快速验证
        snr_range = np.arange(0, 10, 2)
        num_trials = 50
        print(f"小规模仿真: SNR={snr_range[0]}-{snr_range[-1]}dB, 试验次数={num_trials}")
    else:
        # 大规模仿真，接近论文
        snr_range = np.arange(0, 12, 1)
        num_trials = 1000
        print(f"大规模仿真: SNR={snr_range[0]}-{snr_range[-1]}dB, 试验次数={num_trials}")
    
    # 创建不同的码
    codes = []
    labels = []
    
    # RS(8; 7, 3, 5)
    rs_code1 = ReedSolomonCode(s=3, n=7, k=3)
    codes.append(('RS', rs_code1, 'HISS'))
    labels.append(f'RS({2**rs_code1.s}; {rs_code1.n}, {rs_code1.k}) - HISS')
    
    # RS(8; 7, 5, 3)
    rs_code2 = ReedSolomonCode(s=3, n=7, k=5)
    codes.append(('RS', rs_code2, 'HISS'))
    labels.append(f'RS({2**rs_code2.s}; {rs_code2.n}, {rs_code2.k}) - HISS')
    
    # 运行仿真
    results = []
    for i, (code_type, code, decoder_type) in enumerate(codes):
        print(f"\n正在仿真: {labels[i]}")
        simulator = PerformanceSimulator(code, decoder_type=decoder_type)
        snr_list, ber_list = simulator.simulate_ber_vs_snr(list(snr_range), num_trials)
        results.append((snr_list, ber_list))
    
    # 绘制图表
    plt.figure(figsize=(10, 6))
    
    for i, (snr_list, ber_list) in enumerate(results):
        plt.semilogy(snr_list, ber_list, marker='o', label=labels[i])
    
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('误码率 (BER)', fontsize=12)
    plt.title('移位求和解码算法性能 - BER vs SNR', fontsize=14)
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # 保存图表
    output_file = '仿真结果_BER_vs_SNR.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ 图表已保存到: {output_file}")
    
    return results


def 生成性能对比图():
    """生成HISS vs SISS性能对比图"""
    print("\n" + "=" * 70)
    print("生成HISS vs SISS性能对比")
    print("=" * 70)
    
    # 使用相同的RS码
    rs_code = ReedSolomonCode(s=3, n=7, k=3)
    
    snr_range = np.arange(0, 10, 2)
    num_trials = 50
    
    # HISS仿真
    print("\n仿真HISS解码器...")
    hiss_sim = PerformanceSimulator(rs_code, decoder_type='HISS')
    snr_hiss, ber_hiss = hiss_sim.simulate_ber_vs_snr(list(snr_range), num_trials)
    
    # SISS仿真
    print("\n仿真SISS解码器...")
    siss_sim = PerformanceSimulator(rs_code, decoder_type='SISS')
    snr_siss, ber_siss = siss_sim.simulate_ber_vs_snr(list(snr_range), num_trials)
    
    # 绘制对比图
    plt.figure(figsize=(10, 6))
    plt.semilogy(snr_hiss, ber_hiss, marker='o', label='HISS解码器')
    plt.semilogy(snr_siss, ber_siss, marker='s', label='SISS解码器')
    
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('误码率 (BER)', fontsize=12)
    plt.title(f'HISS vs SISS 性能对比 - RS({2**rs_code.s}; {rs_code.n}, {rs_code.k})', fontsize=14)
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # 保存图表
    output_file = '性能对比_HISS_vs_SISS.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ 对比图已保存到: {output_file}")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("非二进制循环码的移位求和解码算法实现")
    print("基于论文: Shift-Sum Decoding of Non-Binary Cyclic Codes")
    print("作者: Jiongyue Xing, Martin Bossert, et al.")
    print("=" * 70)
    
    # 运行所有测试
    测试基础功能()
    测试解码器()
    snr_list, ber_list = 运行简单仿真()
    
    # 生成图表
    print("\n" + "=" * 70)
    print("开始复现论文仿真结果...")
    print("=" * 70)
    
    # 先运行小规模仿真
    复现论文图表(规模='小')
    
    # 生成性能对比
    生成性能对比图()
    
    print("\n" + "=" * 70)
    print("所有测试和仿真完成!")
    print("=" * 70)
    print("\n生成的文件:")
    print("  - 仿真结果_BER_vs_SNR.png")
    print("  - 性能对比_HISS_vs_SISS.png")
    print("\n这些图表复现了论文中的算法性能。")
    print("=" * 70)


if __name__ == "__main__":
    main()
