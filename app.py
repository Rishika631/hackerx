import streamlit as st
import torch
from torchvision.transforms import functional as F
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import os
import requests
from transformers import CLIPProcessor, CLIPModel
import openai

# Set your OpenAI API key
openai.api_key = "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"
API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
headers = {"Authorization": "Bearer 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"}

# Image Transformation: Crop
def crop_image(image, left, top, right, bottom):
    return image.crop((left, top, right, bottom))

# Image Transformation: Transform
def transform_image(image, angle, scale):
    transformed_image = image.rotate(angle)
    transformed_image = transformed_image.resize((int(image.width * scale), int(image.height * scale)))
    return transformed_image

# Image Transformation: Focal Point
def apply_focal_point(image, x, y, size):
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=10))
    cropped_image = crop_image(blurred_image, x - size, y - size, x + size, y + size)
    return cropped_image

# Image Transformation: Effects (Brightness)
def apply_brightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(factor)
    return enhanced_image

# Image Transformation: Overlay
def apply_overlay(image, overlay_path):
    overlay = Image.open(overlay_path).convert("RGBA")
    overlayed_image = Image.alpha_composite(image.convert("RGBA"), overlay)
    return overlayed_image

# Image Transformation: Frames
def apply_frame(image, padding):
    framed_image = ImageOps.expand(image, border=padding, fill="white")
    return framed_image

def generate_image_caption(image_path):

    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(API_URL, headers=headers, files=files)

    if response.status_code == 200:
        result = response.json()
        generated_captions = result["predictions"]
        output = "Generated Image Captions:\n" + "\n".join(generated_captions)
    else:
        output = "Error generating captions. Please try again."

    return output

def query(file):
    response = requests.post(API_URL, headers=headers, data=file)
    return response.text

# Image Resize with AI Analysis
def resize_image_with_analysis(image, width, height):
    resized_image = image.resize((width, height))
    resized_image_bytes = resized_image.read()
    output = query(image)
    return resized_image, output


# Streamlit App
def main():
    st.title("Digital Asset Management App")

    # Add a sidebar with function selection
    function = st.sidebar.selectbox("Select Function", ["Image Transformation", "AI Analysis", "Image Resize"])

    if function == "Image Transformation":
        # Image Transformation
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)

            # Crop, Transform, Focal Point, Brightness, Overlay, Frames
            # ...

    elif function == "AI Analysis":
        # AI Analysis and Tagging
        st.title("Image Caption Generator")

        # Upload an image file
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])

        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            output = query(image_bytes)
            # Display the generated captions
            st.text_area("Generated Captions:", value=output, height=200)

    elif function == "Image Resize":
        # Image Resize with AI Analysis
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            width = st.slider("Width", 100, 2000, 800, 100)
            height = st.slider("Height", 100, 2000, 600, 100)
            resized_image, tags = resize_image_with_analysis(image, width, height)
            st.image(resized_image, use_column_width=True)
            st.write("Tags:", tags)

# Run the app
if __name__ == "__main__":
    main()
