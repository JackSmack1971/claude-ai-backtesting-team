# Synthetic placeholder "simulation" for the smoke fixture only.
# Not a real trading strategy: deterministically doubles a fixed list of
# numbers so the fixture has *something* to fingerprint as "code".
def run(values):
    return [v * 2 for v in values]


if __name__ == "__main__":
    print(run([1, 2, 3]))
