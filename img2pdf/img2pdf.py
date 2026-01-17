import os
from PIL import Image, ImageDraw, ImageFont


def get_image_files(directory):
    exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    try:
        files = [f for f in os.listdir(directory) if f.lower().endswith(exts)]
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
        return []
    files.sort()
    return files

def get_image_stats(image_files, directory):
    sizes = []
    for fname in image_files:
        with Image.open(os.path.join(directory, fname)) as img:
            sizes.append(img.size)
    return sizes

def suggest_size(sizes):
    from collections import Counter
    counter = Counter(sizes)
    most_common = counter.most_common(1)[0][0]
    return most_common

def resize_images(image_files, directory, target_size):
    images = []
    for fname in image_files:
        with Image.open(os.path.join(directory, fname)) as img:
            if img.size != target_size:
                img = img.resize(target_size, Image.ANTIALIAS)
            images.append(img.convert('RGB'))
    return images

def main():
    ########################################Input Source Directory Here########################################
    input_src = '/Users/meraz/Desktop/MyLearning/LLM/LLMs-from-scratch-pic/lec2'
    
    ###########################################################################################################
    directory = input_src.strip() or '.'
    try:
        image_files = get_image_files(directory)
    except Exception as e:
        print(f"Error reading directory: {e}")
        return
    if not image_files:
        print('No images found or directory not found.')
        return
    print(f'Found {len(image_files)} images:')
    for idx, fname in enumerate(image_files, 1):
        print(f'{idx}: {fname}')
    sizes = get_image_stats(image_files, directory)
    print('\nImage sizes:')
    for fname, size in zip(image_files, sizes):
        print(f'{fname}: {size}')
    if len(set(sizes)) > 1:
        print('\nImages have different sizes.')
        target_size = suggest_size(sizes)
        print(f'Suggested standard size: {target_size}')
        resize = input('Resize all images to this size? (y/n): ').strip().lower() == 'y'
    else:
        target_size = sizes[0]
        resize = False
    seq = input('Enter image sequence (e.g. 1-5) or "all" (default: all): ').strip().lower()
    if seq == '' or seq == 'all':
        selected = image_files
    else:
        try:
            start, end = map(int, seq.split('-'))
            selected = image_files[start-1:end]
        except Exception:
            print('Invalid input. Using all images.')
            selected = image_files
    def add_filename_overlay(img, fname, page_num, total_pages):
        from PIL import ImageDraw, ImageFont
        overlay = img.copy()
        fname_clean = os.path.splitext(fname)[0].replace('screenshot', '').strip('_- ')
        # Add page number info
        text_label = f"{fname_clean}   {page_num}/{total_pages}"
        overlay_height = int(img.height * 0.05)  # Even smaller height for font and box
        font_size = int(overlay_height * 0.5)    # Even smaller font size for text
        font = None
        tried_fonts = []
        for font_name in ["arial.ttf", "DejaVuSans.ttf", "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except Exception:
                tried_fonts.append(font_name)
        if font is None:
            print("Warning: No scalable TTF font found (tried: %s). Using default font, which may not scale properly." % ', '.join(tried_fonts))
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(overlay)
        # Calculate text size
        try:
            bbox = draw.textbbox((0, 0), text_label, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(text_label, font=font)
        text_x = (img.width - text_w) // 2
        text_y = int(overlay_height * 0.2)
        # Draw white rounded rectangle behind text
        rect_pad_x = 40   # Decreased horizontal padding for shorter box
        rect_pad_y = 10   # Decreased vertical padding
        rect_x0 = text_x - rect_pad_x
        rect_y0 = text_y - rect_pad_y
        rect_x1 = text_x + text_w + rect_pad_x
        rect_y1 = text_y + text_h + rect_pad_y
        rectangle_color = (255, 255, 255, 230)  # White, mostly opaque
        border_color = (255, 215, 0, 255)       # Yellow border (Gold)
        border_width = 3
        radius = 12
        if overlay.mode != 'RGBA':
            overlay = overlay.convert('RGBA')
        draw = ImageDraw.Draw(overlay)
        # Draw rounded rectangle (Pillow >= 8.2.0)
        try:
            draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=radius, fill=rectangle_color, outline=border_color, width=border_width)
        except AttributeError:
            # Fallback to normal rectangle if rounded_rectangle not available
            draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=rectangle_color, outline=border_color, width=border_width)
        draw.text((text_x, text_y), text_label, fill=(0, 0, 0, 255), font=font)  # Black text for contrast
        return overlay.convert('RGB')
    total_pages = len(selected)
    if resize:
        images = []
        for idx, fname in enumerate(selected):
            img = Image.open(os.path.join(directory, fname)).convert('RGB')
            if img.size != target_size:
                img = img.resize(target_size, Image.ANTIALIAS)
            img = add_filename_overlay(img, fname, idx+1, total_pages)
            images.append(img)
    else:
        images = []
        for idx, fname in enumerate(selected):
            img = Image.open(os.path.join(directory, fname)).convert('RGB')
            img = add_filename_overlay(img, fname, idx+1, total_pages)
            images.append(img)
    outname = input(f'Enter output PDF filename (default: {input_src}.pdf): ').strip() or input_src+'.pdf'
    images[0].save(outname, save_all=True, append_images=images[1:])
    print(f'PDF saved as {outname}')

if __name__ == '__main__':
    main()
