from typing import List
from PIL import Image
import numpy
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("clip-ViT-B-32")


def calculate_duplicates(images, threshold: int = 0.90):
    encoded_images = model.encode(
        images,
        show_progress_bar=True,
        convert_to_tensor=True,
    )
    processed_images = util.paraphrase_mining_embeddings(encoded_images)
    return [image for image in processed_images if image[0] >= threshold]
