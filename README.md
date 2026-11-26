# PDF to Markdown with Images

Convert a PDF into Markdown and keep its figures next to the text. The `tomd` functions run locally in zsh. Docling handles PDF layout, figure extraction, and Apple Vision OCR. The first PDF conversion may download Docling’s models.

## Quickstart on macOS

Use macOS with zsh, Python 3, and [uv](https://docs.astral.sh/uv/getting-started/installation/). The PDF setup below uses the Docling version tested with the sample.

```sh
uv tool install --python 3.12 --with ocrmac "docling==2.151.1"
uv tool update-shell
```

Open a new terminal so `docling` is on PATH, then clone and source the script.

```sh
git clone https://github.com/statrix29/pdf-to-markdown-with-images.git
cd pdf-to-markdown-with-images
source ./tomd.sh
tomd examples/sample.pdf converted
```

The synthetic [sample PDF](examples/sample.pdf) has one figure. The command writes `converted/sample.md` and a `converted/sample_artifacts/` folder. Move both together so the relative image link keeps working. See the [example conversion](examples/sample.md).

## Bundle the figures

```sh
tomd-pack examples/sample.pdf packed
```

The bundle contains `sample.md` and the generated figures in `sample_figs/`, named `fig-01.png` and so on. It is saved as `packed/sample_for_ai.zip`. Use a fresh output folder for a repeat conversion. The commands stop if the destination already contains a matching output.

## Other document formats

| Input | Backend | Installation |
| --- | --- | --- |
| PDF, PowerPoint, and images | [Docling](https://github.com/docling-project/docling) | See the quickstart |
| Word, HTML, Markdown, and other supported text documents | [Pandoc](https://pandoc.org/) | `brew install pandoc` |
| Spreadsheets and other supported formats | [MarkItDown](https://github.com/microsoft/markitdown) | `uv tool install --python 3.12 "markitdown[all]==0.1.9"` |

Use `tomd-fast file.pdf output` when you only need text and tables. It uses MarkItDown and skips image extraction. Source `tomd.sh` in each zsh session where you want the commands available, or add a source line using the absolute path to the cloned script to your `.zshrc`.

## License

The wrapper code is source-available under the [PolyForm Strict License 1.0.0](LICENSE). Docling, its models, Pandoc, and MarkItDown retain their own terms. For a commercial license, open a [licensing inquiry](https://github.com/statrix29/pdf-to-markdown-with-images/issues/new?title=Commercial%20licensing%20inquiry).
