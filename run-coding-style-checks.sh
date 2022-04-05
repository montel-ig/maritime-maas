#!/bin/bash

black --check .
flake8
isort . -c