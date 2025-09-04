import os
import shutil
import random

# --- CONFIGURATION ---
# 1. UPDATE these two lines with the names of your two source photos.
#    Make sure these photos are in the same directory as this script.
SOURCE_IMAGE_1 = "photo1.jpg"  # Replace with your first image file
SOURCE_IMAGE_2 = "photo2.jpg"  # Replace with your second image file

# 2. SET the number of defect pairs you want to generate.
#    500 pairs will create 1000 total image files.
NUMBER_OF_PAIRS = 500

# 3. DEFINE the output folder.
OUTPUT_FOLDER = "images"

# --- SCRIPT LOGIC (No changes needed below) ---

def generate_images():
    """
    Creates multiple copies of two source images with unique names
    based on a coordinate-based naming convention.
    """
    print("Starting test image generation...")

    # Check if the source images exist before starting
    if not os.path.exists(SOURCE_IMAGE_1) or not os.path.exists(SOURCE_IMAGE_2):
        print("\n--- ERROR ---")
        print(f"Source images not found! Please make sure '{SOURCE_IMAGE_1}' and '{SOURCE_IMAGE_2}' are in the same folder as this script.")
        print("Aborting.")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: '{OUTPUT_FOLDER}'")

    # Keep track of coordinates to ensure they are unique
    used_coords = set()
    files_created = 0

    while files_created < NUMBER_OF_PAIRS:
        # Generate random coordinates (e.g., from 0 to 50)
        x = random.randint(0, 50)
        y = random.randint(0, 50)

        # Ensure we haven't used this coordinate pair before
        if (x, y) in used_coords:
            continue
        
        used_coords.add((x, y))

        # Create the new filenames based on our pattern
        new_filename_1 = f"defect_{x}_{y}_m1.jpg"
        new_filename_2 = f"defect_{x}_{y}_m2.jpg"

        # Define the full path for the new files
        dest_path_1 = os.path.join(OUTPUT_FOLDER, new_filename_1)
        dest_path_2 = os.path.join(OUTPUT_FOLDER, new_filename_2)

        # Copy the source images to the destination with the new names
        shutil.copy(SOURCE_IMAGE_1, dest_path_1)
        shutil.copy(SOURCE_IMAGE_2, dest_path_2)

        files_created += 1

        # Print progress to the console
        if files_created % 50 == 0:
            print(f"  ...created {files_created * 2} images so far.")

    print("\n--- SUCCESS ---")
    print(f"Successfully created {files_created * 2} test images in the '{OUTPUT_FOLDER}' folder.")

# Run the function
if __name__ == "__main__":
    generate_images()
