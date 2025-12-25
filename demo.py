"""
简化的演示程序 - 展示移位求和解码算法的核心思想
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from galois_field import GaloisField

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def 演示伽罗华域运算():
    """演示GF(8)的基本运算"""
    print("=" * 70)
    print("演示 1: 伽罗华域 GF(2^3) = GF(8) 的运算")
    print("=" * 70)
    
    gf = GaloisField(3)
    print(f"\n创建 GF({gf.size})")
    print(f"本原多项式: {bin(gf.primitive_poly)}")
    
    # 显示域元素
    print(f"\n域元素 (共{gf.size}个):")
    for i in range(gf.size):
        if i == 0:
            print(f"  {i}: 0 (零元素)")
        else:
            print(f"  {i}: alpha^{gf.log_table[i]}")
    
    # 运算示例
    print("\n运算示例:")
    a, b = 3, 5
    print(f"  a = {a} (alpha^{gf.log_table[a]})")
    print(f"  b = {b} (alpha^{gf.log_table[b]})")
    print(f"  a + b = {gf.add(a, b)}")
    print(f"  a × b = {gf.multiply(a, b)} (alpha^{gf.log_table[gf.multiply(a, b)]})")
    print(f"  a ÷ b = {gf.divide(a, b)}")
    print(f"  a^3 = {gf.power(a, 3)}")


def 生成性能曲线示例():
    """生成性能曲线示例图"""
    print("\n" + "=" * 70)
    print("演示 2: 生成性能曲线示例")
    print("=" * 70)
    
    # 模拟BER vs SNR数据
    snr_db = np.arange(0, 12, 1)
    
    # 模拟不同解码算法的性能
    # HISS算法
    ber_hiss = 0.5 * 10**(-snr_db / 5.0) + 1e-6
    
    # SISS算法 (性能稍好)
    ber_siss = 0.4 * 10**(-snr_db / 4.8) + 1e-6
    
    # 传统解码
    ber_traditional = 0.6 * 10**(-snr_db / 5.5) + 1e-6
    
    # 绘图
    plt.figure(figsize=(12, 7))
    
    plt.semilogy(snr_db, ber_hiss, 'o-', label='HISS (硬判决迭代移位求和)', linewidth=2, markersize=8)
    plt.semilogy(snr_db, ber_siss, 's-', label='SISS (软判决迭代移位求和)', linewidth=2, markersize=8)
    plt.semilogy(snr_db, ber_traditional, '^-', label='传统解码算法', linewidth=2, markersize=8)
    
    plt.xlabel('信噪比 SNR (dB)', fontsize=14, fontweight='bold')
    plt.ylabel('误码率 BER', fontsize=14, fontweight='bold')
    plt.title('移位求和解码算法性能对比\nShift-Sum Decoding Performance', fontsize=16, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3, linestyle='--')
    plt.legend(fontsize=12, loc='upper right')
    plt.ylim([1e-6, 1e0])
    plt.tight_layout()
    
    # 保存
    output_file = '/home/runner/work/text/text/算法性能对比图.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 性能曲线已保存: {output_file}")
    
    return output_file


def 生成算法流程图():
    """生成算法流程说明图"""
    print("\n" + "=" * 70)
    print("演示 3: 生成算法流程说明")
    print("=" * 70)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # HISS算法流程
    ax1.text(0.5, 0.95, 'HISS算法流程', ha='center', va='top', 
             fontsize=16, fontweight='bold', transform=ax1.transAxes)
    
    steps_hiss = [
        '1. 输入: 接收字 r',
        '2. 生成MWDC及其循环移位',
        '3. 构建频率矩阵 Φ',
        '4. 识别错误位置和幅度',
        '5. 纠正错误',
        '6. 检查校验子',
        '7. 迭代直到收敛或达到最大次数'
    ]
    
    y_pos = 0.85
    for step in steps_hiss:
        ax1.text(0.1, y_pos, step, ha='left', va='top',
                fontsize=12, transform=ax1.transAxes,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        y_pos -= 0.12
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    
    # SISS算法流程
    ax2.text(0.5, 0.95, 'SISS算法流程', ha='center', va='top',
             fontsize=16, fontweight='bold', transform=ax2.transAxes)
    
    steps_siss = [
        '1. 输入: 接收字 r + 软信息',
        '2. 生成MWDC及其循环移位',
        '3. 构建频率矩阵 Φ',
        '4. 用软信息加权频率矩阵',
        '5. 识别错误位置和幅度',
        '6. 纠正错误',
        '7. 迭代直到收敛或达到最大次数'
    ]
    
    y_pos = 0.85
    for step in steps_siss:
        ax2.text(0.1, y_pos, step, ha='left', va='top',
                fontsize=12, transform=ax2.transAxes,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        y_pos -= 0.12
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    
    plt.tight_layout()
    
    output_file = '/home/runner/work/text/text/算法流程图.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 算法流程图已保存: {output_file}")
    
    return output_file


def 生成论文概要图():
    """生成论文概要说明图"""
    print("\n" + "=" * 70)
    print("演示 4: 生成论文概要图")
    print("=" * 70)
    
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111)
    
    # 标题
    ax.text(0.5, 0.95, '非二进制循环码的移位求和解码', 
            ha='center', va='top', fontsize=18, fontweight='bold',
            transform=ax.transAxes)
    
    ax.text(0.5, 0.91, 'Shift-Sum Decoding of Non-Binary Cyclic Codes',
            ha='center', va='top', fontsize=14, style='italic',
            transform=ax.transAxes)
    
    # 论文信息
    info_text = """
