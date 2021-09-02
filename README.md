# Worksheet XBlock

An OpenEdX XBlock that allows students to respond to multiple sections (using free text)
on an HTML/CSS structured worksheet
that may be in the form of a table or any other layout.


## Development

We use the xblock workbench here: https://github.com/edx/xblock-sdk

Follow the instructions to install and create it and then install this XBlock into 
the python virtual environment:

```sh
pip install --upgrade --force-reinstall  git+https://github.com/imsimbi-training/xblock-worksheet
```

Run the workbench in `xblock-sdk`:

```
python manage.py runserver
```

The XBlock should be available in the workbench

## Setting up a worksheet

A sample worksheet is shown below, and it needs to be valid HTML:

```html
<div>
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
    <div id="buttons"><p>You can add and delete rows to the worksheet</p></div>
</div>
```

Any cell that has a class `input` will allow the student to enter text 
(using an html `<textarea>`). A prompt should be given for each input as the inner text. 
A `name` attribute is used for referencing the response in the state (see below).

A tag with a `repeat` class can be replicated by the student, allowing them to provide 
multiple responses. This is explained below.

The rest of the HTML is used for static layout of the worksheet and any valid html 
can be used.

## Enriched HTML

The above worksheet template will be enriched:
- the entire fragment will be wrapped with a div tag that has id `worksheet`
- an element with `input` class is enriched with elements to input and display responses
- a submit button is added


```
<div id="worksheet">
    <div>
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
                    <div name="example1" class="xbt-cell input">
                        <pre>Enter test 1 here</pre>
                        <textarea placeholder="Enter test 1 here" hidden></textarea>
                    </div>
                    <div name="example2" class="xbt-cell input">
                        <pre>Enter test 1 here</pre>
                        <textarea placeholder="Enter test 1 here" hidden></textarea>
                    </div>
                </div>
        </div>
        <div id="buttons"><p>You can add and delete rows to the worksheet</p></div>
    </div>
    <button class="submit>Submit</button>
</div>
```

The `<textarea>` is used to enter a response to that input. The `<pre>` is used
to display the response.


Your CSS can be used to style these as you wish.
## Repeating sections

We allow the worksheet to have sections that can be repeated an arbitrary number of times. 

For example, a worksheet capturing a recipe might have an arbitrary number of steps that
the student can fill in.

This is achieved by adding a class `repeat` to any HTML element (there can currently only be one repeat section). Buttons will be automatically added to "Add" or "Delete" a
repeating section. When the student adds a repeating section, the HTML that has class `repeat`
will be cloned and appended directly below it. Names will be generated for 
each  element marked as an `input` using `{name}[{i}]`
where `name` is the name attribute of the original element and `i` is a zero-based index.

In the above example, adding a repeating section will effectively generate this:

```
<div>
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
            <div class="xbt-row">
                <div class="xbt-cell header">Row 2</div>
                <div name="example1[0]" class="xbt-cell input">Enter test 1 here</div>
                <div name="example2[0]" class="xbt-cell input">Enter test 2 here</div>
            </div>
    </div>
    <div id="buttons"><p>You can add and delete rows to the worksheet</p></div>
</div>
```

To track these changes and to assist with CSS, the original `repeat` element will have an
 additional class `repeat-original` and any added elementes will have classes 


The buttons to add and delete repeating elements are added to the div with id `buttons`:

```html
<div id="buttons"><p>You can add and delete rows to the worksheet</p>
    <button class="add"><i class="fa fa-2x fa-plus"/></button>
    <button class="delete"><i class="fa fa-2x fa-trash-o"/></button>
</div>
```

The delete button always deletes the last repeating element.

## State

The state will be stored with this structure:

```json
{
    "responses": {
        "name1": "response1",
        "name2": "response2",
    },
    "addedRepeats": 0,
}
```

Where `name1` and `name2` are names of elements that have the `input` class in the HTML.

