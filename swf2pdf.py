import os
import sys
import shutil
import logging

from fitz import Document

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if 'win' in sys.platform.lower():
    swfrender = os.path.join(BASE_DIR, 'bin', 'swfrender.exe')
    NULL = '1>nul 2>nul'
elif 'linux' in sys.platform.lower():
    swfrender = os.path.join(BASE_DIR, 'bin', 'swfrender')
    NULL = '1>/dev/null 2>/dev/null'
else:
    raise OSError('操作系统平台不受支持 -> %s' % sys.platform)

if not os.path.exists(swfrender):
    raise EnvironmentError('''找不到 swfrender 程序依赖 -> %s
    可到下面地址下载程序，并将 swfrender 放到 bin 目录下。
    http://www.swftools.org/download.html
    ''' % swfrender)


def swf2pdf(src_path: str, target_path: str, dpi: int = 300) -> None:
    name = src_path.split(os.sep)[-1]
    image_path_dir = os.path.join(os.path.dirname(src_path), name.replace('.swf', '-pngs'))
    os.makedirs(image_path_dir, exist_ok=True)
    image_path = os.path.join(image_path_dir, 'content.png')
    print('开始将swf转为png图片，稍候...')
    os.system('%s "%s" -r %d -o "%s" %s' % (swfrender, src_path, dpi, image_path, NULL))
    print('已将swf转为png图片 -> %s' % image_path_dir)
    print('开始将png转为合并为PDF')
    with Document() as pdf:
        num_files = os.listdir(image_path_dir).__len__()
        if num_files < 1:
            logging.error(msg='未从swf文件中解出图片 -> %s' % src_path)
            shutil.rmtree(image_path_dir)
            return
        for i in range(1, num_files+1):
            img_path = os.path.join(image_path_dir, 'content-%d.png' % i)
            if not os.path.exists(img_path):
                continue
            with Document(img_path) as img:
                with Document(stream=img.convert_to_pdf(), filetype='pdf') as p:
                    pdf.insert_pdf(p)
                    print('\t添加图片到pdf -> %s' % img_path)
        pdf.save(target_path)
    print('合并完成，保存转换后的PDF -> %s' % target_path)
    shutil.rmtree(image_path_dir)
    print('临时文件已清除！')

