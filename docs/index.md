# PyPDFFill

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Concept

A helper tool to map fields from a Pydantic model to a PDF form using the great [PyPDFForm](https://chinapandaman.github.io/PyPDFForm/) library.

## Why

Many PDF forms are not very "friendly" to fill out, largely because of weird tab order issues. Also, if any calculations need to be done, they need to be done "offline" and entered manually.

Python is a great tool for creating simple
