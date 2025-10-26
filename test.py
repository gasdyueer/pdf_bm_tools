import pymupdf

pdffile = r"D:\data\book\math\运筹学教程（第5版） (胡运权 郭耀煌 龚益鸣 程佳惠 陈秉正) (Z-Library)-加书签目录.pdf"
doc = pymupdf.open(pdffile)
toc = doc.get_toc()  # type: ignore
print(toc)