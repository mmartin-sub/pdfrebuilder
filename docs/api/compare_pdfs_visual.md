# compare_pdfs_visual

## Functions

### compare_pdfs_visual(original_path, generated_path, diff_image_base_path, visual_diff_threshold)

Compare two documents visually using the advanced visual validation system.

Args:
    original_path: Path to the original document
    generated_path: Path to the generated document
    diff_image_base_path: Base path for saving difference images
    visual_diff_threshold: Optional threshold for visual difference detection
                          (if None, use the value from CONFIG)

Returns:
    int: Error code indicating the result of the comparison
