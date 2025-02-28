import pytest
from skimage import color
import colorspacious as cs
from load_parties import color_palette

def hex_to_rgb(hex_color):
    """Convert a hex color string to an RGB list."""
    hex_color = hex_color.lstrip('#')  # Remove the '#' character
    return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]  # Convert hex to RGB as a list

def color_distance(color1, color2):
    """Calculate the perceptual distance between two colors using Delta E."""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    # Print RGB values for debugging
    print(f"RGB1: {rgb1}, RGB2: {rgb2}")

    # Normalize RGB values to the range [0, 1]
    rgb1_normalized = [x / 255.0 for x in rgb1]
    rgb2_normalized = [x / 255.0 for x in rgb2]

    # Convert RGB to LAB using skimage
    lab1 = color.rgb2lab([[rgb1_normalized]])[0][0]  # Convert to LAB
    lab2 = color.rgb2lab([[rgb2_normalized]])[0][0]  # Convert to LAB

    # Print LAB values for debugging
    print(f"LAB1: {lab1}, LAB2: {lab2}")

    # Calculate Delta E using colorspacious
    delta_e = cs.deltaE(lab1, lab2)
    print(f"Delta E: {delta_e}")  # Print Delta E value for debugging
    return delta_e

def test_color_palette_distances():
    # Check that all colors in the palette are distinct
    for i in range(len(color_palette)):
        for j in range(i + 1, len(color_palette)):
            dist = color_distance(color_palette[i], color_palette[j])
            print(f"Distance between {color_palette[i]} and {color_palette[j]}: {dist}")
            assert dist > 2, f"Colors {color_palette[i]} and {color_palette[j]} are not distinct enough."

# Run the test
if __name__ == "__main__":
    pytest.main()
