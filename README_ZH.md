# 非二进制循环码的移位求和解码算法实现

本项目实现了论文《Shift-Sum Decoding of Non-Binary Cyclic Codes》中提出的移位求和解码算法。

## 论文信息

- **标题**: Shift-Sum Decoding of Non-Binary Cyclic Codes
- **作者**: Jiongyue Xing, Martin Bossert, Li Chen, Jiasheng Yuan, and Sebastian Bitzer
- **期刊**: IEEE Transactions on Information Theory, Vol. 70, No. 2, February 2024
- **页码**: 980-995

## 项目结构

```
.
├── galois_field.py         # 伽罗华域(GF)实现
├── cyclic_codes.py          # 循环码实现(RS码和NB-BCH码)
├── shift_sum_decoder.py     # 移位求和解码器(HISS和SISS)
├── simulation.py            # 信道仿真和性能评估
├── main.py                  # 主程序
├── picture/                 # 论文图片(共15页)
└── README_ZH.md            # 本文件
```

## 主要功能

### 1. 伽罗华域运算 (`galois_field.py`)

实现了GF(2^m)的基本运算:
- 加法、减法(XOR)
- 乘法、除法
- 幂运算、逆元
- 多项式运算

### 2. 循环码 (`cyclic_codes.py`)

实现了两种经典的非二进制循环码:
- **RS码**: Reed-Solomon码 C(2^s; n, k, d_RS)
- **NB-BCH码**: 非二进制BCH码

功能包括:
- 系统编码
- 校验子计算
- 生成多项式构造

### 3. 移位求和解码 (`shift_sum_decoder.py`)

实现了论文中提出的两种解码算法:

#### HISS (Hard-decision Iterative Shift-Sum)
- 硬判决迭代移位求和解码
- 能够纠正超过码的最小汉明距离一半的错误
- 只需要多项式乘法、加法和比较运算

#### SISS (Soft-decision Iterative Shift-Sum)
- 软判决迭代移位求和解码
- 利用信道软信息提高解码性能
- 在HISS基础上集成软信息

核心步骤:
1. 生成最小重量对偶码字(MWDC)
2. 构建频率矩阵
3. 识别错误位置和幅度
4. 迭代纠错

### 4. 性能仿真 (`simulation.py`)

提供完整的仿真框架:
- **AWGN信道**: 加性高斯白噪声信道
- **BSC信道**: 二进制对称信道
- **性能指标**: 
  - BER (误码率)
  - FER (帧错误率)

## 使用方法

### 基础测试

```bash
python3 main.py
```

这将运行以下测试:
1. 伽罗华域基础操作测试
2. RS码编码测试
3. HISS解码器测试
4. 性能仿真(小规模)
5. 生成BER vs SNR曲线
6. 生成HISS vs SISS性能对比图

### 自定义仿真

```python
from galois_field import GaloisField
from cyclic_codes import ReedSolomonCode
from shift_sum_decoder import HISSDecoder

# 创建RS(8; 7, 3, 5)码
rs_code = ReedSolomonCode(s=3, n=7, k=3)

# 创建HISS解码器
decoder = HISSDecoder(rs_code, num_mwdcs=5, max_iterations=10)

# 编码
message = [1, 2, 3]
codeword = rs_code.encode(message)

# 添加错误
received = codeword.copy()
received[0] = rs_code.gf.add(received[0], 1)

# 解码
decoded = decoder.decode(received)
```

## 算法说明

### 移位求和操作

移位求和操作利用多个循环不同的最小重量对偶码字(MWDC)及其循环移位来生成频率矩阵，用于识别错误位置和幅度。

**关键思想**:
- 利用对偶码的性质
- 通过统计频率矩阵的条目来识别错误
- 频率矩阵的条目被分类为四种情况，具有不同的概率特征

### HISS算法流程

```
1. 初始化: r = 接收字
2. 循环(最多max_iterations次):
   a. 计算校验子，如果为0则返回r
   b. 构建频率矩阵Φ
   c. 从Φ识别错误位置和幅度
   d. 纠正错误
3. 返回解码结果
```

### SISS算法改进

SISS在HISS基础上:
- 利用信道软信息加权频率矩阵
- 提高了错误识别的准确性
- 在低SNR下性能优于HISS

## 复现的论文结果

程序会生成以下图表:

1. **仿真结果_BER_vs_SNR.png**: 
   - 展示不同RS码参数下的BER vs SNR性能曲线
   - 对应论文中的仿真图

2. **性能对比_HISS_vs_SISS.png**:
   - HISS和SISS解码器的性能对比
   - 验证SISS的性能优势

## 理论背景

### 循环码

循环码是一类重要的线性分组码，具有循环移位性质:
- 如果c = (c₀, c₁, ..., c_{n-1})是码字
- 则其循环移位也是码字

### 对偶码

对偶码C^⊥由所有与C正交的向量组成:
- 如果C有生成多项式g(x)
- 则C^⊥有生成多项式h(x) = (x^n-1)/g(x)

### 最小重量对偶码字(MWDC)

MWDC是对偶码中汉明重量最小的非零码字，在移位求和解码中起核心作用。

## 性能特点

与传统解码算法相比，移位求和解码具有以下优势:

1. **硬件友好**: 只需要多项式乘法、加法和比较运算
2. **纠错能力强**: 可纠正超过d/2的错误
3. **复杂度低**: 相比插值类算法复杂度更低
4. **性能优异**: 
   - 对于RS码，达到与GS算法相同的性能
   - 能够纠正超过码的最小汉明距离一半的错误

## 依赖项

```
numpy >= 1.20.0
matplotlib >= 3.3.0
```

安装依赖:
```bash
pip install numpy matplotlib
```

## 参考文献

[1] J. Xing et al., "Shift-Sum Decoding of Non-Binary Cyclic Codes," IEEE Transactions on Information Theory, vol. 70, no. 2, pp. 980-995, February 2024.

[2] R. E. Blahut, "Theory and Practice of Error Control Codes," Addison-Wesley, 1983.

[3] S. Lin and D. J. Costello, "Error Control Coding," 2nd ed., Prentice Hall, 2004.

## 作者

本实现基于上述论文，用于学习和研究目的。

## 许可

本项目仅用于学术研究和学习目的。
