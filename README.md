# barebones_image_sorter

## Usage (Windows)

1. Put `ImageSorter.exe` in a folder where you want the sorted images stored.
3. Run `ImageSorter.exe`. It creates the `unsorted_images`, `positive_images`, `negative_images`, and `uncertain_images` folders automatically. Exit the program when prompted.
2. Place the images to be sorted in the `unsorted_images` folder. Supported formats: JPG, JPEG, PNG, BMP, WEBP, and GIF.
4. Run `ImageSorter.exe` again. Sort the displayed image with the arrow keys: Left for Negative, Right for Positive, and Down for Uncertain. Scroll the mouse wheel to zoom in or out. Press Escape to quit.

Each sorted image is moved from `unsorted_images` into its selected folder. Please note that there is currently no 'undo' button; if you accidentally sort an image into the wrong folder, you will need to manually return it to `unsorted_images`. 

The executable needs write access to its folder.