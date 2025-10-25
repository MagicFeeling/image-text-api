# Image Text Overlay Tool

A simple Python tool to add text overlays to images. Perfect for adding watermarks, captions, or promotional text to SFW and NSFW content.

## Features

- Add text to multiple images (SFW/NSFW) in one run
- Configurable font, size, color, and position
- Automatic text outline for better visibility
- Original images are preserved
- Output files saved with custom names

## Requirements

- Python 3.7+
- Pillow (PIL)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Copy `config.json.example` to `config.json`:
```bash
cp config.json.example config.json
```

2. Edit `config.json` with your settings:

```json
{
  "font_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
  "sfw": {
    "input_image": "/path/to/original.png",
    "output_image": "/path/to/output.png",
    "text": "Your text here",
    "font_size": 48,
    "color": "#FFFFFF",
    "position": "bottom"
  },
  "nsfw": {
    "input_image": "/path/to/original.png",
    "output_image": "/path/to/output.png",
    "text": "Your text here",
    "font_size": 48,
    "color": "#FF69B4",
    "position": "bottom"
  }
}
```

3. Run the script:
```bash
python add_text_to_image.py config.json
```

## Configuration Options

### Global Settings

- `font_path`: Path to TrueType font file (default: DejaVuSans-Bold)

### Image Settings (sfw/nsfw)

- `input_image`: Path to original image (required)
- `output_image`: Path for output image (required)
- `text`: Text to add to image (required)
- `font_size`: Font size in points (default: 48)
- `color`: Text color as hex code (e.g., "#FFFFFF" for white)
- `position`: Text position - "bottom", "top", or "center" (default: "bottom")

## Color Examples

- White: `#FFFFFF`
- Black: `#000000`
- Pink: `#FF69B4`
- Red: `#FF0000`
- Blue: `#0000FF`
- Gold: `#FFD700`

## Notes

- Text is automatically centered horizontally
- An outline is added automatically for better visibility
- Output directories are created automatically if they don't exist
- You can process just SFW, just NSFW, or both in one run
- Original images are never modified

## Example

```bash
# Process both SFW and NSFW images
python add_text_to_image.py config.json

# Expected output:
# Processing SFW image...
# ✓ Created: /path/to/sfw_output.png
# Processing NSFW image...
# ✓ Created: /path/to/nsfw_output.png
#
# ✓ All images processed successfully!
```

## Troubleshooting

**Font not found?**
- Use a system font path, or specify a custom `.ttf` font file
- Common Linux font paths:
  - `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`
  - `/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf`

**Image not found?**
- Check that input image paths are correct and absolute
- Ensure you have read permissions for input files

**Permission denied when saving?**
- Ensure you have write permissions for the output directory
