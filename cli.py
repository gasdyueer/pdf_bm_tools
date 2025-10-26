#!/usr/bin/env python3
"""
PDF书签工具 - 命令行版本
支持PDF书签应用、页面提取、书签查看等功能
"""

import sys
import os
import argparse
import pymupdf
import re
import shutil


def load_pdf_info(pdf_path):
    """加载PDF基本信息"""
    try:
        doc = pymupdf.open(pdf_path)
        info = f"""
PDF基本信息:
文件路径: {pdf_path}
总页数: {doc.page_count}
PDF版本: {getattr(doc.metadata, 'format', '未知')}
标题: {getattr(doc.metadata, 'title', '未知')}
作者: {getattr(doc.metadata, 'creator', '未知')}
主题: {getattr(doc.metadata, 'subject', '未知')}
关键字: {getattr(doc.metadata, 'keywords', '未知')}
创建日期: {getattr(doc.metadata, 'creationDate', '未知')}
修改日期: {getattr(doc.metadata, 'modDate', '未知')}
        """
        print(info.strip())
        doc.close()
        return True
    except Exception as e:
        print(f"加载PDF信息失败: {str(e)}")
        return False


def extract_pages(pdf_path, page_range, output_path):
    """提取指定页面"""
    try:
        # 解析页面范围
        pages = parse_page_range(page_range)
        if not pages:
            print("页面范围格式错误，请使用格式如: 1-5,8,10-12")
            return False

        # 打开PDF文档
        doc = pymupdf.open(pdf_path)

        # 创建新文档
        new_doc = pymupdf.open()

        # 添加指定页面
        for page_num in pages:
            if 0 <= page_num < doc.page_count:
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # 如果未指定输出路径，自动生成
        if not output_path:
            original_dir = os.path.dirname(pdf_path)
            original_basename = os.path.splitext(os.path.basename(pdf_path))[0]

            # 根据提取的页面生成智能文件名
            if len(pages) == 1:
                page_str = f"第{pages[0]+1}页"
            elif len(pages) <= 5:
                page_str = f"第{','.join(str(p+1) for p in pages)}页"
            else:
                page_str = f"第{pages[0]+1}-{pages[-1]+1}页({len(pages)}页)"

            default_filename = f"{original_basename}_{page_str}.pdf"
            output_path = os.path.join(original_dir, default_filename)

        # 保存新文档
        new_doc.save(output_path)
        new_doc.close()
        doc.close()

        print(f"成功提取 {len(pages)} 页，保存至: {output_path}")
        return True

    except Exception as e:
        print(f"页面提取失败: {str(e)}")
        return False


def parse_page_range(page_range):
    """解析页面范围字符串"""
    pages = []
    try:
        # 分割逗号
        parts = page_range.split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                # 处理范围
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                pages.extend(range(start - 1, end))  # 转换为0基索引
            else:
                # 处理单个页面
                pages.append(int(part.strip()) - 1)  # 转换为0基索引

        return sorted(set(pages))  # 去重并排序
    except Exception as e:
        print(f"解析页面范围失败: {e}")
        return []


