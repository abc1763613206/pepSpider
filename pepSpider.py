import os
import traceback

import requests
from fpdf import FPDF
from lxml import etree
from time import sleep


def get_html_doc(url):
    response = requests.get(url, headers=headers)
    response.encoding = "UTF-8"
    return etree.HTML(response.text)


def spider_book_info(ourl, html_doc):
    book_info_dicts = {}
    url_li_elements = html_doc.xpath('//*[@id="container"]/div/ul/li[@class="fl"]')
    for li in url_li_elements:
        name = li.xpath('./a/@title')[0]
        # url = li.xpath('./a/@href')[0]
        url = str(li.xpath('./div/a[@class="btn_type_dl"]/@href')[0]).replace('./',ourl)
        #print("Filelist:\n")
        #print(F"{name}: {url}")
        book_info_dicts.update({name: url})
    return book_info_dicts


def download_book_images_to(output_dir, book_name: str, book_url: str):
    book_id = book_url.rsplit('/', maxsplit=2)[1]
    print(F"downloading {book_name} (操作期间请不要动tmp目录) : {output_dir}")
    for image_number in range(1, 2000):  # 2000 页肯定够了
        image_urls = F"http://bp.pep.com.cn/ebook/{book_id}/files/mobile/{image_number}.jpg"
        response = requests.get(image_urls, headers=headers)
        if response.status_code == 200:
            image_path = F"{output_dir}{image_number}.jpg"
            with open(image_path, 'wb') as fp:
                fp.write(response.content)
            print(F"{image_number}.jpg", end=' ')
        else:
            print(image_urls)
            print(response.status_code)
            print(F"{book_name}: {image_number - 1} images")
            break

def download_book_to(output_dir, book_name: str, book_url: str):
    print(F"downloading {book_name} {book_url} : {output_dir}")
    response = requests.get(book_url, headers=headers)
    if response.status_code == 200:
        #content_size = int(response.headers['Content-Length'])/1024     #确定大小
        image_path = F"{output_dir}{book_name}.pdf"
        with open(image_path, 'wb') as fp:
            #for data in tqdm(iterable=response.iter_content(1024),total=content_size,unit='k',desc=book_name):
            #    #调用iter_content，一块一块的遍历要下载的内容，搭配stream=True，此时才开始真正的下载
            #    #iterable：可迭代的进度条 total：总的迭代次数 desc：进度条的前缀
            #    fp.write(data)
            fp.write(response.content)
        #print(F"{image_number}.jpg", end=' ')
        return
    else:
        print(book_url)
        print(response.status_code)
        #print(F"{book_name}: {image_number - 1} images")
        return 


def images2pdf(from_dir, to_dir, book_name):
    """convert *.jpg files into a pdf in specify directory(from_dir) to destination directory(to_dir)"""
    os.chdir(from_dir)
    images = [image for image in os.listdir(from_dir) if image.endswith('jpg')]
    images.sort(key=lambda x: int(x.split('.')[0]))
    pdf = FPDF()
    for each_image in images:
        if each_image.endswith('.jpg'):
            pdf.add_page()
            pdf.image(each_image, x=5, y=5, w=210, h=297, type='jpg')
    else:
        os.chdir(to_dir)
        output_book_name = F"{book_name}.pdf"
        pdf.output(output_book_name)


def make_or_rename_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        make_or_rename_dir(dir_path)
    else:
        if os.path.isdir(dir_path):
            pass
        else:
            os.rename(dir_path, "tmp_dir_name")
            os.mkdir(dir_path)
            make_or_rename_dir(dir_path)


