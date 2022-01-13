import re
import logging

import requests
from lxml import etree

from downloader import HEADERS
from config import is_file_downloaded, get_file_name


def get_resource_url(url: str, code: str, name: str) -> str:
    resp = requests.get(url, headers=HEADERS)
    down_code = re.search(r'window.open\(.*\)', resp.text)
    target_url = ''
    if down_code:
        path = re.sub('["+()\s]', '', down_code.group()).replace('window.open', '')
        pdf_url = 'http://zwgk.mwr.gov.cn' + path
        # 从信息页抓取的pdf下载地址，推荐性规范的资源已被删除，不能直接下载，需要转换为swf下载地址
        swf_url = pdf_url.replace('pdf', 'swf')
        # 判断服务器存在哪种格式的资源，优先下载PDF
        if pdf_url and 'pdf' in requests.head(pdf_url, headers=HEADERS).headers.get('Content-Type', '').lower():
            target_url = pdf_url
        elif swf_url and 'flash' in requests.head(swf_url, headers=HEADERS).headers.get('Content-Type', '').lower():
            target_url = swf_url
    if not target_url:
        logging.warning(msg='未解析到下载地址！ -> %s' % get_file_name(code, name))
    return target_url


def standard_info_generator(ignore_downloaded=False):
    html = etree.HTML(requests.post('http://zwgk.mwr.gov.cn/jsp/yishenqing/appladd/bzsearch.jsp', headers=HEADERS).text)
    trs = html.xpath('//*[@id="dynamic-table"]/tbody/tr')
    for tr in trs:
        uuid = ','.join(tr.xpath('./td')[0].xpath('./text()'))
        txh = ','.join(tr.xpath('./td')[1].xpath('./text()'))
        name = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[2].xpath('./a/text()')))
        href = 'http://zwgk.mwr.gov.cn/jsp/yishenqing/appladd/' + tr.xpath('./td')[2].xpath('./a/@href')[0]
        name_en = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[3].xpath('./text()')))
        code = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[4].xpath('./text()')))
        if ignore_downloaded and is_file_downloaded(code, name):
            continue
        klass = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[5].xpath('./text()')))
        category = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[6].xpath('./text()')))
        public_date = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[7].xpath('./text()')))
        implement_date = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[8].xpath('./text()')))
        department = re.sub(r'\s+', ' ', ''.join(tr.xpath('./td')[10].xpath('./text()')))
        url = get_resource_url(href, code, name)

        yield {
            'url': url,
            'code': code,
            'name': name,
            'englishName': name_en,
            'publicDate': public_date.replace('/', '-'),
            'implementDate': implement_date.replace('/', '-'),
            'hostUnit': department,
            'industrySon': klass,
            'category': category,
            'uuid': uuid,
            'txh': txh,
        }


if __name__ == '__main__':
    for st in standard_info_generator(ignore_downloaded=True):
        print(st)

