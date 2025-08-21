import numpy as np
from skimage.metrics import structural_similarity

# Create two simple grayscale images
im1 = np.zeros((10, 10), dtype=np.uint8)
im1[2:8, 2:8] = 200

im2 = np.zeros((10, 10), dtype=np.uint8)
im2[2:8, 2:8] = 200

# Call structural_similarity with full=True and gradient=False
result = structural_similarity(im1, im2, full=True, gradient=False)

# Print the result and its type to see what is returned
print(f"Result: {result}")
print(f"Type of result: {type(result)}")
if isinstance(result, tuple):
    print(f"Number of elements in tuple: {len(result)}")
