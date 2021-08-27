# Worksheet XBlock

An OpenEdX XBlock that allows students to capture freeform text on a structured worksheet
that may be in the form of a table or any other layout that can be created in html.


## Development

We use the xblock workbench here: https://github.com/edx/xblock-sdk

Follow the instructions to install and create it and then install this XBlock into 
the python virtual environment:

```sh
pip install git+https://github.com/imsimbi-training/xblock-worksheet
```

## Setting up a worksheet

A sample worksheet is shown below:

```html
<div id="worksheet">
    <div class="xbt-table">
            <div class="xbt-row">
                <div class="xbt-cell header"></div>
                <div class="xbt-cell header">Column 1</div>
                <div class="xbt-cell header">Column 2</div>
            </div>
            <div class="xbt-row">
                <div class="xbt-cell header">Row 1</div>
                <div class="xbt-cell static">Example 1</div>
                <div class="xbt-cell static">Example 2</div>
            </div>
            <div class="xbt-row repeat">
                <div class="xbt-cell header">Row 2</div>
                <div name="example1" class="xbt-cell input">Enter test 1 here</div>
                <div name="example2" class="xbt-cell input">Enter test 2 here</div>
            </div>
    </div>
    <div id="repeat-buttons"><p>You can add and delete rows to the worksheet</p></div>
</div>
```

Any cell that has a class `input` will allow the student to enter text (using an html `<textarea>`). A prompt should be given for each input. A `name` attribute is used 
for storing the response in the state (see below).

A tag with a `repeat` class can be replicated by the student, allowing them to provide 
multiple responses. Buttons are added to the html to add and delete these subsections.

These buttons are added as children of the element with id `repeat-buttons`.

The rest of the HTML is used for static layout of the worksheet and any valid html 
can be used.




## State