"""Data layer: resolves product / query image files on disk."""
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class ImageStorage:

    def __init__(self, root=DATA_DIR):
        self.root = root

    def path(self, relative):
        return relative if os.path.isabs(relative) else os.path.join(self.root, relative)

    def exists(self, relative):
        return os.path.isfile(self.path(relative))
