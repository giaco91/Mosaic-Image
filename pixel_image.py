from PIL import Image,ExifTags
import os
import numpy as np


# Open an Image
def open_image(path,rotate=False):
  img = Image.open(path)
  try:
  	img._getexif()
  except:
  	if rotate:
  		print('Warning: could not rotate that image because the necessary meta data is not given for that image.')
  	rotate=False
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

def resize(image,width,height):
	img=image.resize((width,height),Image.ANTIALIAS)
	return img

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
	preprocessed_image_path='preprocessed_size='+str(size)+'/'
	preprocessed_micro_images=[]
	if load==False:
		if not os.path.exists(preprocessed_image_path):
			os.mkdir(preprocessed_image_path)
		for im_name in os.listdir(path_micro_images):
			if im_name[0]!='.' and im_name.endswith(".jpg"):
				im=open_image(path_micro_images+im_name,rotate=True)
				im=square_crop(im)
				im=resize_to_height_ref(im,size).convert('RGB')
				preprocessed_micro_images.append(im)
				print('save_image....')
				save_image(im,preprocessed_image_path+im_name)
	else:
		if not os.path.exists(preprocessed_image_path):
			raise ValueError('can not load processed images because directory does not exist')
		else:
			for im_name in os.listdir(preprocessed_image_path):
				if im_name.endswith(".jpg"):
					im=open_image(preprocessed_image_path+im_name).copy()
					preprocessed_micro_images.append(im.convert('RGB'))
	return preprocessed_micro_images

def get_assignment(macro_im,averages,temp=5):
	#temp>0 allowes inoptimal assigments for adding a sampling feature
	temp=int(np.ceil(temp))
	W,H=macro_im.size
	im_matrix=-np.ones((W,H))
	d=np.zeros(len(averages))
	counter=np.zeros(len(averages))
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
			sorted_idx=np.argsort(d)[:temp]#void of perfect fit helps also for diversity!
			if temp>10:
				s=1
				if temp>30:
					s=2
				neighbours=[]
				for nw in range(max(0,w-s),min(W,w+s+1)):
					for nh in range(max(0,h-s),min(H,h+s+1)):
						if im_matrix[nw,nh]!=-1:
							neighbours.append(int(im_matrix[nw,nh]))
				sorted_idx=list(set(sorted_idx)-set(neighbours))
			selected_counts=counter[sorted_idx]
			smallest_occurence_idx=np.argsort(selected_counts)[0]
			selected_idx=sorted_idx[smallest_occurence_idx]
			counter[selected_idx]+=1
			im_matrix[w,h]=selected_idx
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

def create_pixel_image(path_macro_image,path_micro_images,macro_size=60,micro_size=40,load=False,temp=5,ratio=0.25):
	macro_im=open_image(path_macro_image,rotate=True)
	#macro_im=resize_to_height_ref(macro_im,macro_size)
	macro_im=resize(macro_im,macro_size[0],macro_size[1])
	macro_w,macro_h=macro_im.size
	print('getting prepocessed micro images...')
	micro_images=get_preprocessed_micro_images(path_micro_images,micro_size,load=load)
	#micro_images2=get_preprocessed_micro_images('/Users/Giaco/Desktop/pics/',micro_size,load=load)
	#micro_images=micro_images1+micro_images2
	averages=[]
	for micro_im in micro_images:
		averages.append(calc_average_rgb(micro_im))
	print('calculating the assignents...')
	assignment=get_assignment(macro_im,averages,temp=temp)
	pixel_image=create_image(micro_size*macro_w,micro_size*macro_h)
	pixel=pixel_image.load()
	print('constructing the mosaik image...')
	for w in range(macro_w):
		p=int(w/macro_w*100)
		if p%10==0:
			print('progress: '+str(p)+'%')
		for h in range(macro_h):
			micro_image=micro_images[assignment[w,h]]
			if ratio is not None:
				micro_image=push(get_pixel(macro_im,w,h),micro_image,ratio=ratio)
			micro_pixels=micro_image.load()
			for i in range(micro_size):
				for j in range(micro_size):
					pixel[micro_size*w+i,micro_size*h+j]=micro_pixels[i,j]
	return pixel_image

# image_path='/Volumes/TOSHIBA EXT/Meret und Sandro/'
# n='mesa.jpg'
# macro_path='/Users/Giaco/Desktop/'+n
# im=create_pixel_image(macro_path,image_path,macro_size=[200,150],micro_size=50,load=True,temp=40,ratio=0.25)
# if not os.path.exists('mosaik_images/'):
# 	os.makedirs('mosaik_images/')
# save_image(im,'mosaik_images/'+'mosaik_75_100_'+n)
# im.show()

# image_path='/Volumes/TOSHIBA EXT/Fotoalbum-Kindheit-Sandro-Mario-Amanda-1991-2008/'
# n_list=['familie.jpg']
# for n in n_list: 
# 	macro_path='/Users/Giaco/Desktop/'+n
# 	im=create_pixel_image(macro_path,image_path,macro_size=[200,150],micro_size=48,load=True,temp=40,ratio=0.1)
# 	if not os.path.exists('mosaik_images/'):
# 		os.makedirs('mosaik_images/')
# 	w,h=im.size
# 	print('the size of the final image is: '+str(w)+' x '+str(h))
# 	save_image(im,'mosaik_images/'+'diverse_'+n)


img = Image.open('mosaik_images/mosaik_75_100_mesa.jpg')
img.save('mosaik_images/mosaik_75_100_mesa.jpeg',format='JPEG')
