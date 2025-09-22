"""GalleryLinker plugin for Stash."""

from . import datatypes, gallery_linker, util
from .gallery_linker import GalleryLinker

__all__ = ["GalleryLinker", "util", "datatypes", "gallery_linker"]
