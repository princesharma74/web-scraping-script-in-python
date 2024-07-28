def append_hello_world(filename):
    # Check if the file exists
    try:
        with open(filename, 'r') as f:
            # File exists, do nothing
            pass
    except FileNotFoundError:
        # File does not exist, create it and append 'hello world'
        with open(filename, 'w') as f:
            f.write('hello world\n')

if __name__ == "__main__":
    filename = "output.txt"
    append_hello_world(filename)