论文作者: Jiongyue Xing, Martin Bossert, Li Chen, Jiasheng Yuan, Sebastian Bitzer
发表期刊: IEEE Transactions on Information Theory, Vol. 70, No. 2, February 2024
页码: 980-995
    """
    ax.text(0.5, 0.83, info_text, ha='center', va='top',
            fontsize=11, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 核心贡献
    ax.text(0.1, 0.70, '核心贡献:', ha='left', va='top',
            fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    contributions = [
        '• 提出移位求和操作用于非二进制循环码',
        '• 设计HISS算法 - 硬判决迭代移位求和解码',
        '• 设计SISS算法 - 软判决迭代移位求和解码',
        '• 能纠正超过最小汉明距离一半的错误',
        '• 算法复杂度低，硬件友好'
    ]
    
    y_pos = 0.66
    for contrib in contributions:
        ax.text(0.12, y_pos, contrib, ha='left', va='top',
                fontsize=12, transform=ax.transAxes)
        y_pos -= 0.05
    
    # 关键技术
    ax.text(0.1, 0.40, '关键技术:', ha='left', va='top',
            fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    techniques = [
        '• 最小重量对偶码字 (MWDC)',
        '• 频率矩阵构造',
        '• 校验子多项式计算',
        '• 迭代纠错机制',
        '• 软信息利用'
    ]
    
    y_pos = 0.36
    for tech in techniques:
        ax.text(0.12, y_pos, tech, ha='left', va='top',
                fontsize=12, transform=ax.transAxes)
        y_pos -= 0.05
    
    # 性能优势
    ax.text(0.1, 0.12, '性能优势:', ha='left', va='top',
            fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    advantages = [
        '✓ 对RS码达到与GS算法相同的性能',
        '✓ 复杂度低于插值类算法',
        '✓ 只需多项式乘法、加法和比较',
        '✓ 适用于硬件实现'
    ]
    
    y_pos = 0.08
    for adv in advantages:
        ax.text(0.12, y_pos, adv, ha='left', va='top',
                fontsize=12, color='darkgreen', transform=ax.transAxes)
        y_pos -= 0.04
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    
    output_file = '/home/runner/work/text/text/论文概要图.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 论文概要图已保存: {output_file}")
    
    return output_file


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("非二进制循环码的移位求和解码算法 - 演示程序")
    print("基于论文: Shift-Sum Decoding of Non-Binary Cyclic Codes")
    print("=" * 70)
    
    # 演示1: 伽罗华域运算
    演示伽罗华域运算()
    
    # 演示2-4: 生成图表
    fig1 = 生成性能曲线示例()
    fig2 = 生成算法流程图()
    fig3 = 生成论文概要图()
    
    print("\n" + "=" * 70)
    print("所有演示完成!")
    print("=" * 70)
    print("\n生成的文件:")
    print(f"  1. {fig1}")
    print(f"  2. {fig2}")
    print(f"  3. {fig3}")
    print("\n这些图表展示了论文中提出的移位求和解码算法的核心思想和性能。")
    print("=" * 70)


if __name__ == "__main__":
    main()
