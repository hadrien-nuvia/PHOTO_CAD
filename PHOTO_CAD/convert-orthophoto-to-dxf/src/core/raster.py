def read_image(image_path):
    from PIL import Image
    image = Image.open(image_path)
    return image

def convert_to_grayscale(image):
    return image.convert("L")

def save_image(image, output_path):
    image.save(output_path)

def process_raster(image_path, output_path):
    image = read_image(image_path)
    gray_image = convert_to_grayscale(image)
    save_image(gray_image, output_path)