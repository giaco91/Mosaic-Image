from mosaik_functions import *

import argparse

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser()
parser.add_argument('--path_to_macro_img', default='makro_images/main5.jpg')
parser.add_argument('--path_to_image_folder', default='downloads/rose/')
parser.add_argument('--save_path', default='mosaik_images/test.jpeg')
parser.add_argument('--load_preprocessed_img', type=str2bool, default=True)
parser.add_argument('--micro_size', type=int, default=45)
parser.add_argument('--macro_width', type=int, default=90)
parser.add_argument('--macro_height', type=int, default=80)
parser.add_argument('--temperature',  type=int, default=40)
parser.add_argument('--amount_of_augmentation',  type=float, default=0.2)

opt = parser.parse_args()
print(opt)


im=create_pixel_image(path_macro_image=opt.path_to_macro_img,path_micro_images=opt.path_to_image_folder,
                                macro_size=[opt.macro_width,opt.macro_height],micro_size=opt.micro_size,
                                load=opt.load_preprocessed_img,temp=opt.temperature,ratio=opt.amount_of_augmentation)
im.save(opt.save_path)#,format='JPEG'

