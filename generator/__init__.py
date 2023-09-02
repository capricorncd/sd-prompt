import os
import imghdr
import json

from typing import List, Dict
from .read_img_sd_info import read_img_sd_info, get_timestamp

IMAGE_EXT_LIST = [
    "bmp",
    "gif",
    "ief",
    "jpg",
    "jpe",
    "jpeg",
    "heic",
    "heif",
    "png",
    "svg",
    "tiff",
    "tif",
    "ico",
    "webp",
    "ras",
    "bmp",
    "pnm",
    "pbm",
    "pgm",
    "ppm",
    "rgb",
    "xbm",
    "xpm",
    "xwd",
]


def read_input_images(input_dir: str = "input") -> List[str]:
    """
    读取input_dir目录中的图片文件，并返回图片路径数组
    """
    result: List[str] = []

    if os.path.isdir(input_dir):
        files = [os.path.join(input_dir, filename)
                 for filename in os.listdir(input_dir)]
    elif os.path.isfile(input_dir):
        files = [input_dir]
    else:
        raise f"{input} folder does not exist."

    for file_path in files:
        if os.path.isdir(file_path):
            result.extend(read_input_images(file_path))
        elif is_image_file(file_path):
            result.append(file_path)

    return result


def is_image_file(file_path) -> bool:
    """
    根据文件后缀，判断是否为图片文件
    """
    ext = imghdr.what(file_path) or ""
    return ext in IMAGE_EXT_LIST


def handle_images(input_dir="input", out_dir="output"):
    # 读取图片中SD信息
    images_path = read_input_images(input_dir)
    for image_path in images_path:
        res = read_img_sd_info(image_path)
        # 只处理存在SD信息的图片
        if res.get("Prompt"):
            move_image_to_output_model_dir(res, out_dir)


def move_image_to_output_model_dir(image_info: Dict[str, str], out_dir: str):
    """
    移动图片至output目录下的[model_name]目录中
    并输出同名JSON文件
    """
    src = image_info.get("file_path")
    model_name = image_info.get("Model") or "unknown"
    # 目标目录
    dst = os.path.join(out_dir, model_name.lower(),
                       image_info.get("create_date"))

    # 目标目录不存在则创建
    if not os.path.exists(dst):
        mkdir(dst)

    # 目标图片文件路径
    dst_file_path = os.path.join(dst, create_filename(src))

    # 目标文件是否已存在
    if os.path.exists(dst_file_path):
        dst_file_path = rename_exists_image_file_path(dst_file_path)

    image_info["file_url"] = dst_file_path.replace(os.path.sep, "/")

    del image_info["file_path"]

    # 输出SD图片信息到JSON文件
    json_file_path = create_json_file_path(dst_file_path)
    with open(json_file_path, "w") as write_file:
        json.dump(image_info, write_file)

    # 移动图片文件
    os.rename(src, dst_file_path)
    print(f"{src} 移动成功!")
    print("-->", dst_file_path)


def rename_exists_image_file_path(file_path: str) -> str:
    """
    file_path: 有有效后缀的文件路径
    """
    arr = file_path.split(".")
    ext = arr.pop()
    new_path = f"{'.'.join(arr)}-{get_timestamp()}.{ext}"
    if not os.path.exists(new_path):
        return new_path
    return rename_exists_image_file_path(new_path)


def mkdir(dir: str):
    if os.path.exists(dir):
        return
    temp = []
    for d in dir.split(os.path.sep):
        temp.append(d)
        dir_path = os.path.sep.join(temp)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)


def create_filename(file_path: str) -> str:
    basename = os.path.basename(file_path).lower()
    ext = imghdr.what(file_path)
    if ext is None or basename.endswith(f".{ext}"):
        return basename
    return f"{basename}.{ext}"


def create_json_file_path(image_file_path: str) -> str:
    """
    创建与图片文件同名的JSON文件
    """
    paths = image_file_path.split(".")
    paths[-1] = "json"
    return ".".join(paths)


__all__ = [
    "read_img_sd_info",
    "handle_images"
]
