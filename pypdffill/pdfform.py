from pathlib import Path

from PyPDFForm import PdfWrapper


def generate_preview(input_file: Path | str, output_file: Path):
    """Generates a preview of the PDF form.

    Args:
        input_file (Path | str): The path to the PDF file.
        output_file (Path): The path to the output file.
    """
    if isinstance(input_file, Path):
        input_file = str(input_file)

    wrapper = PdfWrapper(input_file)

    preview_stream = wrapper.preview

    with output_file.open("wb+") as output:
        output.write(preview_stream)


def generate_schema(input_file: Path | str):
    """Generates a schema of the PDF form.

    Args:
        input_file (Path | str): The path to the PDF file.

    Returns:
        dict: The schema of the PDF form.
    """
    if isinstance(input_file, Path):
        input_file = str(input_file)

    wrapper = PdfWrapper(input_file)

    return wrapper.schema


if __name__ == "__main__":
    from rich.pretty import pprint

    input_file = Path("tests/samples/f8962.pdf")

    json_schema = generate_schema(input_file)

    pprint(json_schema)
