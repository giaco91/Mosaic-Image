from PIL import Image,ExifTags
import os
import numpy as np

image_path='/Users/Giaco/Pictures/Meret_Giaco/Bis 26.Dez/'

# Open an Image
def open_image(path,rotate=False):
  img = Image.open(path)
  if rotate:
  	if img._getexif() is not None:
	  	exif=dict((ExifTags.TAGS[k], v) for k, v in img._getexif().items() if k in ExifTags.TAGS)
	  	if 'Orientation' in exif.keys():
		  	if not exif['Orientation']:
		  		return img
		  	elif exif['Orientation']==3:
		  		print('rotating image by 180')
		  		img=img.rotate(180, expand=True)
		  	elif exif['Orientation']==6:
		  		print('rotating image by 270')
		  		img=img.rotate(270, expand=True)
		  	elif exif['Orientation']==8: 	
		  		print('rotating image by 90')
		  		img=img.rotate(90, expand=True)
  return img

# Save Image
def save_image(image, path):
  image.save(path, 'png')


# Create a new image with the given size
def create_image(i, j):
  image = Image.new("RGB", (i, j), "white")
  return image

def get_pixel(image, i, j):
  # Inside image bounds?
  width, height = image.size
  if i > width or j > height:
    return None

  # Get Pixel
  pixel = image.getpixel((i, j))
  return pixel

def resize_to_height_ref(image,n_height):
	w,h=image.size
	return image.resize((n_height,round(n_height*h/w)),Image.ANTIALIAS)

def square_crop(image):
	w,h=image.size
	if w<h:
		step=round((h-w)/2)
		return image.crop((0, step, w, h-step))
	else:
		step=round((w-h)/2)
		return image.crop((step,0,w-step,h))

def calc_average_rgb(image):
	W,H=image.size
	rgb=np.zeros(3)
	for w in range(0,W):
		for h in range(0,H):
			pixel_rgb=get_pixel(image,w,h)
			rgb[0]+=pixel_rgb[0]
			rgb[1]+=pixel_rgb[1]
			rgb[2]+=pixel_rgb[2]
	rgb/=W*H
	return (int(rgb[0]),int(rgb[1]),int(rgb[2]))



def get_preprocessed_micro_images(path_micro_images,size,load=False):
	preprocessed_micro_images=[]
	if load==False:
		if not os.path.exists(path_micro_images+'processed'+str(size)):
			os.mkdir(path_micro_images+'processed'+str(size))
		for im_name in os.listdir(path_micro_images):
			if im_name.endswith(".jpg"):
				im=open_image(path_micro_images+im_name,rotate=not load)
				im=square_crop(im)
				im=resize_to_height_ref(im,size)
				preprocessed_micro_images.append(im)
				print('save_image....')
				save_image(im,path_micro_images+'processed'+str(size)+'/'+im_name)
	else:
		if not os.path.exists(path_micro_images+'processed'):
			raise ValueError('can not load processed images')
		else:
			for im_name in os.listdir(path_micro_images+'processed'+str(size)):
				if im_name.endswith(".jpg"):
					im=open_image(path_micro_images+'processed'+str(size)+'/'+im_name).copy()
					preprocessed_micro_images.append(im)
	return preprocessed_micro_images

def get_assignment(macro_im,averages,temp=5):
	#temp>0 allowes inoptimal assigments for systematic breaking
	temp=int(np.ceil(temp))
	W,H=macro_im.size
	im_matrix=np.zeros((W,H))
	d=np.zeros(len(averages))
	for w in range(0,W):
		for h in range(0,H):
			closest=1e10
			p=get_pixel(macro_im,w,h)
			i=0
			for a in averages:
				#d=(a[0]-p[0])**2+(a[1]-p[1])**2+(a[2]-p[2])**2
				d[i]=(a[0]-p[0])**2+(a[1]-p[1])**2+(a[2]-p[2])**2
				# if d<closest:
				# 	closest=d
				# 	im_matrix[w,h]=i
				i+=1
			sorted_idx=np.argsort(d)
			im_matrix[w,h]=np.random.choice(sorted_idx[0:temp])

	return im_matrix.astype(int)

def push(macro_pixel,micro_im,ratio=0.25):
	#ratio between 0 and 1, 1 is full push and 0 is no push
	W,H=micro_im.size
	a=calc_average_rgb(micro_im)
	pixels=micro_im.load()
	d0=macro_pixel[0]-a[0]
	d1=macro_pixel[1]-a[1]
	d2=macro_pixel[2]-a[2]
	for w in range(W):
		for h in range(H):
			pixels[w,h]=(round(max(min(pixels[w,h][0]+d0*ratio,255),0)),round(max(min(pixels[w,h][1]+d1*ratio,255),0)),round(max(min(pixels[w,h][2]+d2*ratio,255),0)))
	return micro_im

def create_pixel_image(path_macro_image,path_micro_images,macro_size=60,micro_size=40,cheat=True,load=False,temp=5,ratio=0.25):
	macro_im=open_image(path_macro_image,rotate=not load)
	macro_im=resize_to_height_ref(macro_im,macro_size)
	macro_w,macro_h=macro_im.size
	micro_images=get_preprocessed_micro_images(path_micro_images,micro_size,load=load)
	averages=[]
	for micro_im in micro_images:
		averages.append(calc_average_rgb(micro_im))
	assignment=get_assignment(macro_im,averages,temp=temp)
	pixel_image=create_image(micro_size*macro_w,micro_size*macro_h)
	pixel=pixel_image.load()
	for w in range(macro_w):
		for h in range(macro_h):
			micro_image=micro_images[assignment[w,h]]
			if cheat:
				micro_image=push(get_pixel(macro_im,w,h),micro_image,ratio=ratio)
			micro_pixels=micro_image.load()
			for i in range(micro_size):
				for j in range(micro_size):
					pixel[micro_size*w+i,micro_size*h+j]=micro_pixels[i,j]
	return pixel_image




im=create_pixel_image(image_path+'main11.jpg',image_path)
save_image(im,'/Users/Giaco/Pictures/Meret_Giaco/11.3.jpg')
im.show()





