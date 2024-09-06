from pathlib import Path

import pytest

from pypdffill.mappers import FieldMapper, PdfForm
from tests.models import Form8962


@pytest.fixture()
def sample_fill():
    return Form8962(
        name="John Doe",
        ssn="123-45-6789",
        tax_family_size=4,
        modified_agi=10000.78,
        dependents_modified_agi_total=None,
        exceptions=True,
    )


@pytest.fixture()
def mapper():
    return PdfForm(
        name="TestForm",
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
            FieldMapper(
                field_name="dependents_modified_agi_total",
                widget_type="text",
                widget_name="f1_5[0]",
            ),
            FieldMapper(
                field_name="household_income", widget_type="text", widget_name="f1_6[0]"
            ),
        ],
        blank_pdf_path="tests/samples/f8962.pdf",
    )


def test_pdf_fill(sample_fill: Form8962, mapper: PdfForm, tmp_path: Path):
    filled_form_model = mapper.model_validate(sample_fill.model_dump())

    mapper.generate_pdf(
        form=filled_form_model, output_path=tmp_path / "filled_form.pdf"
    )

    assert (tmp_path / "filled_form.pdf").exists()