def apply_bookmarks(pdf_path, bookmark_path):
    """应用书签到PDF"""
    doc = None
    try:
        # 解析书签文件
        bookmarks = parse_bookmark_file(bookmark_path)
        if not bookmarks:
            print("书签文件格式错误或为空")
            return False

        print(f"成功解析 {len(bookmarks)} 个书签，开始应用到PDF...")

        # 打开PDF文档
        doc = pymupdf.open(pdf_path)

        # 使用set_toc方法设置书签
        try:
            doc.set_toc(bookmarks)  # type: ignore
        except (AttributeError, Exception) as e:
            raise Exception(f"无法设置书签：{str(e)}。请确保PyMuPDF版本支持set_toc方法")

        # 保存PDF文档（处理加密文件）
        try:
            # 尝试增量更新
            doc.save(pdf_path, incremental=True)
        except Exception as save_error:
            if "encryption" in str(save_error).lower():
                # 如果是加密问题，创建临时文件然后替换
                temp_path = pdf_path + ".tmp"
                doc.save(temp_path)
                doc.close()

                # 替换原文件
                shutil.move(temp_path, pdf_path)
                print(f"成功应用 {len(bookmarks)} 个书签到PDF文件（已处理加密文件）")
                return True
            else:
                raise save_error

        doc.close()
        doc = None

        print(f"成功应用 {len(bookmarks)} 个书签到PDF文件")
        return True

    except Exception as e:
        print(f"应用书签失败: {str(e)}")
        return False
    finally:
        # 确保文档被正确关闭
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def parse_bookmark_file(bookmark_path):
    """解析书签TXT文件"""
    bookmarks = []
    try:
        with open(bookmark_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # 解析层级和标题
            level = 0
            title = ""
            page = 1

            # 尝试匹配不同格式
            # 格式1: 层级|标题|页码
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    level = int(parts[0].strip())  # 保持1基索引（PyMuPDF要求）
                    title = parts[1].strip()
                    page = int(parts[2].strip())  # 页码保持1基索引（PyMuPDF要求）
            # 格式2: 标题 (页码)
            elif '(' in line and ')' in line:
                # 找到最后一个括号对
                paren_start = line.rfind('(')
                paren_end = line.rfind(')')
                if paren_start < paren_end:
                    title = line[:paren_start].strip()
                    page_str = line[paren_start + 1:paren_end].strip()
                    page = int(page_str)  # 页码保持1基索引（PyMuPDF要求）
                    level = 1  # 默认层级为1
            # 格式3: 缩进表示层级
            else:
                # 计算缩进层级
                indent_count = 0
                for char in line:
                    if char == ' ':
                        indent_count += 1
                    elif char == '\t':
                        indent_count += 4
                    else:
                        break
                level = (indent_count // 2) + 1  # 每2个空格为一级，从1开始
                title = line.strip()

                # 尝试从标题中提取页码
                page_match = re.search(r'\((\d+)\)$', title)
                if page_match:
                    page = int(page_match.group(1))
                    title = title[:page_match.start()].strip()
                else:
                    page = 1  # 默认第一页

            if title:  # 只有当标题不为空时才添加
                bookmarks.append([level, title, page])

        return bookmarks
    except Exception as e:
        print(f"解析书签文件失败: {str(e)}")
        return []


def view_pdf_bookmarks(pdf_path):
    """查看PDF书签信息"""
    doc = None
    try:
        doc = pymupdf.open(pdf_path)

        # 获取PDF书签
        toc = []
        try:
            toc = doc.get_toc() # type: ignore
        except (AttributeError, Exception):
            try:
                toc = doc.get_toc() # type: ignore
            except (AttributeError, Exception):
                try:
                    outline = doc.outline
                    if outline:
                        toc = []
                        def extract_outline_items(outline_obj, level=1):
                            items = []
                            if hasattr(outline_obj, '__iter__'):
                                for item in outline_obj:
                                    if hasattr(item, 'title') and hasattr(item, 'page'):
                                        title = getattr(item, 'title', '')
                                        page = getattr(item, 'page', 0)
                                        if title:
                                            items.append([level, title, page])
                                        # 递归处理子项目
                                        if hasattr(item, 'down') and item.down:
                                            items.extend(extract_outline_items(item.down, level + 1))
                            return items

                        toc = extract_outline_items(outline)
                except Exception:
                    toc = []

        if not toc:
            print("此PDF文档没有书签信息。")
            return False

        # 格式化书签信息
        print("PDF书签信息：\n")

        for i, (level, title, page) in enumerate(toc, 1):
            indent = "  " * (level - 1)  # 根据层级计算缩进
            print(f"{i:2d}. {indent}{title} (第{page}页)")

        print(f"\n总计: {len(toc)} 个书签")
        return True

    except Exception as e:
        print(f"查看书签失败: {str(e)}")
        return False
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def show_ai_prompt():
    """显示AI提示词"""
    prompt_text = """请分析这个PDF文档，为我生成一个书签TXT文件。书签应该按照以下格式组织：

格式1（推荐）：
1|第一章 引言|1
1|第二章 基础知识|5
2|2.1 基本概念|5
2|2.2 重要定理|8
1|第三章 高级主题|12
2|3.1 高级概念|12
3|3.1.1 详细说明|12
3|3.1.2 应用实例|15
1|第四章 总结|20

格式说明：
- 每行一个书签
- 格式：层级|标题|页码
- 层级从1开始，1表示顶级，2表示二级，以此类推
- 页码从1开始，表示该书签指向的页面

或者使用格式2：
第一章 引言 (1)
第二章 基础知识 (5)
  2.1 基本概念 (5)
  2.2 重要定理 (8)
第三章 高级主题 (12)
  3.1 高级概念 (12)
    3.1.1 详细说明 (12)
    3.1.2 应用实例 (15)
第四章 总结 (20)

请确保：
1. 正确识别文档结构和章节层级
2. 准确识别每个章节的起始页码
3. 保持逻辑的层次结构
4. 标题要简洁明了"""

    print("请复制下面的提示词，然后将PDF文件一起提供给AI：\n")
    print(prompt_text)


def main():
    parser = argparse.ArgumentParser(description="PDF书签工具 - 命令行版本")
    parser.add_argument('--pdf', help='PDF文件路径')
    parser.add_argument('--bookmarks', help='书签TXT文件路径')
    parser.add_argument('--operation', choices=['info', 'apply', 'extract', 'view', 'prompt'],
                       help='操作类型: info(显示PDF信息), apply(应用书签), extract(提取页面), view(查看书签), prompt(显示AI提示词)')
    parser.add_argument('--pages', help='要提取的页面范围 (例如: 1-5,8,10-12)')
    parser.add_argument('--output', help='输出文件路径 (用于提取页面)')

    args = parser.parse_args()

    if args.operation == 'prompt':
        show_ai_prompt()
        return

    if not args.pdf and args.operation != 'prompt':
        parser.error("--pdf 参数是必需的，除非操作是 prompt")

    if args.operation == 'info':
        if not load_pdf_info(args.pdf):
            sys.exit(1)
    elif args.operation == 'apply':
        if not args.bookmarks:
            parser.error("--bookmarks 参数是必需的用于 apply 操作")
        if not apply_bookmarks(args.pdf, args.bookmarks):
            sys.exit(1)
    elif args.operation == 'extract':
        if not args.pages:
            parser.error("--pages 参数是必需的用于 extract 操作")
        if not extract_pages(args.pdf, args.pages, args.output):
            sys.exit(1)
    elif args.operation == 'view':
        if not view_pdf_bookmarks(args.pdf):
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()