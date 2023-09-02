@echo off  
chcp 65001 > nul  
echo 即将开始处理根目录下的input文件夹中的图片文件
echo 获取图片中的Stable Diffusion相关信息、生成json文件，并放入output文件夹中按模型归类
echo.
echo 请确保input文件夹中存在需要处理的文件
pause
python main.py
pause