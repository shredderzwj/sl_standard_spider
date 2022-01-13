import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置swf文件存储路径
SWF_DIR = os.path.join(BASE_DIR, 'standards', 'swf')

# 设置pdf文件存储路径
PDF_DIR = os.path.join(BASE_DIR, 'standards', 'pdf')

os.makedirs(SWF_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


def filter_name(name: str) -> str:
    """过滤掉文件名中的非法字符"""
    return re.sub(r'[/\\:*"<>|?\n\s]+', ' ', name)


def get_file_name(code: str, name: str) -> str:
    return filter_name('%s《%s》' % (code, name))


def get_pdf_file_path(code: str, name: str, is_from_swf: bool = False) -> str:
    file_name = get_file_name(code, name)
    path = os.path.join(PDF_DIR, file_name)
    if is_from_swf:
        return path + '.swf.pdf'
    return path + '.pdf'


def is_file_downloaded(code: str, name: str) -> bool:
    for ft in [False, True]:
        target_path = get_pdf_file_path(code, name, is_from_swf=ft)
        if os.path.exists(target_path):
            print('已下载规范，跳过 -> %s' % target_path)
            return True
    return False
