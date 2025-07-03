import requests
import json
from PIL import Image
import os
from io import BytesIO


def fetch_maps_data(url):
    """Fetch maps data from the Valorant API"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def download_crop_and_resize_image(image_url, filename, size=(1024, 1024)):
    """Download image from URL, crop to square from center, then resize to specified dimensions"""
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()

        # Open image with PIL
        image = Image.open(BytesIO(response.content))

        # Convert to RGBA if not already (to handle transparency)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Get image dimensions
        width, height = image.size
        print(f"Original image size: {width}x{height}")

        # Calculate crop dimensions for center square
        # Use the smaller dimension as the square size
        crop_size = min(width, height)

        # Calculate crop coordinates (center the crop)
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        right = left + crop_size
        bottom = top + crop_size

        # Crop to square
        cropped_image = image.crop((left, top, right, bottom))
        print(f"Cropped to square: {crop_size}x{crop_size}")

        # Resize the cropped square to final size
        resized_image = cropped_image.resize(size, Image.Resampling.LANCZOS)

        # Save the image
        resized_image.save(f"{filename}.png", "PNG")
        print(f"Downloaded, cropped and resized: {filename}.png")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {image_url}: {e}")
    except Exception as e:
        print(f"Error processing image {filename}: {e}")


def main():
    # API URL
    api_url = "https://valorant-api.com/v1/maps"

    # Create directory for images if it doesn't exist
    if not os.path.exists("map_splashes"):
        os.makedirs("map_splashes")

    # Fetch the data
    data = fetch_maps_data(api_url)

    if not data:
        print("Failed to fetch data from API")
        return

    if data.get("status") != 200:
        print(f"API returned status: {data.get('status')}")
        return

    maps = data.get("data", [])

    if not maps:
        print("No maps data found")
        return

    print(f"Found {len(maps)} maps")

    # Process each map
    for map_data in maps:
        display_name = map_data.get("displayName")
        splash_image = map_data.get("splash")

        if not display_name or not splash_image:
            print(f"Skipping map with missing data: {map_data.get('uuid', 'unknown')}")
            continue

        # Create filename from display name (lowercase)
        filename = os.path.join("map_splashes", display_name.lower())

        # Download, crop and resize the image
        download_crop_and_resize_image(splash_image, filename)

    print("Download complete!")


if __name__ == "__main__":
    main()