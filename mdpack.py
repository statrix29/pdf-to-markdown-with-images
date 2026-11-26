#!/usr/bin/env python3
"""Rename generated local figures and optionally bundle a conversion."""

import argparse
from html import unescape
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import quote, unquote, urlsplit
import zipfile

IMAGES = re.compile(
    r"!\[[^\]\n]*\]\((?:<(?P<angled>[^>\n]+)>|(?P<markdown>[^)\s]+))[^)\n]*\)"
    r"|<img\b[^>]*?\bsrc=[\"'](?P<html>[^\"']+)[\"'][^>]*>",
    re.IGNORECASE,
)
IMAGE_EXTENSIONS = {
    ".avif", ".bmp", ".gif", ".heic", ".jpeg", ".jpg", ".png",
    ".svg", ".tif", ".tiff", ".webp",
}


def generated_image(markdown, reference):
    url = urlsplit(unescape(reference))
    if url.scheme or url.netloc or url.query or url.fragment:
        return None
    relative = Path(unquote(url.path))
    allowed = {f"{markdown.stem}_{suffix}" for suffix in ("artifacts", "media", "figs")}
    if (
        len(relative.parts) < 2
        or relative.parts[0] not in allowed
        or ".." in relative.parts
        or relative.suffix.lower() not in IMAGE_EXTENSIONS
    ):
        return None
    candidate = markdown.parent / relative
    if candidate.resolve() != candidate or not candidate.is_file():
        return None
    return candidate


def pack(markdown, bundle):
    if markdown.is_symlink():
        raise ValueError("choose a Markdown file rather than a symbolic link")
    markdown = markdown.resolve(strict=True)
    text = markdown.read_text(encoding="utf-8")
    figures = markdown.with_name(f"{markdown.stem}_figs")
    if figures.is_symlink():
        raise ValueError("figure directory is a symbolic link")

    matches = {}
    sources = {}
    for match in IMAGES.finditer(text):
        reference = next(value for value in match.groups() if value is not None)
        source = generated_image(markdown, reference)
        if source is not None:
            sources.setdefault(source, len(sources) + 1)
            matches[match.start()] = source

    with tempfile.TemporaryDirectory(prefix=".mdpack-", dir=markdown.parent) as directory:
        work = Path(directory)
        image_paths = {}
        width = max(2, len(str(len(sources))))
        for source, number in sources.items():
            filename = f"fig-{number:0{width}d}{source.suffix.lower()}"
            staged = work / filename
            shutil.copyfile(source, staged)
            image_paths[source] = (staged, figures / filename)

        def substitute(match):
            source = matches.get(match.start())
            if source is None:
                return match.group()
            _, target = image_paths[source]
            relative = quote(target.relative_to(markdown.parent).as_posix(), safe="/")
            return f"![Figure {sources[source]} ({target.name})]({relative})"

        rendered = IMAGES.sub(substitute, text)
        staged_markdown = work / markdown.name
        staged_markdown.write_text(rendered, encoding="utf-8")

        if bundle:
            archive = markdown.with_name(f"{markdown.stem}_for_ai.zip")
            staged_archive = work / archive.name
            with zipfile.ZipFile(staged_archive, "w", zipfile.ZIP_DEFLATED) as output:
                output.write(staged_markdown, markdown.name)
                for staged, target in image_paths.values():
                    output.write(staged, target.relative_to(markdown.parent).as_posix())

        if image_paths:
            figures.mkdir(exist_ok=True)
            for staged, target in image_paths.values():
                os.replace(staged, target)
        os.replace(staged_markdown, markdown)
        if bundle:
            os.replace(staged_archive, archive)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--bundle", action="store_true")
    args = parser.parse_args()
    try:
        pack(args.markdown, args.bundle)
    except (OSError, ValueError) as error:
        parser.exit(1, f"mdpack: {error}\n")
