# Ciphey

本项目是在https://github.com/bee-san/Ciphey的基础上进行改进的。
Ciphey 是一款使用人工智能和自然语言处理技术的自动化解密工具。输入加密文本，即可获得解密结果。

## 功能特点

- **自动化解密**：自动识别和解密多种加密和编码格式
- **智能识别**：使用 AI 技术智能判断解密结果的有效性
- **多格式支持**：支持多种加密和编码格式
- **中文支持**：特别优化支持中文文本解密

## 安装要求

- Python 3.6+
- Windows、Linux 或 macOS 操作系统

## 安装方法

```bash
pip install ciphey
```

## 使用方法

### 基本用法

```bash
# 解密文本
ciphey -t "your_encrypted_text_here"

# 解密文件
ciphey -f path/to/your/file.txt

# 详细输出
ciphey -t "encrypted_text" -v
```

### 命令行选项

- `-t, --text TEXT`：要解密的文本
- `-f, --file FILENAME`：要解密的文件
- `-v, --verbose`：增加输出详细程度
- `-q, --quiet`：减少输出详细程度
- `-g, --greppable`：仅输出结果（便于管道操作）
- `-C, --checker CHECKER`：指定使用的检查器
- `-c, --config PATH`：指定配置文件
- `-w, --wordlist PATH`：指定词典文件
- `-l, --list-params`：列出所选模块的参数
- `--searcher SEARCHER`：指定搜索算法

### 示例

```bash
# 解密简单的Base64编码
ciphey -t "aGVsbG8gd29ybGQ="

# 解密文件
ciphey -f ./encrypted_file.txt

# 使用详细模式解密
ciphey -t "encrypted_text" -vvv

# 解密URL编码的中文文本
ciphey -t "%E4%BD%A0%E5%A5%BD%E4%B8%96%E7%95%8C" -v
```

## 支持的编码格式

Ciphey 支持以下编码和加密格式：

- **编码格式**：
  - Base64, Base32, Base16
  - URL 编码（包括 `=XX` 格式）
  - 十六进制编码
  - 八进制编码
  - Base58 (Bitcoin, Flickr, Ripple)
  - ASCII85, Base85
  - 二进制编码
  - 更多编码格式...

- **加密格式**：
  - Caesar 密码
  - ROT47
  - Affine 密码
  - Vigenère 密码
  - Atbash 密码
  - 更多加密格式...

- **其他格式**：
  - 摩尔斯电码
  - Leet Speak
  - Tap Code
  - Reverse 文本
  - DNA 编码
  - 当铺密码（汉字转数字再转ASCII）
  - 元素周期表（原子序数转元素符号）
  - 等等...

## 特殊功能

### 中文文本支持

Ciphey 特别增强了对中文文本的支持，能够正确解密：

- URL编码的中文文本（如 `=E7=94=A8=...` 格式）
- 其他编码格式的中文文本
- 当铺密码（汉字笔画出头数转数字再转ASCII）

### 自动验证

Ciphey 使用多种验证方法确保解密结果的准确性：

- **Quadgrams 分析**：分析字符组合频率
- **Unicode 检查器**：验证中文等非英语文本
- **语法检查**：验证结果的语法有效性
- **用户交互**：必要时请求用户确认

## 配置

### 默认配置

Ciphey 会在用户配置目录中创建默认配置文件。您可以根据需要修改配置以优化性能。

### 自定义配置

通过 `-c` 参数指定自定义配置文件：

```bash
ciphey -t "encrypted_text" -c /path/to/config.yml
```

## 高级用法

### 指定解密器

```bash
# 强制使用特定解密器
ciphey -t "text" --param decoder.type=url
```

### 调整搜索策略

```bash
# 使用特定搜索算法
ciphey -t "text" --searcher astar
```

### 批量处理

```bash
# 处理多个文件
for file in *.enc; do
  ciphey -f "$file" -g > "${file%.enc}.txt"
done
```

## 故障排除

### 常见问题

1. **Python 版本问题**：确保使用 Python 3.6+ 版本
2. **权限问题**：确保对输入文件有读取权限
3. **内存不足**：对于大文件，可能需要更多内存

### 调试模式

使用详细模式来调试问题：

```bash
ciphey -t "problematic_text" -vvv
```

## 开发与贡献

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/Ciphey/Ciphey.git
cd Ciphey

# 安装依赖
pip install -e .

# 运行测试
pytest
```

### 添加新解密器

要添加新的解密器，请参考 `ciphey/basemods/Decoders/` 目录中的示例。

## 性能优化

- **优先级设置**：常用解密器具有更高优先级
- **缓存机制**：避免重复解密相同的文本
- **并行处理**：支持多线程解密（如果启用）

## 注意事项

- 某些解密操作可能需要较长的计算时间
- 对于高度加密的文本，可能无法找到解密方法
- 遵守当地法律法规，合法使用本工具

## 支持与社区

- **Discord**: [http://discord.skerritt.blog](http://discord.skerritt.blog)
- **GitHub**: [https://github.com/Ciphey/Ciphey](https://github.com/Ciphey/Ciphey)
- **文档**: [https://github.com/Ciphey/Ciphey/wiki](https://github.com/Ciphey/Ciphey/wiki)

## 许可证

本项目遵循 MIT 许可证。详情请参阅 LICENSE 文件。

## 更新日志

最新版本增强了对中文文本的解密支持，特别优化了 URL 编码格式（包括 `=XX` 格式）的处理。

---

> © 2026 Ciphey 项目团队