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


class EditorHtmlProduction:
    def __init__(self):
        self.file = open("index.html", "w")
        self.add(HTML_BOILERPLATE_START)

    def __del__(self):
        self.add(HTML_BOILERPLATE_END)
        self.file.close()

    def add(self, text_output):
        self.file.write(text_output)

    def add_collection(self, collection):
        # Start the collection
        self.add(
            '<details class="prop-container">'
            '   <summary>%s</summary>'
            '   <div class="prop-container__inner">'
            '       <div class="prop-container__edit-grid">'
            % collection.collection_name
        )

        # Add the properties
        for prop in collection.dproperties:
            self.add_text_edit(prop.display_name, prop.default_val)

        # Finish the collection HTML attributes!
        self.add(
            '       </div>' # prop-container__edit-grid
            '   </div>' # prop-container__inner
            '</details>' # prop-container
        )

    def add_text_edit(self, name, value):
        self.add(
            '<label class="num-edit__label">%s</label>'
            '<input class="num-edit__input" value="%s"/>'
            % (name, value)
        )

def main():
    with open("test2_class.py", buffering=8096) as file:
        my_collection = dcompile_ast(file)

    out = EditorHtmlProduction()
    out.add_collection(my_collection)

if __name__ == '__main__':
    main()
