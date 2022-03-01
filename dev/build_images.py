import os
from PIL import Image

for part in os.listdir('partial_forest'):
    part_num = part.replace('partial_forest_', '').replace('.png', '')
    part_num = int(part_num)
    part_img = Image.open(f'partial_forest/{part}')
    os.mkdir(f'../sprites/forest/{part_num}')
    paths = os.listdir('../sprites/forest_old')
    for path in paths:
        path_img = Image.open(f'../sprites/forest_old/{path}')
        path_img.paste(part_img, (0, 0), part_img)
        path_img.save(f'../sprites/forest/{part_num}/{path}')