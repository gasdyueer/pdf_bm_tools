# PDF书签工具 - 命令行版本

基于GUI版本创建的命令行工具，支持PDF书签应用、页面提取、书签查看等功能。

## 功能特性

- **显示PDF信息** (`info`): 显示PDF的基本信息（页数、标题、作者等）
- **应用书签** (`apply`): 将TXT格式的书签应用到PDF文件
- **提取页面** (`extract`): 提取指定页面范围保存为新PDF
- **查看书签** (`view`): 显示PDF中现有的书签结构
- **AI提示词** (`prompt`): 显示用于生成书签的AI提示词

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 显示PDF信息
```bash
python cli.py --pdf document.pdf --operation info
```

### 应用书签
```bash
python cli.py --pdf document.pdf --bookmarks bookmarks.txt --operation apply
```

### 提取页面
```bash
# 提取第1-5页和第8页
python cli.py --pdf document.pdf --pages "1-5,8" --operation extract

# 指定输出文件名
python cli.py --pdf document.pdf --pages "1-5,8" --output extracted.pdf --operation extract
```

### 查看PDF书签
```bash
python cli.py --pdf document.pdf --operation view
```

### 显示AI提示词
```bash
python cli.py --operation prompt
```

## 书签文件格式

支持多种TXT书签格式：

### 格式1（推荐）：
```
1|第一章 引言|1
1|第二章 基础知识|5
2|2.1 基本概念|5
2|2.2 重要定理|8
```

### 格式2：
```
第一章 引言 (1)
第二章 基础知识 (5)
  2.1 基本概念 (5)
  2.2 重要定理 (8)
```

### 格式3（缩进表示层级）：
```
第一章 引言 (1)
第二章 基础知识 (5)
  2.1 基本概念 (5)
  2.2 重要定理 (8)
```

## 页面范围格式

提取页面时支持以下格式：
- `1-5`: 第1到5页
- `8`: 第8页
- `1-3,5,7-9`: 第1-3页、第5页、第7-9页

## 示例

```bash
# 显示帮助信息
python cli.py --help

# 查看PDF信息
python cli.py --pdf example.pdf --operation info

# 应用书签
python cli.py --pdf example.pdf --bookmarks bookmarks.txt --operation apply

# 提取前10页
python cli.py --pdf example.pdf --pages "1-10" --operation extract

# 查看书签
python cli.py --pdf example.pdf --operation view

# 获取AI提示词
python cli.py --operation prompt
```

## 注意事项

1. 确保PDF文件未被其他程序占用
2. 书签页码从1开始计数
3. 提取页面时如果不指定输出路径，会自动生成文件名
4. 应用书签时会直接修改原PDF文件
5. 支持加密PDF文件的书签应用（会创建临时文件）