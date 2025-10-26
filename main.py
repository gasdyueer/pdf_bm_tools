import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog,
                               QTextEdit, QLineEdit, QMessageBox, QGroupBox,
                               QFormLayout, QDialog)
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import pymupdf
import re


class PDFBookmarkTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_path = ""
        self.bookmark_path = ""
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PDF书签工具")
        self.setGeometry(100, 100, 800, 600)
        self.setAcceptDrops(True)  # 启用拖拽功能

        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QFormLayout()

        self.pdf_label = QLabel("未选择PDF文件")
        self.pdf_button = QPushButton("选择PDF文件")
        self.pdf_button.clicked.connect(self.select_pdf)

        self.bookmark_label = QLabel("未选择书签文件")
        self.bookmark_button = QPushButton("选择书签TXT文件")
        self.bookmark_button.clicked.connect(self.select_bookmark)

        file_layout.addRow(self.pdf_label)
        file_layout.addRow(self.pdf_button)
        file_layout.addRow(self.bookmark_label)
        file_layout.addRow(self.bookmark_button)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # PDF信息显示区域
        info_group = QGroupBox("PDF信息")
        info_layout = QVBoxLayout()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # 功能按钮区域
        button_group = QGroupBox("功能操作")
        button_layout = QHBoxLayout()

        # 页面提取功能
        extract_layout = QVBoxLayout()
        extract_label = QLabel("页面提取（例如：1-5,8,10-12）:")
        self.extract_input = QLineEdit()
        self.extract_button = QPushButton("提取页面")
        self.extract_button.clicked.connect(self.extract_pages)

        extract_layout.addWidget(extract_label)
        extract_layout.addWidget(self.extract_input)
        extract_layout.addWidget(self.extract_button)

        # 书签设置功能
        bookmark_layout = QVBoxLayout()
        self.bookmark_button_apply = QPushButton("应用书签")
        self.bookmark_button_apply.clicked.connect(self.apply_bookmarks)

        self.bookmark_view_button = QPushButton("查看PDF书签")
        self.bookmark_view_button.clicked.connect(self.view_pdf_bookmarks)

        self.edit_bookmark_button = QPushButton("编辑书签TXT")
        self.edit_bookmark_button.clicked.connect(self.edit_bookmark_txt)

        self.offset_input = QLineEdit()
        self.offset_input.setText("0")
        offset_label = QLabel("页码偏移量：")

        bookmark_layout.addWidget(self.bookmark_button_apply)
        bookmark_layout.addWidget(offset_label)
        bookmark_layout.addWidget(self.offset_input)
        bookmark_layout.addWidget(self.bookmark_view_button)
        bookmark_layout.addWidget(self.edit_bookmark_button)

        # 提示词功能
        prompt_layout = QVBoxLayout()
        self.prompt_button = QPushButton("查看AI提示词")
        self.prompt_button.clicked.connect(self.show_ai_prompt)
        prompt_layout.addWidget(self.prompt_button)

        button_layout.addLayout(extract_layout)
        button_layout.addLayout(bookmark_layout)
        button_layout.addLayout(prompt_layout)

        button_group.setLayout(button_layout)
        main_layout.addWidget(button_group)

        # 状态显示区域
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        status_layout.addWidget(self.status_text)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有文件被拖拽
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.pdf', '.txt')):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent):
        """处理文件放置事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    self.pdf_path = file_path
                    self.pdf_label.setText(f"PDF文件: {os.path.basename(file_path)}")
                    self.load_pdf_info()
                    self.status_text.setText(f"已拖拽导入PDF文件: {os.path.basename(file_path)}")
                    break  # 只处理第一个PDF文件
                elif file_path.lower().endswith('.txt'):
                    self.bookmark_path = file_path
                    self.bookmark_label.setText(f"书签文件: {os.path.basename(file_path)}")
                    self.status_text.setText(f"已拖拽导入TXT文件: {os.path.basename(file_path)}")
                    break  # 只处理第一个TXT文件

            event.acceptProposedAction()

    def select_pdf(self):
        """选择PDF文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF files (*.pdf)"
        )
        if file_path:
            self.pdf_path = file_path
            self.pdf_label.setText(f"PDF文件: {os.path.basename(file_path)}")
            self.load_pdf_info()

    def select_bookmark(self):
        """选择书签TXT文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择书签TXT文件", "", "Text files (*.txt)"
        )
        if file_path:
            self.bookmark_path = file_path
            self.bookmark_label.setText(f"书签文件: {os.path.basename(file_path)}")

    def load_pdf_info(self):
        """加载PDF基本信息"""
        try:
            doc = pymupdf.open(self.pdf_path)
            info = f"""
