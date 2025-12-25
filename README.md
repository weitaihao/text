# 非二进制循环码的移位求和解码算法

本项目实现了IEEE论文《Shift-Sum Decoding of Non-Binary Cyclic Codes》中提出的移位求和解码算法。

## 论文信息

- **标题**: Shift-Sum Decoding of Non-Binary Cyclic Codes
- **作者**: Jiongyue Xing, Martin Bossert, Li Chen, Jiasheng Yuan, Sebastian Bitzer  
- **期刊**: IEEE Transactions on Information Theory, Vol. 70, No. 2, February 2024
- **页码**: 980-995

## 快速开始

```bash
# 安装依赖
pip install numpy matplotlib

# 运行演示程序
python3 demo.py
```

## 项目结构

- `demo.py` - 演示程序（推荐运行）⭐
- `galois_field.py` - 伽罗华域实现
- `cyclic_codes.py` - 循环码实现  
- `shift_sum_decoder.py` - 解码器实现
- `simulation.py` - 仿真框架
- `picture/` - 论文图片（15页）
- 三张生成的可视化图表

## 文档

- [详细说明](README_ZH.md)
- [运行指南](运行说明.md)
- [项目总结](项目总结.md)

## 核心功能

✅ HISS解码器（硬判决迭代移位求和）  
✅ SISS解码器（软判决迭代移位求和）  
✅ 性能仿真和可视化  
✅ 完整的中文文档
