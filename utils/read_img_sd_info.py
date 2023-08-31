import re

from typing import Dict
from PIL import Image


def read_img_sd_info(img_path: str) -> Dict[str, str]:
    """
    Read the Stable Diffusion information in the image.
    """
    img = Image.open(img_path)
    parameters = (img.text).get('parameters') or ''

    result = {}
    is_prompt_ended = False
    prompt_arr = []
    for line in parameters.split('\n'):
        line = line.strip()
        if not is_prompt_ended:
            if line.startswith('Negative prompt:'):
                is_prompt_ended = True
                result['prompt'] = '\n'.join(prompt_arr)
                result['negative'] = line[16:].strip()
            else:
                prompt_arr.append(line)
        else:
            _other_params_parser(line.split(', '), result)

    return result


def _other_params_parser(arr, result):
    for item in arr:
        s = re.search(r'([\w\s]+):\s*(.+)', item)
        if s:
            k = s.group(1).lower().replace(' ', '_')
            v = s.group(2)
            result[k] = v
            if k == 'size':
                [w, h] = v.split('x')
                result['width'] = w
                result['height'] = h
