# -*- coding: utf-8 -*-
__author__ = 'ji_bu_de'
__time__ = '2019-08-29 18:41'
import aiohttp
import asyncio
import os
from pyquery import PyQuery
import re


async def get_html(url):
    """
    获取根link的页面
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               # 使用的纸飞机的http代理模式,目标网站服务器在美国 建议找一个国外代理运行
                               # proxy='http://127.0.0.1:1087'
                               ) as response:
            return await response.text()


async def get_html_name(url, name):
    """
    为了方便代码编写
    :param url:
    :param name:
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               # 使用的纸飞机的http代理模式
                               # proxy='http://127.0.0.1:1087'
                               ) as response:
            return await response.text(), name


async def get_img(url, file_name, dir_name):
    """
    下载图片
    :param url:
    :param file_name:
    :param dir_name:
    :return:
    """
    url = f'http://99.94201314.net/dm03{url}'
    if not os.path.isdir(f'./zjny/{dir_name}'):     # 目录存在就不创建
        os.makedirs(f'./zjny/{dir_name}')
    if os.path.isfile(f'zjny/{dir_name}/{file_name}.jpg'):      # 如果本身就存在，已经下载好了就跳过，没下载好就重新下载
        if os.path.getsize(f'zjny/{dir_name}/{file_name}.jpg') > 1000:
            print('已经存在')
            return
        else:
            print(f'{dir_name} 第{file_name}应该没有下载成功 重新下载')
    async with aiohttp.ClientSession() as session:
        async with session.get(url,
                               # 使用的纸飞机的http代理模式
                               # proxy='http://127.0.0.1:1087'
                               ) as response:
            with open(f'zjny/{dir_name}/{file_name}.jpg', 'wb') as f:
                while True:
                    chunk = await response.content.read(512)
                    if not chunk:
                        break
                    f.write(chunk)
    print(f'{dir_name} 第{file_name}页 下载完成')
    return f'{dir_name} 第{file_name}页 下载完成'


def parse_pages(root_html):
    """
    解析根页面的内容获取每一集漫画的url
    :param root_html:
    :return: list
    """
    url_list = []
    doc = PyQuery(root_html)
    urls = doc('.cVolList div a').items()
    for url in urls:
        url_list.append({
            'url': f"http://99.hhxxee.com{url.attr('href')}",
            'name': url.text()
        })
    return url_list


def parse_imgs(page_html):
    """
    获取每一集漫画的中图片的链接
    :param page_html:
    :return:
    """
    img_list = []
    doc = PyQuery(page_html)
    matchObj = re.match(r'^var sFiles="(.*)";var sPath="3";$',
                        doc('#Head1 > script:nth-child(6)').text())
    if matchObj:
        img_list.extend(matchObj.group(1).split('|'))
    else:
        return None
    return img_list
    pass


async def run():
    """
    :return:
    """
    imgs_queue = asyncio.Queue()     # 图片下载队列
    chapter_imgs_list = []     # 每一集的图片的列表
    imgs_list = []  # 太快 下载会出错

    # 获取入口html 解析处每一集的链接地址
    root_html = await get_html('http://99.hhxxee.com/comic/9932644/')
    chapter_list = parse_pages(root_html)

    # 获取每一集中的图片链接地址
    chapter_list_tasks = [asyncio.ensure_future(get_html_name(chapter['url'], chapter['name']))
                          for chapter in chapter_list]
    for task in asyncio.as_completed(chapter_list_tasks):
        res = await task
        chapter_imgs_list.append({
            'imgs': parse_imgs(res[0]),
            'name': res[1]

        })

    for chapter_imgs in chapter_imgs_list:
        i = 1
        for chapter_img in chapter_imgs['imgs']:
            # 太快 下载会出错
            # imgs_list.append({
            #     'url': chapter_img,
            #     'dir_name': chapter_imgs['name'],
            #     'file_name': i
            # })
            imgs_queue.put_nowait({
                'url': chapter_img,     # 图片下载地址
                'dir_name': chapter_imgs['name'],   # 图片对应的章节文件夹
                'file_name': i      # 图片在章节的那一页
            })
            i = i + 1


    # 太快 下载会出错
    # img_task = None
    # img_task = [asyncio.ensure_future(get_img(img['url'], img['file_name'], img['dir_name'])) for img in imgs_list]
    # for i_tsak in img_task:
    #     print(await i_tsak)

    while(not imgs_queue.empty()):
        img = await imgs_queue.get()
        await get_img(img['url'], img['file_name'], img['dir_name'])

    print('下载完成')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    pass



