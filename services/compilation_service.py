from typing import List

from flask import abort

from repositories import compilation_repository, user_repository, Album, YTCompilation
from . import default_page_size, check_uuid


def prepare_albums_list(albums: List[Album]):
    for album in albums:
        album.album_id = album.id
        album.title = album.album_name
    return albums


def prepare_compilations_list(compilations: List[YTCompilation]):
    for compilation in compilations:
        compilation.compilation_id = compilation.id
    return compilations


def get_albums(page: int):
    return {"albums": prepare_albums_list(
        compilation_repository.get_albums(page, default_page_size)
    )}


def add_album(user_id: str, author: str, album_name: str, picture: str, link: str, **kwargs) -> Album:
    user = user_repository.get_user_by_id(user_id)
    if not user or not (user.admin or user.change_compilations):
        abort(403, "You don't have a permission to add albums")
    album = Album()
    album.author = author
    album.album_name = album_name
    album.picture = picture
    album.link = link
    return compilation_repository.add_album(album)


def delete_album(user_id: str, album_id: str) -> None:
    check_uuid(album_id)
    user = user_repository.get_user_by_id(user_id)
    if not user or not (user.admin or user.change_compilations):
        abort(403, "You don't have a permission to remove albums")
    return compilation_repository.delete_album_by_id(album_id)


def search_albums(page: int, text_to_search: str):
    return {"albums": prepare_albums_list(
        compilation_repository.search_albums(text_to_search, page, default_page_size)
    )}


def get_compilations(page: int):
    return {"compilations": prepare_compilations_list(
        compilation_repository.get_compilations(page, default_page_size)
    )}


def search_compilations(page: int, text_to_search: str):
    return {"compilations": prepare_compilations_list(
        compilation_repository.search_compilations(text_to_search, page, default_page_size)
    )}


def add_compilation(user_id: str, channel: str, video_name: str, link: str, **kwargs) -> YTCompilation:
    user = user_repository.get_user_by_id(user_id)
    if not user or not (user.admin or user.change_compilations):
        abort(403, "You don't have a permission to add compilations")
    compilation = YTCompilation()
    compilation.channel = channel
    compilation.video_name = video_name
    compilation.link = link
    return compilation_repository.add_compilation(compilation)


def delete_compilation(user_id: str, compilation_id: str) -> None:
    check_uuid(compilation_id)
    user = user_repository.get_user_by_id(user_id)
    if not user or not (user.admin or user.change_compilations):
        abort(403, "You don't have a permission to remove compilations")
    return compilation_repository.delete_compilation_by_id(compilation_id)
