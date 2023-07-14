import streamlit as st
import torch
from torchvision.transforms import functional as F
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import os
import requests

# Set your OpenAI API key
openai.api_key = "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"

# Download the CLIP model checkpoint
model_url = "https://cdn.openai.com/clip/models/clip-vit-base-patch32.pt"
model_path = "clip-vit-base-patch32.pt"

if not os.path.exists(model_path):
    response = requests.get(model_url)
    with open(model_path, 'wb') as f:
        f.write(response.content)

# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = torch.jit.load(model_path).to(device).eval()
preprocess = torch.nn.Sequential(
    F.resize((224, 224)),
    F.to_tensor(),
    F.normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
)

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

# Function for image caption generation
def generate_image_caption(image_path):
    # Open the original image
    img = Image.open(image_path).convert("RGB")

    # Preprocess the image for CLIP model
    image = preprocess(img).unsqueeze(0).to(device)

    # Generate a prompt using the image features
    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        image_prompt = "Image features:"
        for feat in image_features[0]:
            image_prompt += f"\n{feat:.3f}"

    # Use the OpenAI API to generate image captions
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=image_prompt,
        temperature=0.5,
        max_tokens=50
    )

    # Extract the generated image captions from the API response
    generated_captions = response['choices'][0]['text']

    output = 'Generated Image Captions:\n' + generated_captions

    return output

# Streamlit App
def main():
    st.title("Digital Asset Management App")

    # Add a sidebar with function selection
    function = st.sidebar.selectbox("Select Function", ["Image Transformation", "AI Analysis"])

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
            captions = generate_image_caption("uploaded_image.jpg")

            # Display the generated captions
            st.text_area("Generated Captions", value=captions, height=200)

# Run the app
if __name__ == "__main__":
    main()
