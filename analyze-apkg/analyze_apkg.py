import sqlite3
import zipfile
import os


def read_apkg(apkg_path):
    # 创建临时目录来解压文件
    temp_dir = 'temp_apkg'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # 解压 .apkg 文件
    with zipfile.ZipFile(apkg_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 数据库文件通常命名为 'collection.anki2'
    db_path = os.path.join(temp_dir, 'collection.anki2')

    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询笔记表
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    # 打印笔记
    for note in notes:
        print(note)

    # 关闭连接
    conn.close()

    # 清理临时目录
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_dir)


# 解压缩 .apkg 文件
def unzip_apkg(apkg_path, extract_to):
    with zipfile.ZipFile(apkg_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


# 检查是否包含音频文件
def check_audio_files(extract_to):
    media_path = os.path.join(extract_to, 'media')
    if not os.path.exists(media_path):
        print("没有找到媒体文件夹。")
        return

    audio_files = [f for f in os.listdir(media_path) if f.endswith('.mp3') or f.endswith('.wav')]
    if audio_files:
        print("发现以下音频文件:")
        for audio_file in audio_files:
            print(audio_file)
    else:
        print("没有发现音频文件。")


# 使用示例
apkg_path = './cache/test_file.apkg'  # 替换为你的 .apkg 文件路径
read_apkg(apkg_path)
# 主程序
# apkg_path = 'path/to/your/file.apkg'
# extract_to = './cache/files'
#
# unzip_apkg(apkg_path, extract_to)
# check_audio_files(extract_to)
