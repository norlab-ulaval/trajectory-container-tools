#!/bin/bash
# =================================================================================================
# DNA shell requirements install
#
# Notes:
# - This file is used in DNA Dockerfile.project-core-pre
# - It is executed before python.requirements-dna.txt
# - N2ST library is available in script i.e., shell script function prefixed 'n2st::'
#
# =================================================================================================

# ....Update pip to latest.........................................................................
python3 -m pip install --upgrade pip
