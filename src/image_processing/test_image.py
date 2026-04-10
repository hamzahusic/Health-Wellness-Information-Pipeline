from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import os
from processor import inspect_image , resize_image, resize_proportional, generate_thumbnail, generate_fixed_thumbnail, crop_top_banner, crop_center_square, crop_image, convert_to_webp, convert_to_grayscale, save_optimised_jpeg, apply_blur, apply_sharpen, apply_edge_detection, enhance_contrast, enhance_brightness, enhance_color

 
img = Image.open('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg')

# Core attributes 
# print('Size (W x H):', img.size)  
# print('Mode:', img.mode)       
# print('Format:', img.format)          
 
# # File size on disk
# file_size = os.path.getsize('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg')
# print(f'File size: {file_size / 1024:.1f} KB')
 
# width, height = img.size
# print(f'Width: {width}px  Height: {height}px')
# print(f'Aspect ratio: {width/height:.2f}')

#single image
# image_path = 'data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg'
# image_properties = inspect_image(image_path)
# print("Image Properties:")
# print(f"Filename: {image_properties['filename']}")
# print(f"Format: {image_properties['format']}")
# print(f"Mode: {image_properties['mode']}")
# print(f"Width: {image_properties['width']}px")
# print(f"Height: {image_properties['height']}px")
# print(f"Aspect Ratio: {image_properties['aspect_ratio']}")
# print(f"File Size: {image_properties['file_size_kb']} KB")

# all images in images folder
# images_dir = 'data/raw/images'
# image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]

# for image_file in image_files:
#     image_path = os.path.join(images_dir, image_file)
#     if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
#         try:
#             image_properties = inspect_image(image_path)
            
#             print(f"\nInspecting Image: {image_properties['filename']}")
#             print(f"Format: {image_properties['format']}")
#             print(f"Mode: {image_properties['mode']}")
#             print(f"Width: {image_properties['width']}px")
#             print(f"Height: {image_properties['height']}px")
#             print(f"Aspect Ratio: {image_properties['aspect_ratio']}")
#             print(f"File Size: {image_properties['file_size_kb']} KB")
#         except FileNotFoundError:
#             print(f"File not found: {image_path}")
#         except Exception as e:
#             print(f"Error inspecting {image_path}: {str(e)}")

# test resizing
 
# image_path = 'data/raw/images/tVvpFIoteRHNnoZMhdnwIVwJpCA.jpg'
# resize_image(image_path, 'data/processed/resized/poster_300x450.jpg', 300, 450)
# resize_proportional(image_path, 'data/processed/resized/poster_w500.jpg', max_width=500)
 
# Verify
# img = Image.open('data/processed/resized/poster_w500.jpg')
# print('New size:', img.size)

# test thumbnails
# image_path = 'data/raw/images/bRBeSHfGHwkEpImlhxPmOcUsaeg.jpg'

# output_thumbnail_path = 'data/processed/thumbnails/thumbnail.jpg'
# generate_thumbnail(image_path, output_thumbnail_path, max_size=(128, 128))
# print(f"Thumbnail generated at {output_thumbnail_path}")

# output_fixed_thumbnail_path = 'data/processed/thumbnails/fixed_thumbnail.jpg'
# generate_fixed_thumbnail(image_path, output_fixed_thumbnail_path, size=(128, 128), method='pad', bg_color='white')
# print(f"Fixed thumbnail generated at {output_fixed_thumbnail_path}")

src = 'data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg'
# crop_top_banner(src, 'data/processed/cropped/banner.jpg', banner_height=200)

# crop_center_square(src, 'data/processed/cropped/square.jpg')
# crop_image(src, 'data/processed/cropped/custom.jpg', box=(50, 50, 290, 350))

# img = Image.open('data/processed/cropped/square.jpg')
# print('Cropped size:', img.size)  

# webp_output_path = 'data/processed/converted/image.webp'
# convert_to_webp(src, webp_output_path, quality=85)
# print(f"WebP image generated at {webp_output_path}")

# grayscale_output_path = 'data/processed/converted/grayscale_image.jpg'
# convert_to_grayscale(src, grayscale_output_path)
# print(f"Grayscale image generated at {grayscale_output_path}")

# jpeg_output_path = 'data/processed/converted/optimized_image.jpg'
# save_optimised_jpeg(src, jpeg_output_path, quality=85)
# print(f"Optimized JPEG image generated at {jpeg_output_path}")


blurred_image_path = 'data/processed/blurred/blurred_image.jpg'
apply_blur('data/raw/images/tVvpFIoteRHNnoZMhdnwIVwJpCA.jpg', blurred_image_path, radius=5)
print(f"Blurred image saved at {blurred_image_path}")

sharpened_image_path = 'data/processed/sharpened/sharpened_image.jpg'
apply_sharpen('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg', sharpened_image_path)
print(f"Sharpened image saved at {sharpened_image_path}")

edge_detected_image_path = 'data/processed/edged/edge_detected_image.jpg'
apply_edge_detection('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg', edge_detected_image_path)
print(f"Edge-detected image saved at {edge_detected_image_path}")

contrast_enhanced_image_path = 'data/processed/contrast/contrast_enhanced_image.jpg'
enhance_contrast('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg', contrast_enhanced_image_path, factor=2.0)
print(f"Contrast enhanced image saved at {contrast_enhanced_image_path}")

brightness_enhanced_image_path = 'data/processed/brightness/brightness_enhanced_image.jpg'
enhance_brightness('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg', brightness_enhanced_image_path, factor=1.5)
print(f"Brightness enhanced image saved at {brightness_enhanced_image_path}")

color_enhanced_image_path = 'data/processed/color/color_enhanced_image.jpg'
enhance_color('data/raw/images/6a77e303-14eb-4d8c-917a-fa045a548a6c.jpg', color_enhanced_image_path, factor=1.5)
print(f"Color enhanced image saved at {color_enhanced_image_path}")

def verify_image(image_path):
    try:
        img = Image.open(image_path)
        print(f"Verified {image_path}, Size: {img.size}, Format: {img.format}")
    except Exception as e:
        print(f"Error verifying image {image_path}: {e}")

# Verify the images after transformations
verify_image(blurred_image_path)
verify_image(sharpened_image_path)
verify_image(edge_detected_image_path)
verify_image(contrast_enhanced_image_path)
verify_image(brightness_enhanced_image_path)
verify_image(color_enhanced_image_path)