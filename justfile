test-all:
    python -m unittest

test TEST:
    python -Wa -m unittest -k {{TEST}}

release:
    bumpver update --minor
    python -m build
    twine upload --skip-existing dist/*
