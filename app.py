import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from io import BytesIO
import requests
import json
import base64
import boto3
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Set your OpenAI API credentials
API_KEY = "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"

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

# AI-powered Image Analysis and Tagging

client = boto3.client('rekognition')

def image_caption_generator(image_path):
    # Create a tmp folder to save the resized input image
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    # Open the original image
    img = Image.open(image_path)

    # Set the desired size for the resized image
    new_size = (100, 100)

    # Resize the image
    resized_img = img.resize(new_size)

    # Save the resized image
    resized_img.save('tmp/tmp.jpg')

    with open('tmp/tmp.jpg', 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    image_labels = []
    for label in response['Labels']:
        if label['Confidence'] > 70:
            image_labels.append(label['Name'].lower())

    # Generate a prompt by concatenating the image labels
    prompt = 'Generate an image caption for the following image labels: ' + ', '.join(image_labels)

    # Use the OpenAI API to generate image captions
    response = openai.Completion.create(
        model='text-davinci-003',  # Set the appropriate model name or ID
        prompt=prompt,
        temperature=0.5,
        max_tokens=50
    )

    # Extract the generated image captions from the API response
    generated_captions = response['choices'][0]['text']

    output = 'Generated Image Captions:\n' + generated_captions

    return output



# Image Resize with AI Analysis
def resize_image_with_analysis(image, width, height):
    resized_image = image.resize((width, height))
    tags = analyze_image(resized_image)
    return resized_image, tags


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

            # Crop
            st.subheader("Crop")
            left = st.slider("Left", 0, image.width, 0)
            top = st.slider("Top", 0, image.height, 0)
            right = st.slider("Right", 0, image.width, image.width)
            bottom = st.slider("Bottom", 0, image.height, image.height)
            cropped_image = crop_image(image, left, top, right, bottom)
            st.image(cropped_image, use_column_width=True)

            # Transform
            st.subheader("Transform")
            angle = st.slider("Angle", -180, 180, 0)
            scale = st.slider("Scale", 0.1, 5.0, 1.0)
            transformed_image = transform_image(image, angle, scale)
            st.image(transformed_image, use_column_width=True)

            # Focal Point
            st.subheader("Focal Point")
            x = st.slider("X", 0, image.width, int(image.width / 2))
            y = st.slider("Y", 0, image.height, int(image.height / 2))
            size = st.slider("Size", 10, 200, 50)
            focal_point_image = apply_focal_point(image, x, y, size)
            st.image(focal_point_image, use_column_width=True)

            # Effects (Brightness)
            st.subheader("Effects (Brightness)")
            factor = st.slider("Factor", 0.1, 2.0, 1.0)
            brightness_image = apply_brightness(image, factor)
            st.image(brightness_image, use_column_width=True)

            # Overlay
            st.subheader("Overlay")
            overlay_image = st.file_uploader("Upload an overlay image", type=["png"])
            if overlay_image is not None:
                overlay = Image.open(overlay_image)
                overlayed_image = apply_overlay(image, overlay)
                st.image(overlayed_image, use_column_width=True)

            # Frames
            st.subheader("Frames")
            padding = st.slider("Padding", 0, 50, 10)
            framed_image = apply_frame(image, padding)
            st.image(framed_image, use_column_width=True)

    elif function == "AI Analysis":
        # AI Analysis and Tagging
        st.title("Image Caption Generator")

    # Upload an image file
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
        # Save the uploaded image to a temporary file
            with open("uploaded_image.jpg", "wb") as f:
                f.write(uploaded_image.getbuffer())

        # Display the uploaded image
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

        # Generate image captions
            captions = image_caption_generator("uploaded_image.jpg")

        # Display the generated captions
            st.text_area("Generated Captions", value=captions, height=200)

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

if __name__ == "__main__":
    main()
