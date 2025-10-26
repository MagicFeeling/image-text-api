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
    font_size: int,
    color: str,
    position: str = "bottom",
    blur: bool = False,
    blur_radius: int = 15
) -> None:
    """
    Add text to an image and save to a new file.

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        text: Text to add to image
        font_path: Path to TrueType font file
        font_size: Font size in points
        color: Color as hex string (e.g., "#FFFFFF") or RGB tuple
        position: Text position ("bottom", "top", or "center")
        blur: Whether to blur the image before adding text
        blur_radius: Blur radius (higher = more blur)
    """
    try:
        # Open the image
        img = Image.open(input_path)

        # Apply blur if requested
        if blur:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

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

        # Get image dimensions
        img_width, img_height = img.size

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        x = (img_width - text_width) // 2  # Center horizontally

        if position == "bottom":
            # Position in lower part of image with padding
            y = img_height - text_height - (img_height // 10)
        elif position == "top":
            y = img_height // 10
        else:  # center
            y = (img_height - text_height) // 2

        # Draw text with outline for better visibility
        outline_color = (0, 0, 0) if sum(rgb_color) > 384 else (255, 255, 255)

        # Draw outline
        for adj_x in range(-2, 3):
            for adj_y in range(-2, 3):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=rgb_color)

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

        add_text_to_image(
            input_path=input_path,
            output_path=output_path,
            text=sfw["text"],
            font_path=config.get("font_path", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            font_size=sfw.get("font_size", 48),
            color=sfw.get("color", "#FFFFFF"),
            position=sfw.get("position", "bottom")
        )

    # Process NSFW image
    if "nsfw" in config:
        nsfw = config["nsfw"]
        print(f"Processing NSFW image...")

        # Build full paths
        input_path = str(Path(project_folder) / nsfw["input_image"])
        output_path = str(Path(project_folder) / nsfw["output_image"])

        add_text_to_image(
            input_path=input_path,
            output_path=output_path,
            text=nsfw["text"],
            font_path=config.get("font_path", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            font_size=nsfw.get("font_size", 48),
            color=nsfw.get("color", "#FFFFFF"),
            position=nsfw.get("position", "bottom"),
            blur=nsfw.get("blur", True),
            blur_radius=nsfw.get("blur_radius", 15)
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