`addedRepeats` records how many additional repeating sections were added by the student.

The names of added repeating sections will be `name[{i}]` where i is a zero based index.

## Sample CSS

An example of CSS to style the above HTML is shown below. It renders the
HTML in a table structure and also needs to style the buttons added
as described above.


```css
/* table formatting */

body {
    font-family: Helvetica, Arial, Sans-Serif;
  }
  
  .xblock-table {
    width: 100%;
    min-width: 600px;
  }
  
  
  .xblock-table .header {
    background-color:rgb(255, 218, 153);
    padding: 5px 10px;
  }
  
  .xblock-table td.static {
    background-color:rgb(218, 218, 218);
    padding: 5px 10px;
  }
  
  .xblock-table td.input {
    background-color:rgb(241, 241, 241);
    color:rgb(128, 128, 128);
  }
  
  .xblock-table td.input pre {
    padding: 5px 10px;
  }
  
  .xblock-table td.input.value {
    background-color:rgb(241, 241, 241);
    color:rgb(32, 32, 32);
  }
  
  .xblock-table td button {
    border-radius: 50%;
    border: 1px solid #444;
    color: #222;
    background: white;
    width: 25px;
    height: 25px;
    font-size: 100%;
  }
  
  .xblock-table td button:active {
    border-radius: 50%;
    border: 1px solid #bbb;
    color: #222;
    background: #ddd;
    width: 25px;
    height: 25px;
    font-size: 100%;
  }
  
  /* .xbt-table {
    display: flex;
    flex-direction: column;
  } */
  
  .xbt-row {
    display: table-row;
    /* flex-direction: row; */
  }
  
  .xbt-cell {
    display: table-cell;
  }
  
  
  .xbt-cell.header {
    background-color:rgb(255, 218, 153);
    padding: 5px 10px;
  }
  
  .xbt-cell.static {
    background-color:rgb(218, 218, 218);
    padding: 5px 10px;
  }
  
  .xbt-cell.input {
    background-color:rgb(241, 241, 241);
    color:rgb(128, 128, 128);
  }
  
  .xbt-cell.input pre {
    padding: 5px 10px;
  }
  
  .xbt-cell.input.value {
    background-color:rgb(241, 241, 241);
    color:rgb(32, 32, 32);
  }
  
  .xbt-cell button {
    border-radius: 50%;
    border: 1px solid #444;
    color: #222;
    background: white;
    width: 25px;
    height: 25px;
    font-size: 100%;
  }
  
  .xbt-cell button:active {
    border-radius: 50%;
    border: 1px solid #bbb;
    color: #222;
    background: #ddd;
    width: 25px;
    height: 25px;
    font-size: 100%;
  }
  .xbt-cell button:active {
    border-radius: 50%;
    border: 1px solid #bbb;
    color: #222;
    background: #ddd;
    width: 25px;
    height: 25px;
    font-size: 100%;
  }
  
  #buttons button {
    background-color: #f1bb4e;
  }

  button.submit {
    background-color: #156bbb;
  }

  button.submit:active {
    background-color: #0b4983;
  }

  #worksheet button {
    display: inline-block;
  
    padding: 0.3em 1.2em;
    margin:0 0.1em 0.1em 0;
    border:0.16em solid rgba(255,255,255,0);
    border-radius:2em;
    box-sizing: border-box;
    text-decoration: none;
    font-family: 'Roboto',sans-serif;
    color: #FFFFFF;
    /* text-shadow: 0 0.04em 0.04em rgba(0,0,0,0.35); */
    text-align: center;
    transition: all 0.2s;
    margin: 10px;
  }
  
  #worksheet button:hover{
    border-color: rgba(196,196,196,1);
  }
  
  #buttons button:active{
    background-color: #e4a01a;
  }
  
  
  @media all and (max-width:30em) {
    #buttons button {
      display:block;
      margin:0.2em auto;
    }
  } 
  
```
