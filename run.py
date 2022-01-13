from crawl import standard_info_generator
from download_standard import download_standard


def execute(swf2pdf_dpi: int = 300) -> None:
    for st in standard_info_generator(ignore_downloaded=True):
        args = [
            st.get('url'),
            st.get('code'),
            st.get('name'),
        ]
        if not all(args):
            continue
        download_standard(*args, swf2pdf_dpi=swf2pdf_dpi)


if __name__ == '__main__':
    execute(150)
