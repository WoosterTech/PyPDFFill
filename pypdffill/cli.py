from pathlib import Path
from typing import Annotated

import typer

from pypdffill.pdfform import generate_preview


def main(
    input_file: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, readable=True)
    ],
    output_file: Annotated[Path, typer.Argument(dir_okay=False, writable=True)],
):
    generate_preview(input_file, output_file)


if __name__ == "__main__":
    typer.run(main)
