# Mosaik Image
A code that fits the pixels of a given (macro)image to small images of a given image collection. You find an example image at `mosaik_images/test.jpeg`.

## How to generate your own image
Use `mosaik_main.py` and hand over parser arguments. By default it uses the macro image at `makro_images/main5.jpg` and the micro images
from the folder `preprocessed_size=45` and generates the mosaik image that you find at `mosaik_images/test.jpeg`. 
<br/>
You have a lot of freedom to design your very own mosaik image! In the following I explain the paramerters you can set in `mosaik_main.py` in more detail.\
**--path_to_macro_img**, the path to the macro image.\
**--path_to_image_folder'**, the path to the folder where you store all the **unprocessed** micro images you want to use.\
**--load_preprocessed_img'**, if True it assumes that you have already preprocessed the micro images at the appropriate size and it loads it from that folder. In that case you don't need care about the argument `--path_to_image_folder`.\
**--save_path**, the path where you want to store your final mosaik image.\
**--micro_size**, the micro images are calculated as squares of size micro_size. Don't make it too small because otherwise you don't recognize the micro images anymore. If too large it will make the final mosaik images propably too large.\
**--macro_height**, the number of pixels (each corresponding to a micro image) in the macro image's height.\
**--temperature**, an integer that helps to controll the variety in the mosaik image. More precisely, for each pixel the programm searches the best fitting n=temperature images and will select the one that has been used the least often. Hence, a small number will likely make a boring mosaik. A good number is somewhere between 20-50 depending on your data set.\
**--amount_of_augmentation**, a number between 0 and 1. This is a little "cheat" by pushing each image to the proper pixel color. If 0, it will not make any image augmentation and leave them as they are. On the other hand a number of 1 changes the micro images in a way such that their average color corresponds exactly to the actual pixel values of the macro image. Again, this value is a question of design and depends on your taste and data set. I suggest a value between 0.1 and 0.3.
