import osxphotos
import os
import json
from photos_wrapped.photo_similarity import dhash, phash
from PIL import Image
from glob import glob
import pillow_avif
from pillow_heif import register_heif_opener

register_heif_opener()

photosdb = osxphotos.PhotosDB()

query = osxphotos.QueryOptions(photos=True, movies=True, year=[2023])
photos = photosdb.query(query)

from sentence_transformers import SentenceTransformer, util
from PIL import Image
import glob
import os

# Load the OpenAI CLIP Model
print("Loading CLIP Model...")
model = SentenceTransformer("clip-ViT-B-32")
