import os
from PIL import Image
import argparse


#given a path provided by the argument --img_dir, it goes trough all folders and subfolders and subsubfodlers and ..., and will delet all images that can 
#not be opened. Carefull, if you provide a path that contains valuable files that are not images, it will delet them!

parser = argparse.ArgumentParser()
parser.add_argument('--img_dir',  default='/Users/Giaco/Dropbox/AIshroom/database/train_multi_classes')
opt = parser.parse_args()

img_dir = opt.img_dir


def clean_images(img_dir):
	for filename in os.listdir(img_dir):
		if os.path.isdir(img_dir+'/'+filename):
			clean_images(img_dir+'/'+filename)
		else:
		    try :
		        # with Image.open(img_dir + "/" + filename) as im:
		        #      print('ok')
		        im=Image.open(img_dir + "/" + filename).convert('RGB')
		        im.save(img_dir + "/" + filename)
		    except :
		        print('removing file: '+img_dir + "/" + filename)
		        os.remove(img_dir + "/" + filename)

clean_images(img_dir)