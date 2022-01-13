import os
import re
import sys
import time
import shutil

import requests
from requests.packages import urllib3

urllib3.disable_warnings()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62',
}


def get_size_flag(total_length: int) -> tuple:
    if total_length >= 1048576:
        return 1048576, "MB"
    elif total_length >= 1073741824:
        return 1073741824, "GB"
    else:
        return 1024, "KB"


def downloader(url: str, path: str = None, chunk_size: int = 4096,
               rewrite: bool = False, retry: int = 1, **kwargs) -> None:
    if not path:
        path = re.sub(r'[/\\<>?:"|*]+', ' ', url.split('/')[-1])
        path = ".%s%s" % (os.path.sep, path)
    if os.path.exists(path) and not rewrite:
        print('文件已存在：%s' % path)
        return

    print('下载：%s -> %s' % (url, path))

    retry_n = 0
    while True:
        if retry_n >= retry > 0:
            raise requests.exceptions.ConnectionError('经过%d次重试后，连接仍然错误！' % retry)
        try:
            response = requests.get(url, stream=True, **kwargs)
            break
        except requests.exceptions.ConnectionError as e:
            print('\t连接错误，5S后重试！')
            retry_n += 1
            time.sleep(5)

    try:
        total_length = int(response.headers["Content-Length"])
    except:
        total_length = 0

    size_flag = get_size_flag(total_length)
    size = "%.2f%s" % (total_length / size_flag[0], size_flag[1])
    time1 = time.time()
    temp_path = path+'.temp~'
    path_dir = os.path.dirname(path)
    os.makedirs(path_dir, exist_ok=True)
    with open(temp_path, 'wb') as f_:
        temp_size = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                temp_size += len(chunk)

                f_.write(chunk)
                f_.flush()
                time2 = time.time()
                if time2 - time1 == 0:
                    speed = 9999
                else:
                    speed = temp_size / (time2 - time1) / 1024
                if total_length == 0:
                    size_flag_tmp = get_size_flag(temp_size)
                    if size_flag_tmp[0] == 0:
                        temp_size_format = ''
                    else:
                        temp_size_format = "%.2f%s" % (temp_size / size_flag_tmp[0], size_flag_tmp[1])
                    sys.stdout.write("\r\t已下载:%s  下载速度:%.2fkB/s" % (temp_size_format, speed))
                else:
                    if size_flag[0] == 0:
                        temp_size_format = ''
                    else:
                        temp_size_format = "%.2f%s" % (temp_size / size_flag[0], size_flag[1])
                    done = int(50 * temp_size / total_length)
                    sys.stdout.write("\r[%s%s]  %d%%  %s/%s  %.2fkB/s" % (
                        '=' * done, ' ' * (50 - done), 100 * temp_size / total_length, temp_size_format, size, speed)
                    )
                sys.stdout.flush()
    shutil.move(temp_path, path)
    sf = get_size_flag(temp_size)
    print('\n下载完成！\t文件大小：%.2f%s\t共用时：%.2fS' % (temp_size / sf[0], sf[1], time.time()-time1))
