from pydantic import BaseModel, Field, Secret, computed_field, field_validator

from pypdffill.mappers import FieldMapper, PdfForm


def number_to_int(value: float | None) -> int | None:
    """Validator for fields that require an int but can be passed as a float."""
    if value is None:
        return None
    return int(value)


class SSN(Secret[str]):
    def _display(self) -> str:
        return "***-**-****"


class Person(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    ssn: SSN

    @property
    def first_last(self):
        return f"{self.first_name} {self.last_name}"


class Form8962(BaseModel):
    name: str
    ssn: str = Field(pattern=r"^\d{3}-?\d{2}-?\d{4}$")
    tax_family_size: int
    modified_agi: int
    dependents_modified_agi_total: int | None = None
    exceptions: bool = False

    @computed_field  # type: ignore[misc]
    @property
    def household_income(self) -> int:
        return self.modified_agi + (self.dependents_modified_agi_total or 0)

    _agi_to_int = field_validator("modified_agi", mode="before")(number_to_int)
    _dependents_modified_agi_total_to_int = field_validator(
        "dependents_modified_agi_total", mode="before"
    )(number_to_int)


Form8962PDF = PdfForm(
    name="Form8962",
    fields=[
        FieldMapper(field_name="name", widget_type="text", widget_name="f1_1[0]"),
        FieldMapper(field_name="ssn", widget_type="text", widget_name="f1_2[0]"),
        FieldMapper(
            field_name="exceptions", widget_type="checkbox", widget_name="c1_1[0]"
        ),
        FieldMapper(
            field_name="tax_family_size", widget_type="text", widget_name="f1_3[0]"
        ),
        FieldMapper(
            field_name="modified_agi", widget_type="text", widget_name="f1_4[0]"
        ),
    ],
    blank_pdf_path="tests/samples/f8962.pdf",
)


if __name__ == "__main__":
    my_form = Form8962(
        name="John Smith",
        ssn="123-45-6789",
        tax_family_size=3,
        modified_agi=12345.67,
        exceptions=True,
    )

    filled_form_model = Form8962PDF.model_validate(my_form.model_dump())

    Form8962PDF.generate_pdf(
        form=filled_form_model, output_path="tests/samples/f8962_filled.pdf"
    )
