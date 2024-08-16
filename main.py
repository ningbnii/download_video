import requests
from bs4 import BeautifulSoup
import os
import datetime
import m3u8_To_MP4


def parse_url(url):
    response = requests.get(url)

    html_content = response.text

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到包含“片名：”的p标签的内容，p标签格式如下：<p>片名：一念关山</p>，截取“片名：”后面的内容
    movie_title_element = soup.find(
        'p', string=lambda text: text and '片名：' in text)
    movie_title = movie_title_element.text.replace('片名：', '')

    # 在download目录下创建以片名命名的文件夹，判断文件夹是否存在，如果不存在则创建
    movie_directory = f'download/{movie_title}'
    if not os.path.exists(movie_directory):
        os.makedirs(movie_directory)

    # 获取.ffm3u8 div标签下的所有a标签
    a_tags = soup.select('.ffm3u8 a')
    # 遍历a标签，获取m3u8视频的URL和title，title格式如下：第01集，第02集，第03集...，最后一个不是视频，不处理，将数据保存到list中，名称为urls_and_outputs
    urls_and_outputs = []
    for a_tag in a_tags:
        # 判断a标签是否有title属性，如果没有则跳过
        if not a_tag.has_attr('title'):
            continue
        title = a_tag['title']
        if '第' in title:
            url = a_tag['href']
            # output = f'{movie_directory}/{title}.mp4'
            file_dir = f'{movie_directory}'
            file_name = f'{title}.mp4'
            urls_and_outputs.append((url, file_dir, file_name))
        else:
            # 获取第一个a标签的数据
            first_a_tag = a_tags[0]
            if first_a_tag:
                url = first_a_tag['href']
                file_dir = f'{movie_directory}'
                file_name = f'{movie_title}.mp4'
                urls_and_outputs.append((url, file_dir, file_name))

    return urls_and_outputs

# # 打印urls_and_outputs
# print(urls_and_outputs)


# 执行 ffmpeg 命令
def execute_ffmpeg_command(input_url, file_dir, file_name):
    # 调用m3u8_To_MP4中的多线程下载函数
    # 查找当前目录下是否存在同名文件，如果存在则跳过
    if os.path.exists(f'{file_dir}/{file_name}'):
        print(f'{file_name}已存在，跳过下载')
        return
    m3u8_To_MP4.multithread_download(
        input_url, mp4_file_dir=file_dir, mp4_file_name=file_name)


def parallel_download(urls_and_outputs):
    # 所有视频开始下载前打印当前时间
    print("开始下载：", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # 记录开始时间，格式为：年-月-日 时:分:秒
    startTime = datetime.datetime.now()

    # 一个个下载
    for url, file_dir, file_name in urls_and_outputs:
        execute_ffmpeg_command(url, file_dir, file_name)

    # 所有视频下载完成后打印当前时间
    print("全部下载完成：", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    endTime = datetime.datetime.now()
    # 计算下载耗时，转成分钟
    useTime = (endTime - startTime).seconds / 60
    print("下载耗时：", useTime, "分钟")
    main()


def main(url=None):
    # 检查是否已经输入了网页地址
    if not url:
        # 提示用户输入网页地址
        url = input('请输入视频网页地址：')
        while not url:
            url = input('请输入视频网页地址：')
    # 解析网页内容
    urls_and_outputs = parse_url(url)
    # 并行下载视频
    parallel_download(urls_and_outputs)


if __name__ == '__main__':
    # 只调用一次主函数
    main()
