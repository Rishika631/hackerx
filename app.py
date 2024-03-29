import streamlit as st
import torch
from torchvision.transforms import functional as F
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import os
import requests
from datetime import datetime
import openai
import io
import pymongo
import base64

# Set your OpenAI API key
# openai.api_key = <APIKEY>
API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
headers = {"Authorization": "Bearer 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"}
# Set up MongoDB connection
client = pymongo.MongoClient("mongodb+srv://Rishika:taylorswift@cluster0.acug8d2.mongodb.net/?retryWrites=true&w=majority")
db = client["image_tags_db"]
collection1 = db["image_tags"]
collection = db["transformation_logs"]

# Initialize a list to store transformation logs
transformation_logs = []

# Function to log transformation details
def log_transformation_details(transformation_type, details):
    log_entry = {
        "type": transformation_type,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    collection.insert_one(log_entry)
    # transformation_logs.append(log_entry)

# Image Transformation: Crop
def crop_image(image, left, top, right, bottom):
    cropped_image = image.crop((left, top, right, bottom))
    log_transformation_details("Crop", {
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                })
    return cropped_image

# Image Transformation: Transform
def transform_image(image, angle, scale):
    transformed_image = image.rotate(angle)
    transformed_image = transformed_image.resize((int(image.width * scale), int(image.height * scale)))
    
    # Log transformation details
    log_transformation_details("Transform", {
        "angle": angle,
        "scale": scale,
    })
    
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
        # Store the generated captions in the MongoDB database
        db_entry = {"image_path": image_path, "captions": generated_captions}
        collection.insert_one(db_entry)
        output = "Generated Image Captions:\n" + "\n".join(generated_captions)
    else:
        output = "Error generating captions. Please try again."

    return output

def query(file):
    response = requests.post(API_URL, headers=headers, data=file)
    return response.text

def encode_html_as_base64(html_filename):
    with open(html_filename, "rb") as html_file:
        html_content = html_file.read()
    encoded_html = base64.b64encode(html_content).decode("utf-8")
    return encoded_html

# Image Resize with AI Analysis
def resize_image_with_analysis(image, width, height):
    resized_image = image.resize((width, height))
    return resized_image

# Image Transformation: Format Conversion
def convert_format(image, new_format):
    buffered = io.BytesIO()
    image.save(buffered, format=new_format)
    return Image.open(buffered)


# Image Transformation: Compression
def compress_image(image, quality):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=quality)
    return Image.open(buffered)

# Streamlit App
def main():
    st.title("Digital Asset Management App")

    # Add a sidebar with function selection
    function = st.sidebar.selectbox("Select Function", ["Image Transformation", "AI Analysis", "Image Resize","Image Optimization","Drawing Canvas"])

    if function == "Image Transformation":
        # Image Transformation
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)

            # Transformation Options
            transformation_option = st.selectbox("Select Transformation", ["Crop", "Transform", "Focal Point", "Brightness", "Overlay", "Frames"])

            if transformation_option == "Crop":
                # Crop
                st.subheader("Crop")
                left = st.slider("Left", 0, image.width, 0)
                top = st.slider("Top", 0, image.height, 0)
                right = st.slider("Right", 0, image.width, image.width)
                bottom = st.slider("Bottom", 0, image.height, image.height)
                cropped_image = crop_image(image, left, top, right, bottom)
                
                st.image(cropped_image, use_column_width=True)

                
                # log_entry = {
                #     "type": "Crop",
                #     "details": {
                #      "left": left,
                #      "top": top,
                #      "right": right,
                #      "bottom": bottom,
                #  },
                # }
                # collection1.insert_one(log_entry)

            elif transformation_option == "Transform":
                # Transform
                st.subheader("Transform")
                angle = st.slider("Angle", -180, 180, 0)
                scale = st.slider("Scale", 0.1, 5.0, 1.0)
                transformed_image = transform_image(image, angle, scale)
                st.image(transformed_image, use_column_width=True)

            
        

            elif transformation_option == "Focal Point":
                # Focal Point
                st.subheader("Focal Point")
                x = st.slider("X", 0, image.width, int(image.width / 2))
                y = st.slider("Y", 0, image.height, int(image.height / 2))
                size = st.slider("Size", 10, 200, 50)
                focal_point_image = apply_focal_point(image, x, y, size)
                st.image(focal_point_image, use_column_width=True)

            elif transformation_option == "Brightness":
                # Effects (Brightness)
                st.subheader("Effects (Brightness)")
                factor = st.slider("Factor", 0.1, 2.0, 1.0)
                brightness_image = apply_brightness(image, factor)
                st.image(brightness_image, use_column_width=True)

            elif transformation_option == "Overlay":
                # Overlay
                st.subheader("Overlay")
                overlay_image = st.file_uploader("Upload an overlay image", type=["png"])
                if overlay_image is not None:
                    overlay = Image.open(overlay_image)
                    overlayed_image = apply_overlay(image, overlay)
                    st.image(overlayed_image, use_column_width=True)

            elif transformation_option == "Frames":
                # Frames
                st.subheader("Frames")
                padding = st.slider("Padding", 0, 50, 10)
                framed_image = apply_frame(image, padding)
                st.image(framed_image, use_column_width=True)
            

    elif function == "AI Analysis":
    # AI Analysis and Tagging
        st.title("Image Caption Generator")

    # Upload an image file
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])

        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            output = query(image_bytes)
            st.text_area("Generated Captions:", value=output, height=200)

        # Store the generated captions in the MongoDB database
            db_entry = {"image_path": uploaded_file.name, "captions": output.split("\n")}
            collection1.insert_one(db_entry)

    elif function == "Image Resize":
        # Image Resize with AI Analysis
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            width = st.slider("Width", 100, 2000, 800, 100)
            height = st.slider("Height", 100, 2000, 600, 100)
            resized_image = resize_image_with_analysis(image, width, height)
            st.image(resized_image, use_column_width=True)

    elif function == "Drawing Canvas":
        st.title("Drawing Canvas")

        st.markdown(
            '<a href="https://rishika631.github.io/techsurf/" target="_blank" rel="noopener noreferrer">Open Drawing Canvas in New Tab</a>',
            unsafe_allow_html=True
        )

    elif function == "Image Optimization":
        st.title("Image Optimization")

    # Upload an image file
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Original Image", use_column_width=True)

        # Optimization Options
            option = st.selectbox("Select Optimization Option", ["Format Conversion", "Compression"])

            if option == "Format Conversion":
                st.subheader("Format Conversion")
                format_option = st.selectbox("Select Format", ["JPEG", "PNG"])
                converted_image = convert_format(image, format_option)
                st.image(converted_image, caption=f"Converted to {format_option}", use_column_width=True)

            elif option == "Compression":
                st.subheader("Compression")
                quality = st.slider("Quality (0-100)", 0, 100, 75)
                compressed_image = compress_image(image, quality)
                st.image(compressed_image, caption=f"Compressed (Quality: {quality})", use_column_width=True)
                if st.button("Download Compressed Image"):
                    # Save the compressed image to a BytesIO object
                    compressed_buffered = io.BytesIO()
                    compressed_image.save(compressed_buffered, format="JPEG", quality=quality)
                
                # Provide the download link
                    st.download_button(
                        label="Click to download",
                        data=compressed_buffered.getvalue(),
                        file_name="compressed_image.jpg",  # Change the file name and extension accordingly
                        mime="image/jpeg"
                    )
        

# Run the app
if __name__ == "__main__":
    main()
