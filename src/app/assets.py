from pathlib import Path
from PIL import Image
from PIL.ImageTk import PhotoImage

_images = []

def load(path: Path, name: str):
    """Load an image to the tcl interpreter with `name`.

    :param Path path: The image to load.
    :param str name: The name.
    :raises FileNotFoundError: If the image file does not exist.
    """
    _images.append(PhotoImage(Image.open(path), name=name))