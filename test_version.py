import pymupdf

# 测试PDF文件路径
pdffile = r"D:\data\book\math\运筹学教程（第5版） (胡运权 郭耀煌 龚益鸣 程佳惠 陈秉正) (Z-Library)-加书签目录.pdf"

try:
    doc = pymupdf.open(pdffile)
    print(f"PyMuPDF版本: {pymupdf.__version__}")
    print("文档页数:", doc.page_count)

    # 测试不同的方法获取目录
    methods = [
        ("doc.get_toc()", lambda: doc.get_toc()), # type: ignore
        ("doc.outline", lambda: doc.outline),
        ("doc.getToC()", lambda: doc.getToC()), # type: ignore
    ]

    for method_name, method_func in methods:
        try:
            result = method_func()
            print(f"✓ {method_name}: 成功")
            print(f"  返回类型: {type(result)}")
            if result:
                print(f"  结果长度: {len(result)}")
                if isinstance(result, list) and len(result) > 0:
                    print(f"  第一个项目: {result[0]}")
            else:
                print("  返回空结果")
        except Exception as e:
            print(f"✗ {method_name}: 失败 - {str(e)}")
        print()

    doc.close()

except Exception as e:
    print(f"打开文档失败: {str(e)}")