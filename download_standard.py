import os

from downloader import downloader, HEADERS
from swf2pdf import swf2pdf
from config import get_file_name, get_pdf_file_path, is_file_downloaded, SWF_DIR


def download_standard(url: str, code: str, name: str, swf2pdf_dpi: int = 300) -> None:
    if is_file_downloaded(code, name):
        return
    print('')
    if url.lower().endswith('swf'):
        swf_path = os.path.join(SWF_DIR, get_file_name(code, name) + '.swf')
        downloader(url, swf_path, retry=5, chunk_size=16*1024, headers=HEADERS)
        if os.path.exists(swf_path):
            swf2pdf(swf_path, get_pdf_file_path(code, name, is_from_swf=True), dpi=swf2pdf_dpi)
    else:
        downloader(url, get_pdf_file_path(code, name, is_from_swf=False), retry=5, chunk_size=16*1024, headers=HEADERS)


if __name__ == '__main__':
    pass
