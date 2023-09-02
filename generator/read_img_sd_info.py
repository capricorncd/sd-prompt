import os
import time
import imghdr
import re

from typing import Dict
from PIL import Image


def read_img_sd_info(img_path: str) -> Dict[str, str]:
    """
    Read the Stable Diffusion information in the image.
    """
    img = Image.open(img_path)
    create_time = os.path.getctime(img_path)

    result = {
        "file_type": imghdr.what(img_path),
        "file_path": img_path,
        "file_size": os.stat(img_path).st_size,
        "create_time": get_timestamp(create_time),
        "create_date": time.strftime("%Y-%m-%d", time.localtime(create_time)),
        # "file_size": img.size, # (width int, height int)
    }

    # 'WebPImageFile' object has no attribute 'text'
    if not hasattr(img, "text"):
        print(f"{img_path}, object has no attribute 'text'")
        return result

    parameters = (img.text).get('parameters') or ''

    is_prompt_ended = False
    prompt_arr = []
    for line in parameters.split('\n'):
        line = line.strip()
        if not is_prompt_ended:
            if line.startswith('Negative prompt:'):
                is_prompt_ended = True
                result['Prompt'] = '\n'.join(prompt_arr)
                result['Negative prompt'] = line[16:].strip()
            else:
                prompt_arr.append(line)
        else:
            _other_params_parser(line.split(', '), result)

    return result


def _other_params_parser(arr, result):
    for item in arr:
        s = re.search(r'([\w\s]+):\s*(.+)', item)
        if s:
            k = s.group(1).strip()
            v = s.group(2)
            result[k] = v
            if k == 'size':
                [w, h] = v.split('x')
                result['width'] = w
                result['height'] = h


def get_timestamp(timestamp: float = time.time()) -> str:
    return str(timestamp).split(".")[0]