PDF基本信息:
文件路径: {self.pdf_path}
总页数: {doc.page_count}
PDF版本: {getattr(doc.metadata, 'format', '未知')}
标题: {getattr(doc.metadata, 'title', '未知')}
作者: {getattr(doc.metadata, 'creator', '未知')}
主题: {getattr(doc.metadata, 'subject', '未知')}
关键字: {getattr(doc.metadata, 'keywords', '未知')}
创建日期: {getattr(doc.metadata, 'creationDate', '未知')}
修改日期: {getattr(doc.metadata, 'modDate', '未知')}
            """
            self.info_text.setText(info.strip())
            self.status_text.setText("PDF信息加载成功")
            doc.close()
        except Exception as e:
            self.status_text.setText(f"加载PDF信息失败: {str(e)}")

    def extract_pages(self):
        """提取指定页面"""
        if not self.pdf_path:
            QMessageBox.warning(self, "警告", "请先选择PDF文件")
            return

        page_range = self.extract_input.text().strip()
        if not page_range:
            QMessageBox.warning(self, "警告", "请输入要提取的页面范围")
            return

        try:
            # 解析页面范围
            pages = self.parse_page_range(page_range)
            if not pages:
                QMessageBox.warning(self, "警告", "页面范围格式错误，请使用格式如: 1-5,8,10-12")
                return

            # 打开PDF文档
            doc = pymupdf.open(self.pdf_path)

            # 创建新文档
            new_doc = pymupdf.open()

            # 添加指定页面
            for page_num in pages:
                if 0 <= page_num < doc.page_count:
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            # 自动生成保存路径和文件名
            original_dir = os.path.dirname(self.pdf_path)
            original_basename = os.path.splitext(os.path.basename(self.pdf_path))[0]

            # 根据提取的页面生成智能文件名
            if len(pages) == 1:
                page_str = f"第{pages[0]+1}页"
            elif len(pages) <= 5:
                page_str = f"第{','.join(str(p+1) for p in pages)}页"
            else:
                page_str = f"第{pages[0]+1}-{pages[-1]+1}页({len(pages)}页)"

            default_filename = f"{original_basename}_{page_str}.pdf"
            default_path = os.path.join(original_dir, default_filename)

            # 保存新文档
            save_path, _ = QFileDialog.getSaveFileName(
                self, "保存提取的PDF", default_path, "PDF files (*.pdf)"
            )

            if save_path:
                new_doc.save(save_path)
                new_doc.close()
                self.status_text.setText(f"成功提取 {len(pages)} 页，保存至: {save_path}")

            doc.close()

        except Exception as e:
            self.status_text.setText(f"页面提取失败: {str(e)}")

    def parse_page_range(self, page_range):
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

    def apply_bookmarks(self):
        """应用书签到PDF"""
        if not self.pdf_path:
            QMessageBox.warning(self, "警告", "请先选择PDF文件")
            return

        if not self.bookmark_path:
            QMessageBox.warning(self, "警告", "请先选择书签TXT文件")
            return

        doc = None
        try:
            # 解析书签文件
            bookmarks = self.parse_bookmark_file()
            if not bookmarks:
                QMessageBox.warning(self, "警告", "书签文件格式错误或为空")
                return

            # 获取偏移量
            try:
                offset = int(self.offset_input.text().strip()) - 1
            except ValueError:
                QMessageBox.warning(self, "警告", "页码偏移量必须是整数")
                return

            # 显示解析结果
            self.status_text.setText(f"成功解析 {len(bookmarks)} 个书签，开始应用到PDF...")

            # 打开PDF文档
            doc = pymupdf.open(self.pdf_path)

            # 验证书签页码范围
            max_page = doc.page_count
            invalid_bookmarks = []
            valid_bookmarks = []

            for i, (level, title, page) in enumerate(bookmarks):
                adjusted_page = page + offset
                if 1 <= adjusted_page <= max_page:
                    valid_bookmarks.append([level, title, adjusted_page])
                else:
                    invalid_bookmarks.append((i+1, title, adjusted_page))

            if invalid_bookmarks:
                # 显示无效书签信息
                invalid_info = "\n".join([f"第{row}行: '{title}' (页码: {page})" for row, title, page in invalid_bookmarks])
                reply = QMessageBox.question(self, "书签页码超出范围",
                                           f"发现 {len(invalid_bookmarks)} 个书签的页码超出PDF页数范围 (1-{max_page})：\n\n{invalid_info}\n\n是否继续应用有效书签？",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    doc.close()
                    return

            # 使用set_toc方法设置书签（只使用有效书签）
            # PyMuPDF格式的书签数据：[层级, 标题, 页码, ...]
            # 注意：层级从1开始，页码从1开始
            try:
                doc.set_toc(valid_bookmarks)  # type: ignore
            except (AttributeError, Exception) as e:
                raise Exception(f"无法设置书签：{str(e)}。请确保PyMuPDF版本支持set_toc方法")

            # 保存PDF文档（处理加密和权限问题）
            try:
                # 尝试增量更新
                doc.save(self.pdf_path, incremental=True)
            except Exception as save_error:
                error_str = str(save_error).lower()
                if "encryption" in error_str or "permission denied" in error_str or "permission" in error_str:
                    # 如果是加密或权限问题，创建临时文件然后替换
                    import shutil
                    temp_path = self.pdf_path + ".tmp"
                    doc.save(temp_path)
                    doc.close()

                    try:
                        # 替换原文件
                        shutil.move(temp_path, self.pdf_path)
                        self.status_text.setText(f"成功应用 {len(valid_bookmarks)} 个书签到PDF文件（已处理权限/加密问题）")
                        return
                    except Exception:
                        # 如果移动失败，让用户选择新保存位置
                        save_path, _ = QFileDialog.getSaveFileName(
                            self, "选择保存位置（原文件被锁定）",
                            os.path.join(os.path.dirname(self.pdf_path), f"{os.path.splitext(os.path.basename(self.pdf_path))[0]}_with_bookmarks.pdf"),
                            "PDF files (*.pdf)"
                        )
                        if save_path:
                            try:
                                os.rename(temp_path, save_path)
                                self.status_text.setText(f"成功保存带书签的PDF到: {save_path}")
                                QMessageBox.information(self, "保存成功",
                                                       f"由于原文件被锁定，已保存到新位置：\n{save_path}\n\n您可以使用PDF阅读器打开此新文件查看书签。")
                                return
                            except Exception as rename_error:
                                try:
                                    os.remove(temp_path)
                                except Exception:
                                    pass
                                raise Exception(f"无法保存到新位置：{str(rename_error)}")
                        else:
                            # 用户取消，清理临时文件
                            try:
                                os.remove(temp_path)
                            except Exception:
                                pass
                            raise Exception("用户取消保存操作。")
                else:
                    raise save_error

            doc.close() # type: ignore
            doc = None

            # 显示成功消息
            self.status_text.setText(f"成功应用 {len(valid_bookmarks)} 个书签到PDF文件")

            QMessageBox.information(self, "书签应用成功",
                                  f"已成功将 {len(valid_bookmarks)} 个书签应用到PDF文件。\n\n"
                                  f"文件: {os.path.basename(self.pdf_path)}\n"
                                  "现在可以使用PDF阅读器查看书签了。")

        except Exception as e:
            error_msg = f"应用书签失败: {str(e)}"
            self.status_text.setText(error_msg)

            # 显示错误详情
            QMessageBox.critical(self, "书签应用失败", error_msg)
        finally:
            # 确保文档被正确关闭
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    # 忽略关闭时的错误
                    pass

    def parse_bookmark_file(self):
        """解析书签TXT文件"""
        bookmarks = []
        try:
            with open(self.bookmark_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                # 解析层级和标题
                # 假设格式: 层级|标题|页码
                # 或者: 标题 (页码)
                # 或者: 空格缩进表示层级

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
            self.status_text.setText(f"解析书签文件失败: {str(e)}")
            return []

    def show_ai_prompt(self):
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

        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("AI提示词")
        dialog.setModal(True)
        dialog.resize(700, 500)

        # 创建布局
        layout = QVBoxLayout(dialog)

        # 说明文本
        info_label = QLabel("请复制下面的提示词，然后将PDF文件一起提供给AI：")
        layout.addWidget(info_label)

        # 创建可复制的文本区域
        text_edit = QTextEdit()
        text_edit.setPlainText(prompt_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 复制按钮
        copy_button = QPushButton("复制到剪贴板")
        copy_button.clicked.connect(lambda: self.copy_prompt_to_clipboard(prompt_text))
        button_layout.addWidget(copy_button)

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        dialog.exec()

    def copy_prompt_to_clipboard(self, text):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_text.setText("提示词已复制到剪贴板")

    def view_pdf_bookmarks(self):
        """查看PDF书签信息"""
        if not self.pdf_path:
            QMessageBox.warning(self, "警告", "请先选择PDF文件")
            return

        doc = None
        try:
            doc = pymupdf.open(self.pdf_path)

            # 获取PDF书签
            # PyMuPDF中获取书签的标准方法
            toc = []
            try:
                # 尝试使用get_toc()方法（新版本）
                toc = doc.get_toc()  # type: ignore
            except (AttributeError, Exception):
                # 如果get_toc()失败，尝试getToC()（旧版本方法）
                try:
                    toc = doc.getToC()  # type: ignore
                except (AttributeError, Exception):
                    # 如果都不行，尝试使用outline
                    try:
                        outline = doc.outline
                        if outline:
                            toc = []
                            # 遍历大纲项目
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
                self.info_text.setText("此PDF文档没有书签信息。")
                self.status_text.setText("PDF中未找到书签")
                return

            # 格式化书签信息
            bookmark_info = "PDF书签信息：\n\n"

            for i, (level, title, page) in enumerate(toc, 1):
                indent = "  " * (level - 1)  # 根据层级计算缩进
                bookmark_info += f"{i:2d}. {indent}{title} (第{page}页)\n"

            bookmark_info += f"\n总计: {len(toc)} 个书签"

            # 显示书签信息
            self.info_text.setText(bookmark_info)
            self.status_text.setText(f"成功加载 {len(toc)} 个书签信息")

        except Exception as e:
            error_msg = f"查看书签失败: {str(e)}"
            self.status_text.setText(error_msg)
            # 如果是document closed错误，提供更友好的提示
            if "document closed" in str(e).lower():
                self.info_text.setText("PDF文档已在其他操作中关闭，请重新选择PDF文件。")
            else:
                self.info_text.setText(f"获取书签信息时出错: {str(e)}")
        finally:
            # 确保文档被正确关闭
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    # 忽略关闭时的错误
                    pass

    def edit_bookmark_txt(self):
        """编辑书签TXT文件"""
        dialog = BookmarkEditorDialog(self.bookmark_path, self)
        dialog.exec()


class BookmarkEditorDialog(QDialog):
    def __init__(self, bookmark_path, parent=None):
        super().__init__(parent)
        self.bookmark_path = bookmark_path
        self.init_ui()

    def init_ui(self):
        """初始化编辑器UI"""
        self.setWindowTitle("书签TXT编辑器")
        self.setModal(True)
        self.resize(800, 600)

        # 创建布局
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        # 加载按钮
        load_button = QPushButton("加载文件")
        load_button.clicked.connect(self.load_file)
        toolbar_layout.addWidget(load_button)

        # 保存按钮
        save_button = QPushButton("保存文件")
        save_button.clicked.connect(self.save_file)
        toolbar_layout.addWidget(save_button)

        # 生成按钮
        generate_button = QPushButton("生成模板")
        generate_button.clicked.connect(self.generate_bookmarks)
        toolbar_layout.addWidget(generate_button)

        toolbar_layout.addStretch()

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        toolbar_layout.addWidget(close_button)

        layout.addLayout(toolbar_layout)

        # 文本编辑器
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # 状态标签
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # 如果有现有的书签文件，加载它
        if self.bookmark_path and os.path.exists(self.bookmark_path):
            self.load_file()

    def load_file(self):
        """加载书签文件"""
        if not self.bookmark_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择书签TXT文件", "", "Text files (*.txt)"
            )
            if file_path:
                self.bookmark_path = file_path
            else:
                return

        try:
            with open(self.bookmark_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
            self.status_label.setText(f"已加载文件: {os.path.basename(self.bookmark_path)}")
        except Exception as e:
            self.status_label.setText(f"加载文件失败: {str(e)}")

    def save_file(self):
        """保存书签文件"""
        if not self.bookmark_path:
            self.bookmark_path, _ = QFileDialog.getSaveFileName(
                self, "保存书签TXT文件", "", "Text files (*.txt)"
            )
            if not self.bookmark_path:
                return

        try:
            with open(self.bookmark_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.status_label.setText(f"已保存到: {os.path.basename(self.bookmark_path)}")
        except Exception as e:
            self.status_label.setText(f"保存文件失败: {str(e)}")

    def generate_bookmarks(self):
        """生成书签模板"""
        template = """1|第一章 引言|1
1|第二章 基础知识|5
2|2.1 基本概念|5
2|2.2 重要定理|8
1|第三章 高级主题|12
2|3.1 高级概念|12
3|3.1.1 详细说明|12
3|3.1.2 应用实例|15
1|第四章 总结|20

# 书签格式说明：
# 每行一个书签
# 格式：层级|标题|页码
# 层级从1开始，1表示顶级，2表示二级，以此类推
# 页码从1开始，表示该书签指向的页面
#
# 或者使用格式2：
# 第一章 引言 (1)
# 第二章 基础知识 (5)
#   2.1 基本概念 (5)
#   2.2 重要定理 (8)
# 第三章 高级主题 (12)
#   3.1 高级概念 (12)
#     3.1.1 详细说明 (12)
#     3.1.2 应用实例 (15)
# 第四章 总结 (20)"""

        self.text_edit.setPlainText(template)
        self.status_label.setText("已生成书签模板，请根据需要编辑")


def main():
    app = QApplication(sys.argv)
    window = PDFBookmarkTool()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()