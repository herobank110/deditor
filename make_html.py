"""Produce HTML editor output from DEditor parsing.
"""

from DEditor import dcompile_ast


HTML_BOILERPLATE_START = (
"""<html>
<head><script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script><script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script><script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body {  display: grid;  align-items: center;  justify-items: center;  margin: 30px;}.num-edit__label {  user-select: none;}.num-edit__input {  width: 5rem;  outline: none;  border: 1px solid lightgrey;  border-radius: 4px;  padding: 3px;  height: 1.5em;}.prop-container {  width: 400px;}.prop-container summary {  user-select: none;}.prop-container__inner {  margin: 0.5rem 1rem;}.prop-container__edit-grid {  display: grid;  grid-template-columns: auto 1fr;  align-items: baseline;  column-gap: 10px;  row-gap: 3px;}</style></head>
<body>
    <h2 class="mb-5">My Editor Interface</h2>
"""
)

HTML_BOILERPLATE_END = (
"""</body>
</html>"""
)

def main():
    with open("test2_class.py", buffering=8096) as file:
        my_collection = dcompile_ast(file)

    with open("index.html", "w") as file:
        file.write(HTML_BOILERPLATE_START)
        file.write(HTML_BOILERPLATE_END)

if __name__ == '__main__':
    main()
