import os
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def add_footer_and_logo(image_path):
    """Add the DSE logo and license footer to a saved PNG file.
    Ensures the image is exactly 1920x1080 pixels.
    """
    try:
        # Read the main image and logos
        main_img = plt.imread(image_path)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo = plt.imread(os.path.join(script_dir, 'dse.png'))
        cc_img = plt.imread(os.path.join(script_dir, 'cc.png'))
        ccby_img = plt.imread(os.path.join(script_dir, 'ccby.png'))
        
        # First resize the main image to exactly 1920x1080
        from PIL import Image
        import numpy as np
        
        # Convert to PIL Image for resizing
        if isinstance(main_img, np.ndarray):
            main_img = Image.fromarray((main_img * 255).astype(np.uint8) if main_img.dtype == np.float32 else main_img)
        else:
            main_img = Image.open(image_path)
            
        # Resize to exactly 1920x1080 with proper aspect ratio
        target_width = 1920
        target_height = 1080
        
        # Calculate dimensions preserving aspect ratio
        aspect = main_img.width / main_img.height
        target_aspect = target_width / target_height
        
        if aspect > target_aspect:  # Image is wider than 16:9
            new_width = target_width
            new_height = int(target_width / aspect)
        else:  # Image is taller than 16:9
            new_height = target_height
            new_width = int(target_height * aspect)
            
        # Resize maintaining aspect ratio
        main_img = main_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new 16:9 canvas
        canvas = Image.new('RGB', (target_width, target_height), 'white')
        
        # Paste resized image in center
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        canvas.paste(main_img, (x, y))
        
        # Convert back to numpy array
        main_img = np.array(canvas)
        
        # Create figure with exact pixel dimensions
        dpi = 100
        fig = plt.figure(figsize=(target_width/dpi, target_height/dpi), dpi=dpi)
        
        # Main plot for the visualization (90% height)
        main_ax = plt.axes([0, 0.1, 1, 0.9])
        main_ax.imshow(main_img)
        main_ax.axis('off')
        
        # Add DSE logo in top-left corner
        logo_height = 0.05  # Relative to figure height
        logo_box = OffsetImage(logo, zoom=logo_height)
        logo_anno = AnnotationBbox(logo_box, (-0.02, 0.99),  # Moved much further left
                                 xycoords='axes fraction',
                                 box_alignment=(0, 1),
                                 bboxprops=dict(alpha=0.0))
        main_ax.add_artist(logo_anno)
        
        # Footer with license info (10% height)
        footer_ax = plt.axes([0, 0, 1, 0.1])
        footer_ax.axis('off')
        
        # Add CC icons
        icon_height = 0.0075  # Relative to figure height
        cc_box = OffsetImage(cc_img, zoom=icon_height)
        ccby_box = OffsetImage(ccby_img, zoom=icon_height)
        
        # Position icons and text
        cc_anno = AnnotationBbox(cc_box, (0.02, 0.5),
                               xycoords='axes fraction',
                               box_alignment=(0, 0.5),
                               bboxprops=dict(alpha=0.0))
        ccby_anno = AnnotationBbox(ccby_box, (0.035, 0.5),
                                 xycoords='axes fraction',
                                 box_alignment=(0, 0.5),
                                 bboxprops=dict(alpha=0.0))
        footer_ax.add_artist(cc_anno)
        footer_ax.add_artist(ccby_anno)
        
        # Add license text
        footer_ax.text(0.055, 0.5,
                      'CC BY TVLuke; tvluke.de. Sourcecode at https://github.com/TVLuke/Democracy-Exchange',
                      va='center', ha='left',
                      fontsize=10)
        
        # Save with exact dimensions
        plt.savefig(image_path, dpi=dpi, bbox_inches=None, pad_inches=0)
        plt.close()
        
        # Verify and force exact dimensions
        img = Image.open(image_path)
        if img.size != (target_width, target_height):
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            img.save(image_path)
        
    except Exception as e:
        print(f"Error adding footer to {image_path}: {str(e)}")
        # Keep the original file if there's an error
