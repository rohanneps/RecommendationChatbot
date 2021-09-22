import os
import os
from urllib.request import urlopen
from PIL import Image
from shutil import copyfile


def create_dir(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)

def download_image(url, image_path):
	if not os.path.exists(image_path):
		f = open(image_path,'wb')
		f.write(urlopen(url).read())
		f.close()
		image = Image.open(image_path)
		image.convert('RGB').save(image_path)

def download_page_source(page_source, file_name):
	with open(file_name, 'w') as f:
		f.write(page_source)

def copy_file(src_path, dest_path):
	copyfile(src_path, dest_path)