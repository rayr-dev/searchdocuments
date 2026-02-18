#tests/test_something.py
def test_something_with_temp_dir(temp_dir):
    path = os.path.join(temp_dir, "file.txt")
    with open(path, "w") as f:
        f.write("hello")