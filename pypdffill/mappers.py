"""Module to map a PDF form to a Pydantic model.

This module provides a class to map a PDF form to a Pydantic model. The
`PdfForm` class is used to map the fields of a PDF form to a Pydantic
model. The class can be used to generate a Pydantic model from the fields of a
PDF form and to generate a filled PDF form from a Pydantic model."""

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, create_model, field_validator
from PyPDFForm import PdfWrapper

_VALID_TYPES = Literal["text", "checkbox", "radio", "dropdown", "signature"]


def any_to_str(value: str | float | None) -> str:
    if value is None:
        return ""
    return str(value)


class FieldMapper(BaseModel):
    """A class to map a field in a PDF form to a Pydantic model.

    Example:

    ```python
    from pypdffill.mappers import FieldMapper

    field = FieldMapper(
        field_name="first_name",
        widget_type="text",
        widget_name="f1_1[0]",
    )
    ```
    """

    field_name: str = Field(description="The name of the field in the Pydantic model.")
    widget_type: _VALID_TYPES = Field(default="text", description="The type of widget.")
    max_length: int | None = Field(
        default=None, description="The maximum length of the field."
    )
    widget_name: str = Field(description="The name of the field in the PDF form.")
    default_value: str | bool | None = Field(
        default=None, description="The default value of the field."
    )

    def get_field(self):
        match self.widget_type:
            case "text":
                if self.max_length is not None:
                    return (
                        str,
                        Field(
                            alias=AliasChoices(self.field_name, self.widget_name),
                            serialization_alias=self.widget_name,
                            max_length=self.max_length,
                            default=self.default_value,
                        ),
                    )
                return (
                    str,
                    Field(
                        alias=AliasChoices(self.field_name, self.widget_name),
                        serialization_alias=self.widget_name,
                        default=self.default_value,
                    ),
                )
            case "checkbox":
                if isinstance(self.default_value, str):
                    msg = "Checkbox default value must be a boolean."
                    raise TypeError(msg)
                return (
                    bool,
                    Field(
                        alias=AliasChoices(self.field_name, self.widget_name),
                        serialization_alias=self.widget_name,
                        default=self.default_value,
                    ),
                )
            case _:
                msg = f"Widget type {self.widget_type} not implemented."
                raise NotImplementedError(msg)


class PdfForm(BaseModel):
    """A class to map a PDF form to a Pydantic model.

    Example:

    ```python
    from pypdffill.mappers import FieldMapper, PdfForm

    form = PdfForm(
        name="Form8962",
        fields=[
            FieldMapper(
                field_name="name",
                widget_type="text",
                widget_name="f1_1[0]",
            ),
            FieldMapper(
                field_name="ssn",
                widget_type="text",
                widget_name="f1_2[0]",
            ),
            FieldMapper(
                field_name="exceptions",
                widget_type="checkbox",
                widget_name="c1_1[0]",
            ),
            FieldMapper(
                field_name="tax_family_size",
                widget_type="text",
                widget_name="f1_3[0]",
            ),
            FieldMapper(
                field_name="modified_agi",
                widget_type="text",
                widget_name="f1_4[0]",
            ),
        ],
        blank_pdf_path="tests/samples/f8962.pdf",
    )
    ```
    """

    name: str
    fields: list[FieldMapper]
    blank_pdf_path: Path

    _form_model: type[BaseModel] | None = None

    @field_validator("blank_pdf_path", mode="before")
    @classmethod
    def str_to_path(cls, value: str | Path) -> Path:
        if isinstance(value, str):
            return Path(value)
        return value

    def generate_model(self) -> type[BaseModel]:
        if self._form_model is None:
            fields = {field.field_name: field.get_field() for field in self.fields}

            validators = {
                f"{field.field_name}_to_str": field_validator(
                    field.field_name, mode="before"
                )(any_to_str)
                for field in self.fields
                if field.widget_type == "text"
            }

            self._form_model = create_model(
                self.name, __validators__=validators, **fields
            )

        return self._form_model

    @property
    def form(self):
        """The Pydantic model generated from the PDF form used to populate the PDF."""
        if self._form_model is None:
            self._form_model = self.generate_model()
        return self._form_model

    def generate_pdf(self, form: BaseModel, output_path: str | Path):
        """Generates a filled PDF form.

        Args:
            form (BaseModel): The Pydantic model used to populate the PDF.
            output_path (str | Path): The path to the output file.
        """
        if isinstance(output_path, str):
            output_path = Path(output_path)

        pdf_form = PdfWrapper(str(self.blank_pdf_path))

        filled = pdf_form.fill(form.model_dump(by_alias=True))

        with output_path.open("wb+") as output:
            output.write(filled.read())

    def model_validate(self, obj, **kwargs):
        return self.form.model_validate(obj, **kwargs)
