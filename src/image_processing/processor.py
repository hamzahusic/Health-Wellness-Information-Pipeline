import os
import logging
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
 
logger = logging.getLogger(__name__)
 
def inspect_image(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Image not found: {path}')
    img = Image.open(path)
    width, height = img.size
    file_size = path.stat().st_size
    return {
        'filename': path.name,
        'format': img.format,
        'mode': img.mode,
        'width': width,
        'height': height,
        'aspect_ratio': round(width / height, 3),
        'file_size_bytes': file_size,
        'file_size_kb': round(file_size / 1024, 1),
    }

def resize_image(path, output_path, width, height, resample=Image.Resampling.LANCZOS):
    img = Image.open(path)
    resized = img.resize((width, height), resample)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resized.save(output_path)
    logger.info(f'Resized {path} -> {output_path} ({width}x{height})')
    return output_path
 
def resize_proportional(path, output_path, max_width=500):
    img = Image.open(path)
    w, h = img.size
    ratio = max_width / w
    new_h = int(h * ratio)
    resized = img.resize((max_width, new_h), Image.Resampling.LANCZOS)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resized.save(output_path)
    logger.info(f'Resized proportionally: {w}x{h} -> {max_width}x{new_h}')
    return output_path

def generate_thumbnail(path, output_path, max_size=(128, 128)):
    img = Image.open(path)
    thumb = img.copy()   
    thumb.thumbnail(max_size, Image.Resampling.LANCZOS)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    thumb.save(output_path)
    logger.info(f'Thumbnail saved: {output_path} {thumb.size}')
    return output_path

def generate_fixed_thumbnail(path, output_path, size=(128, 128),method='pad', bg_color='black'):
    img = Image.open(path).convert('RGB')
    if method == 'fit':
        result = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    elif method == 'pad':
        result = ImageOps.pad(img, size, color=bg_color)
    elif method == 'contain':
        result = ImageOps.contain(img, size)
    else:
        result = ImageOps.cover(img, size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    return output_path

def pro(path, output_path, size=(128, 128), method='pad', bg_color='black'):
    img = Image.open(path).convert('RGB')
    if method == 'fit':
        result = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    elif method == 'pad':
        result = ImageOps.pad(img, size, color=bg_color)
    elif method == 'contain':
        result = ImageOps.contain(img, size)
    else:
        result = ImageOps.cover(img, size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    return output_path

def crop_image(path, output_path, box):
    img = Image.open(path)
    cropped = img.crop(box)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path)
    logger.info(f'Cropped {path} with box {box} -> {output_path}')
    return output_path
 
def crop_top_banner(path, output_path, banner_height=200):
    img = Image.open(path)
    width, height = img.size
    box = (0, 0, width, min(banner_height, height))
    return crop_image(path, output_path, box)
 
def crop_center_square(path, output_path):
    img = Image.open(path)
    w, h = img.size
    side = min(w, h)
    left  = (w - side) // 2
    upper = (h - side) // 2
    box = (left, upper, left + side, upper + side)
    return crop_image(path, output_path, box)

def convert_to_webp(path, output_path, quality=85):
    img = Image.open(path).convert('RGB')  
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'WEBP', quality=quality, optimize=True)
    orig_size = Path(path).stat().st_size
    new_size  = Path(output_path).stat().st_size
    saving_pct = round((1 - new_size / orig_size) * 100, 1)
    logger.info(f'WebP: {orig_size//1024}KB -> {new_size//1024}KB ({saving_pct}% saving)')
    return output_path
 
def convert_to_grayscale(path, output_path):
    img = Image.open(path).convert('L')
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
 
def save_optimised_jpeg(path, output_path, quality=85):
    img = Image.open(path).convert('RGB')
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'JPEG', quality=quality, optimize=True)
    return output_path

def apply_blur(path, output_path, radius=2):
    img = Image.open(path)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    blurred.save(output_path)
    return output_path
 
def apply_sharpen(path, output_path):
    img = Image.open(path)
    sharpened = img.filter(ImageFilter.SHARPEN)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sharpened.save(output_path)
    return output_path
 
def apply_edge_detection(path, output_path):
    img = Image.open(path).convert('L')   # edge detect works best on greyscale
    edges = img.filter(ImageFilter.FIND_EDGES)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    edges.save(output_path)
    return output_path
 
def enhance_contrast(path, output_path, factor=1.5):
    img = Image.open(path)
    enhanced = ImageEnhance.Contrast(img).enhance(factor)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    enhanced.save(output_path)
    return output_path
 
def enhance_brightness(path, output_path, factor=1.2):
    img = Image.open(path)
    enhanced = ImageEnhance.Brightness(img).enhance(factor)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    enhanced.save(output_path)
    return output_path
 
def enhance_color(path, output_path, factor=1.3):
    img = Image.open(path)
    enhanced = ImageEnhance.Color(img).enhance(factor)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    enhanced.save(output_path)
    return output_path