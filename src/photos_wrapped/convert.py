import osxphotos
from PIL import Image

from pillow_heif import register_heif_opener

register_heif_opener()


def convert_to_jpeg(photo: osxphotos.PhotoInfo, asset_dir: str) -> str:
    if photo.adjustments:
        [filename] = photo.export(asset_dir, overwrite=True, edited=True)
        if not filename:
            [filename] = photo.export(
                asset_dir, overwrite=True, edited=True, use_photos_export=True
            )
    else:
        [filename] = photo.export(asset_dir, overwrite=True)
        if not filename:
            [filename] = photo.export(
                asset_dir, overwrite=True, edited=True, use_photos_export=True
            )
    if filename.lower().endswith("heic"):
        heic_file = Image.open(filename)
        jpeg_filename = filename.lower().replace(".heic", ".jpeg")
        heic_file.save(jpeg_filename)
        return jpeg_filename
    return filename
