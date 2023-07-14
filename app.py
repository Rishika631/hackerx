import streamlit as st
import requests
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

# Set your OpenAI API credentials
API_KEY = "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"

# Front-end
def main():
    st.title("Digital Asset Management App")

    # Add a sidebar with function selection
    function = st.sidebar.selectbox("Select Function", ["Image Transformation", "AI Analysis", "Image Optimization"])

    if function == "Image Transformation":
        # Image Transformation
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        overlay_image = st.file_uploader("Upload overlay image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None and overlay_image is not None:
            transformed_image = perform_image_transformation(uploaded_image, overlay_image)
            st.image(transformed_image, use_column_width=True)

    elif function == "AI Analysis":
        # AI Analysis and Tagging
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            tags = perform_image_analysis(uploaded_image)
            st.write("Tags:", tags)

    elif function == "Image Optimization":
        # Image Optimization
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            width = st.sidebar.slider("Width", 100, 2000, 800, 100)
            height = st.sidebar.slider("Height", 100, 2000, 600, 100)
            optimized_image = perform_image_optimization(uploaded_image, width, height)
            st.image(optimized_image, use_column_width=True)

# Image Transformation
def perform_image_transformation(uploaded_image, overlay_image):
    # Open the uploaded image using Pillow
    image = Image.open(uploaded_image)

    # Add your image transformation logic here
    # This is a placeholder code that returns the uploaded image as is
    transformed_image = image

    # Open the uploaded overlay image using Pillow
    overlay = Image.open(overlay_image).convert("RGBA")

    # Apply overlay
    overlayed_image = Image.alpha_composite(transformed_image.convert("RGBA"), overlay)

    return overlayed_image

# AI Analysis and Tagging
def perform_image_analysis(uploaded_image):
    # Upload the image to OpenAI API for analysis
    response = upload_image_to_openai(uploaded_image)

    # Get the generated image tags from the OpenAI API response
    tags = response["output"]["tags"]

    return tags

# Image Optimization
def perform_image_optimization(uploaded_image, width, height):
    # Open the uploaded image using Pillow
    image = Image.open(uploaded_image)

    # Resize the image for optimization
    resized_image = image.resize((width, height))

    # Convert the image to WebP format
    resized_image.save("optimized_image.webp", "webp", quality=80)

    # Open the optimized image
    optimized_image = Image.open("optimized_image.webp")

    return optimized_image

# Upload image to OpenAI API for analysis
def upload_image_to_openai(uploaded_image):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "image/jpeg"  # Adjust the content type based on the uploaded image type
    }

    files = {"file": uploaded_image.read()}

    response = requests.post("https://api.openai.com/v1/vision/davinci/tags", headers=headers, files=files)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    main()
