"""GalleryLinker plugin for Stash."""

from ..void_common import util
from . import datatypes, gallery_linker
from .gallery_linker import GalleryLinker

__all__ = ["GalleryLinker", "util", "datatypes", "gallery_linker"]
