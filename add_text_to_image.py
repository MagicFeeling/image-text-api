#!/usr/bin/env python3
"""
Image Text Overlay Tool

Adds text to images (SFW and NSFW) with configurable font, size, color, and position.
Original images are preserved; new files are created with specified output names.
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file and expand paths."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Expand project_folder path if it exists
        if "project_folder" in config:
            project_folder = Path(config["project_folder"]).expanduser()
            config["project_folder"] = str(project_folder)

        return config
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def add_text_to_image(
    input_path: str,
    output_path: str,
    text: str,
    font_path: str,
    font_size_percent: float,
    color: str,
    position: str = "bottom",
    blur: bool = False,
    blur_radius: int = 15,
    num_images: int = None
) -> None:
    """
    Add text to an image and save to a new file.

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        text: Text to add to image
        font_path: Path to TrueType font file
        font_size_percent: Font size as percentage of image height
        color: Color as hex string (e.g., "#FFFFFF") or RGB tuple
        position: Text position ("bottom", "top", or "center")
        blur: Whether to blur the image before adding text
        blur_radius: Blur radius (higher = more blur)
        num_images: Optional number of images to append to text (e.g., " (3 images)")
    """
    try:
        # Open the image
        img = Image.open(input_path)

        # Apply blur if requested
        if blur:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Get image dimensions and calculate font size
        img_width, img_height = img.size
        font_size = int(img_height * (font_size_percent / 100))

        draw = ImageDraw.Draw(img)

        # Load font
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            print(f"Warning: Could not load font '{font_path}'. Using default font.")
            font = ImageFont.load_default()

        # Convert color
        if isinstance(color, str):
            rgb_color = hex_to_rgb(color)
        else:
            rgb_color = color

        # Get main text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Prepare image count text if provided
        count_text = None
        count_font = None
        count_height = 0
        if num_images is not None:
            image_word = "images" if num_images > 1 else "image"
            count_text = f"({num_images} {image_word})"
            # Make count font size 60% of main font size
            count_font_size = int(font_size * 0.6)
            try:
                count_font = ImageFont.truetype(font_path, count_font_size)
            except OSError:
                count_font = ImageFont.load_default()

            # Get count text dimensions
            count_bbox = draw.textbbox((0, 0), count_text, font=count_font)
            count_height = count_bbox[3] - count_bbox[1]

        # Calculate total height (main text + count text with spacing)
        total_height = text_height
        if count_text:
            spacing = int(font_size * 0.2)  # 20% of main font size for spacing
            total_height += spacing + count_height

        # Calculate position for main text
        x = (img_width - text_width) // 2  # Center horizontally

        if position == "bottom":
            # Position in lower part of image with padding
            y = img_height - total_height - (img_height // 10)
        elif position == "top":
            y = img_height // 10
        else:  # center
            y = (img_height - total_height) // 2

        # Draw text with outline for better visibility
        outline_color = (0, 0, 0) if sum(rgb_color) > 384 else (255, 255, 255)

        # Draw outline for main text
        for adj_x in range(-2, 3):
            for adj_y in range(-2, 3):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=rgb_color)

        # Draw count text if provided
        if count_text and count_font:
            spacing = int(font_size * 0.2)
            count_y = y + text_height + spacing
            count_bbox = draw.textbbox((0, 0), count_text, font=count_font)
            count_width = count_bbox[2] - count_bbox[0]
            count_x = (img_width - count_width) // 2

            # Draw outline for count text
            for adj_x in range(-2, 3):
                for adj_y in range(-2, 3):
                    draw.text((count_x + adj_x, count_y + adj_y), count_text, font=count_font, fill=outline_color)

            # Draw count text
            draw.text((count_x, count_y), count_text, font=count_font, fill=rgb_color)

        # Save the output image
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        img.save(output_path)

        print(f"✓ Created: {output_path}")

    except FileNotFoundError:
        print(f"Error: Input image not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing image {input_path}: {e}")
        sys.exit(1)


def get_number_of_images(project_folder: str, subfolder: str) -> int:
    """
    Count the number of image files (PNG, JPG, JPEG) in a project subfolder.

    Args:
        project_folder: Base project folder path
        subfolder: Subfolder name (e.g., "SFW" or "NSFW")

    Returns:
        Number of image files in the specified folder
    """
    folder_path = Path(project_folder) / subfolder

    if not folder_path.exists():
        print(f"Warning: Folder not found: {folder_path}")
        return 0

    # Count image files in the folder (png, jpg, jpeg - case insensitive)
    image_files = []
    for pattern in ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]:
        image_files.extend(folder_path.glob(pattern))

    return len(image_files)


def _update_prompt_file(file_path: Path, num_images: int) -> None:
    """
    Helper function to update a prompt file with image count.

    Args:
        file_path: Path to the prompt file
        num_images: Number of images to insert
    """
    import re

    if not file_path.exists():
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the number and make "image" plural if num_images > 1
        image_word = "images" if num_images > 1 else "image"
        # Pattern to match: (any number image/images)
        content = re.sub(r'\(\d+\s+images?\)', f'({num_images} {image_word})', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Updated {file_path} with {num_images} {image_word}")
    except Exception as e:
        print(f"Warning: Failed to update {file_path.name}: {e}")


def _update_socialmedia_file(file_path: Path, num_images: int, platform: str) -> None:
    """
    Helper function to update socialmedia.txt with image count after a platform name.

    Args:
        file_path: Path to the socialmedia.txt file
        num_images: Number of images to insert
        platform: Platform name to insert count after (e.g., "Patreon" or "Fanvue")
    """
    import re

    if not file_path.exists():
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determine singular/plural
        image_word = "images" if num_images > 1 else "image"
        new_text = f" ({num_images} {image_word})"

        # Remove any existing image count after the platform name
        content = re.sub(rf'{platform}\s*\([^)]+\)', platform, content)

        # Insert the new image count after the platform name
        # Handle both cases: "Platform!" and "Platform &"
        content = re.sub(rf'{platform}(?=\s*[&!])', f'{platform}{new_text}', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Updated {file_path} with {num_images} {image_word} for {platform}")
    except Exception as e:
        print(f"Warning: Failed to update {file_path.name} for {platform}: {e}")


def add_number_to_prompts_sfw(project_folder: str, num_images: int) -> None:
    """
    Update SFW prompt files with the number of images.

    Args:
        project_folder: Base project folder path
        num_images: Number of images to insert into prompts
    """
    prompts_folder = Path(project_folder) / "Prompts"

    if not prompts_folder.exists():
        print(f"Warning: Prompts folder not found: {prompts_folder}")
        return

    # Update patreon.txt
    _update_prompt_file(prompts_folder / "patreon.txt", num_images)

    # Update socialmedia.txt with Patreon count
    _update_socialmedia_file(prompts_folder / "socialmedia.txt", num_images, "Patreon")


def add_number_to_prompts_nsfw(project_folder: str, num_images: int) -> None:
    """
    Update NSFW prompt files with the number of images.

    Args:
        project_folder: Base project folder path
        num_images: Number of images to insert into prompts
    """
    prompts_folder = Path(project_folder) / "Prompts"

    if not prompts_folder.exists():
        print(f"Warning: Prompts folder not found: {prompts_folder}")
        return

    # Update fanvue.txt
    _update_prompt_file(prompts_folder / "fanvue.txt", num_images)

    # Update socialmedia.txt with Fanvue count
    _update_socialmedia_file(prompts_folder / "socialmedia.txt", num_images, "Fanvue")


def main():
    """Main function to process images based on config file."""
    if len(sys.argv) != 2:
        print("Usage: python add_text_to_image.py <config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_config(config_path)

    # Get project folder base path
    project_folder = config.get("project_folder", "")
    if not project_folder:
        print("Error: 'project_folder' not specified in config")
        sys.exit(1)

    # Process SFW image
    if "sfw" in config:
        sfw = config["sfw"]
        print(f"Processing SFW image...")

        # Build full paths
        input_path = str(Path(project_folder) / sfw["input_image"])
        output_path = str(Path(project_folder) / sfw["output_image"])

        num_images = get_number_of_images(project_folder, "SFW")
        add_number_to_prompts_sfw(project_folder, num_images)

        add_text_to_image(
            input_path=input_path,
            output_path=output_path,
            text=sfw["text"],
            font_path=config.get("font_path", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            font_size_percent=sfw.get("font_size_percent", 5),
            color=sfw.get("color", "#FFFFFF"),
            num_images=num_images
        )

    # Process NSFW image
    if "nsfw" in config:
        nsfw = config["nsfw"]
        print(f"Processing NSFW image...")

        # Build full paths
        input_path = str(Path(project_folder) / nsfw["input_image"])
        output_path = str(Path(project_folder) / nsfw["output_image"])

        num_images = get_number_of_images(project_folder, "NSFW")
        add_number_to_prompts_nsfw(project_folder, num_images)

        add_text_to_image(
            input_path=input_path,
            output_path=output_path,
            text=nsfw["text"],
            font_path=config.get("font_path", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            font_size_percent=nsfw.get("font_size_percent", 5),
            color=nsfw.get("color", "#FFFFFF"),
            blur=nsfw.get("blur", True),
            blur_radius=nsfw.get("blur_radius", 15),
            num_images=num_images
        )

    print("\n✓ All images processed successfully!")

    # Build full output paths
    sfw_output = str(Path(project_folder) / config["sfw"]["output_image"]) if "sfw" in config else None
    nsfw_output = str(Path(project_folder) / config["nsfw"]["output_image"]) if "nsfw" in config else None

    # Get SFW input image for fanvue-api preview
    sfw_input = config["sfw"]["input_image"] if "sfw" in config else None

    # Update telegram-api config.json with output file paths
    try:
        telegram_config_path = "/home/pocahontas/git/apis/telegram-api/config.json"
        with open(telegram_config_path, "r", encoding="utf-8") as f:
            telegram_config = json.load(f)

        # Update the media section
        if sfw_output:
            telegram_config["media"]["sfw_file"] = sfw_output
        if nsfw_output:
            telegram_config["media"]["nsfw_file"] = nsfw_output

        with open(telegram_config_path, "w", encoding="utf-8") as f:
            json.dump(telegram_config, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] Updated telegram-api config with output file paths")
    except Exception as e:
        print(f"[WARNING] Failed to update telegram-api config: {e}")

    # Update x-api config.json with output file paths
    try:
        x_config_path = "/home/pocahontas/git/apis/x-api/config.json"
        with open(x_config_path, "r", encoding="utf-8") as f:
            x_config = json.load(f)

        # Update the media section
        if sfw_output:
            x_config["media"]["sfw_file"] = sfw_output
        if nsfw_output:
            x_config["media"]["nsfw_file"] = nsfw_output

        with open(x_config_path, "w", encoding="utf-8") as f:
            json.dump(x_config, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] Updated x-api config with output file paths")
    except Exception as e:
        print(f"[WARNING] Failed to update x-api config: {e}")

    # Update fanvue-api config.json with SFW input image for preview
    try:
        fanvue_config_path = "/home/pocahontas/git/apis/fanvue-api/config.json"
        with open(fanvue_config_path, "r", encoding="utf-8") as f:
            fanvue_config = json.load(f)

        # Update the post_preview section with SFW input image
        if sfw_input and "post_preview" in fanvue_config:
            fanvue_config["post_preview"]["preview_image"] = sfw_input

        with open(fanvue_config_path, "w", encoding="utf-8") as f:
            json.dump(fanvue_config, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] Updated fanvue-api config with preview image: {sfw_input}")
    except Exception as e:
        print(f"[WARNING] Failed to update fanvue-api config: {e}")


if __name__ == "__main__":
    main()
