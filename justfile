test-all:
    python -m unittest

test TEST:
    python -Wa -m unittest -k {{TEST}}