def main():
    url_dicts = { # //*[@id="container"]/div[9]/ul/li/a/@href
        '义务教育教科书（小学）': ['http://bp.pep.com.cn/jc/ywjygjkcjc/xdjc/','http://bp.pep.com.cn/jc/ywjygjkcjc/xxdfjsys/','http://bp.pep.com.cn/jc/ywjygjkcjc/xyjc/','http://bp.pep.com.cn/jc/ywjygjkcjc/xxywjsys/','http://bp.pep.com.cn/jc/ywjygjkcjc/xsjc/','http://bp.pep.com.cn/jc/ywjygjkcjc/xxsxjsys/','http://bp.pep.com.cn/jc/ywjygjkcjc/xyingjc/','http://bp.pep.com.cn/jc/ywjygjkcjc/xxyyjsys/','http://bp.pep.com.cn/jc/ywjygjkcjc/xxkxjc/','http://bp.pep.com.cn/jc/ywjygjkcjc/xxkxjsys/','http://bp.pep.com.cn/jc/yjcz/czdf/','http://bp.pep.com.cn/jc/yjcz/czdfjsys/','http://bp.pep.com.cn/jc/yjcz/cyjc/','http://bp.pep.com.cn/jc/yjcz/cyywjsys/','http://bp.pep.com.cn/jc/yjcz/czlsjc/','http://bp.pep.com.cn/jc/yjcz/czlsjsys/','http://bp.pep.com.cn/jc/yjcz/czsxjc/','http://bp.pep.com.cn/jc/yjcz/czsxjsys/','http://bp.pep.com.cn/jc/yjcz/czyingyjc/','http://bp.pep.com.cn/jc/yjcz/czyyjsys/','http://bp.pep.com.cn/jc/yjcz/czwljc/','http://bp.pep.com.cn/jc/yjcz/czwljsys/','http://bp.pep.com.cn/jc/yjcz/czhxjc/','http://bp.pep.com.cn/jc/yjcz/czhxjsys/','http://bp.pep.com.cn/jc/yjcz/czswjc/','http://bp.pep.com.cn/jc/yjcz/czswjsys/','http://bp.pep.com.cn/jc/yjcz/czlsyshjc/','http://bp.pep.com.cn/jc/yjcz/czlsyshjsys/','http://bp.pep.com.cn/jc/yjcz/czdljc/','http://bp.pep.com.cn/jc/yjcz/czdljsys/','http://bp.pep.com.cn/jc/yjcz/czeyjc/','http://bp.pep.com.cn/jc/yjcz/czeyjsys/'],
        
        
        '义务教育教科书（五·四学制）（小学）': ['http://bp.pep.com.cn/jc/ywjygjkcjc54zxx/xxdf54jc/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zxx/xxdf54jsys/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zxx/xxyw54jc/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zxx/xxyw54jsys/',
                                        
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czdf54jc/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czdf54jsys/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czyw54jc/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czyw54jsys/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czls54jc/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czls54jsys/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czsx54jc/',
                                        'http://bp.pep.com.cn/jc/ywjygjkcjc54zcz/czsxjsys/'],
        
        '普通高中教科书': ['http://bp.pep.com.cn/jc/ptgzjks/pgsxzzjc/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pglsjks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgywjks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgywjsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgsxjks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgsxjsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgdljks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgdljsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgyyjks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgyyjsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pghxjks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pghxjsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgswjks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgswjsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgwljks/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgwljsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgxxjsjc/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgxxjsjsys/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgryjc/',
                        'http://bp.pep.com.cn/jc/ptgzjks/pgryjsys/'],
        
        '普通高中课程标准实验教科书': ['http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbsxzzjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbsxzzjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbywjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbywjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkblsjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkblsjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbsxjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbsxjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbwljc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbwljsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbhxjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbhxjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbswjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbswjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbdljc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbdijsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbyyjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/gzkbyyjsys/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/kbeyjc/',
                                   'http://bp.pep.com.cn/jc/ptgzkcbzsyjks/kbeyjsys/'],
        
        '中职教科书': ['http://bp.pep.com.cn/jc/zzwhjc/zzxjc/',
                    'http://bp.pep.com.cn/jc/zzwhjc/zzxjsys/',
                    'http://bp.pep.com.cn/jc/zzwhjc/zzggjckcjc/',
                    'http://bp.pep.com.cn/jc/zzwhjc/zzggjckcjsys/',
                    'http://bp.pep.com.cn/jc/zzwhjc/zzjyghjc/',
                    'http://bp.pep.com.cn/jc/zzwhjc/zzjyghjsys/']
    }

    # make directory_root
    original_path = os.getcwd()
    make_or_rename_dir(F"{original_path}/output/")
    for k, urlitems in url_dicts.items():
        try:
            
            # make directory_leaf
            output_dir = F"{original_path}/output/{k}/"
            #tmp_output_dir = F"{original_path}/output/{k}/tmp/"
            make_or_rename_dir(output_dir)
            #make_or_rename_dir(tmp_output_dir)
            print(F"Output directory: {output_dir}\n")
            for url in urlitems:
                print(url)
                # crawling
                html_doc = get_html_doc(url)
                book_info_dicts = spider_book_info(url, html_doc)
                print(book_info_dicts)
                for book_na, book_url in book_info_dicts.items():
                    # check exists
                    book_name = k + " " + book_na
                    os.chdir(output_dir)
                    if os.path.exists(F"{book_name}.pdf"):
                        print(F"{book_name}.pdf 已存在，开始下一个")
                        continue
                    print(F"{book_name}.pdf 不存在，开始下载")
                    download_book_to(output_dir, book_name=book_name, book_url=book_url)
            #    # truncate tmp directory
            #    os.chdir(tmp_output_dir)
            #    [os.remove(file) for file in os.listdir('.')]
            #    print("tmp 目录清空成功!")
#
            #    # download images to tmp directory
            #    
#
            #    # convert images(JPG) into a PDF file
            #    print("开始合并为 PDF...")
            #    images2pdf(from_dir=tmp_output_dir, to_dir=output_dir, book_name=book_name)
            #    print(F"{book_name} done!")
            #    sleep(3)
            #else:
            #    os.chdir(tmp_output_dir)
            #    [os.remove(file) for file in os.listdir('.')]
            #    print("tmp 目录清空成功!")
            #    print("done!")
            #    print("-----------" * 10)
        except Exception:
            print(F"有一点错误：{traceback.format_exc()}")


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'Host': 'bp.pep.com.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://bp.pep.com.cn/ebook/ddyfzyinjxc/mobile/index.html',
        }
    main()
