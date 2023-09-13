import os
import random
import numpy as np
from struct import pack
from multiprocessing import Pool

# Configuration Parameters
output_directory = "webp_test_cases"
num_test_cases = 850000
image_size_range = (0, 50000)
chunk_size_range = (0, 50000)

def generate_random_webp_file(test_case_number):
    # Generate random pixel data (100 bytes) using NumPy
    pixel_data = np.random.randint(0, 256, size=100, dtype=np.uint8).tobytes()

    # Generate random width and height
    width = random.randint(*image_size_range)
    height = random.randint(*image_size_range)

    # Create a minimal WebP header
    webp_header = b'RIFF' + pack('<I', len(pixel_data) + 30) + b'WEBP'

    # Create VP8, VP8L, or VP8X chunk with random options (including lossless)
    compression_type = random.choice([b'VP8 ', b'VP8L', b'VP8X'])
    if compression_type == b'VP8X':
        # For VP8X, include optional lossless flag
        lossless = random.choice([True, False])
        chunk_data = compression_type + pack('<I', width) + pack('<I', height) + bytes([lossless]) + pixel_data
    else:
        chunk_data = compression_type + pack('<I', width) + pack('<I', height) + pixel_data

    # Add metadata chunks with random data (for testing)
    num_metadata_chunks = random.randint(0, 5)  # Random number of metadata chunks
    metadata_chunks = []
    for _ in range(num_metadata_chunks):
        chunk_size = random.randint(*chunk_size_range)  # Random chunk size
        metadata_chunk = b'METADATA' + pack('<I', chunk_size)
        metadata_chunk += bytes([random.randint(0, 255) for _ in range(chunk_size - 8)])
        metadata_chunks.append(metadata_chunk)

    # Introduce variations in chunk order (e.g., metadata before or after)
    random.shuffle(metadata_chunks)

    # Create a new list to store modified metadata chunks
    modified_metadata_chunks = []

    # Iterate over metadata_chunks and perform modifications
    for metadata_chunk in metadata_chunks:
        # 2. Random padding within chunks
        padding = bytes([random.randint(0, 255) for _ in range(10)])  # Random padding
        metadata_chunk += padding

        # 3. Variations in chunk size fields
        chunk_size = random.randint(1, 100)  # Random chunk size
        metadata_chunk = b'METADATA' + pack('<I', chunk_size) + metadata_chunk[12:]

        # 4. Invalid data within chunks
        chunk_size = len(metadata_chunk) - 8
        metadata_chunk = metadata_chunk[:12] + bytes([random.randint(0, 255) for _ in range(chunk_size - 4)])

        modified_metadata_chunks.append(metadata_chunk)

    # Replace the original metadata_chunks list with the modified one
    metadata_chunks = modified_metadata_chunks

    # Generate random transparency
    transparent_pixel_data = np.random.randint(0, 256, size=100, dtype=np.uint8).tobytes()

    # Create multiple image data chunks (for animations)
    num_image_data_chunks = random.randint(1, 5)  # Random number of image data chunks
    image_data_chunks = [compression_type + pack('<I', width) + pack('<I', height) + transparent_pixel_data]
    for _ in range(num_image_data_chunks - 1):
        image_data_chunks.append(compression_type + pack('<I', width) + pack('<I', height) + pixel_data)

    # Introduce variations in filter modes (e.g., simple, complex)
    filter_modes = [b'\x00', b'\x01']
    random.shuffle(filter_modes)

    # Include Exif data in metadata chunks
    exif_data = b'EXIF' + pack('<I', len(b'fakeexifdata')) + b'fakeexifdata'
    metadata_chunks.append(exif_data)

    # Add variations:

    # 1. Invalid chunk types
    invalid_chunk_types = [b'INVALID', b'UNKWN', b'???']
    random.shuffle(invalid_chunk_types)
    for chunk_type in invalid_chunk_types:
        invalid_chunk = chunk_type + pack('<I', 10) + b'invaliddata'
        metadata_chunks.append(invalid_chunk)

    # 5. Chunk duplication
    metadata_chunks.extend(metadata_chunks)

    # 6. Random data corruption
    random.shuffle(metadata_chunks)  # Shuffle to ensure random corruption
    metadata_chunk = random.choice(metadata_chunks)
    corruption_position = random.randint(0, len(metadata_chunk) - 1)
    metadata_chunk = metadata_chunk[:corruption_position] + bytes([random.randint(0, 255)]) + metadata_chunk[corruption_position + 1:]
    if metadata_chunk in metadata_chunks:
        metadata_chunks[metadata_chunks.index(metadata_chunk)] = metadata_chunk

    # 7. Random chunk omission
    if num_metadata_chunks > 0:
        omitted_chunk = random.choice(metadata_chunks)
        metadata_chunks.remove(omitted_chunk)

    # 8. Very large number of chunks
    if num_metadata_chunks > 0:
        large_num_chunks = random.randint(num_metadata_chunks, num_metadata_chunks + 100)
        for _ in range(large_num_chunks - num_metadata_chunks):
            chunk_size = random.randint(1, 50)  # Random chunk size
            metadata_chunk = b'METADATA' + pack('<I', chunk_size)
            metadata_chunk += bytes([random.randint(0, 255) for _ in range(chunk_size - 8)])
            metadata_chunks.append(metadata_chunk)

    # Combine header, metadata, filter modes, and image data chunks
    webp_data = webp_header + b''.join(metadata_chunks) + b''.join(filter_modes) + b''.join(image_data_chunks)

    # Create the output file path with a suitable name
    output_file_path = os.path.join(output_directory, f"test_case_{test_case_number}.webp")

    # Write the WebP data to the output file
    with open(output_file_path, 'wb') as f:
        f.write(webp_data)

if __name__ == "__main__":
    output_directory = "webp_test_cases"
    os.makedirs(output_directory, exist_ok=True)

    # Use multiprocessing to parallelize generation
    with Pool() as pool:
        pool.map(generate_random_webp_file, range(num_test_cases))

    print("Test cases generated.")
