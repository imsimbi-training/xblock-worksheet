/* Javascript for WorksheetBlock. */
function WorksheetBlock(runtime, element) {  
    function editField(event) {
        console.log("cell gains focus", event);
        var pre = $('pre', event.target.parentElement);
        console.log("pre gains focus", pre);
        var inputContainer = pre.parent();
        console.log("parent gains focus", inputContainer);
        var ta = $('textarea', inputContainer);
        console.log("ta gains focus", ta);
        ta.show();
        pre.hide();
        ta.focus();
    }
    function saveField(event) {
        console.log("cell lose focus", event);
        var ta = $('textarea', event.target.parentElement);
        var inputContainer = ta.parent();
        console.log("parent gains focus", inputContainer);
        var pre = $('pre', inputContainer);
        ta.hide();
        pre.show();
        var text = ta.val();
        pre.text(text || ta.attr('placeholder'));
        if (text) inputContainer.addClass('value'); else inputContainer.removeClass('value');

    }
    function deleteRepeatingSection(event) {
        $('.repeat.repeat-clone', element).last().remove();
    }
    function addRepeatingSection(event) {
        console.log('bt', event);
        var td = $('.repeat.repeat-original', element);
        var td2 = td.clone(true);
        $('.input', td2).each((function() {
            var placeholder = $('textarea', this).attr('placeholder');
            console.log('placeholder', placeholder);
            $('textarea', this).val('');
            $('pre', this).text(placeholder);
        }))
        td2.addClass('repeat-clone');
        td2.removeClass('repeat-original');
        // td.children[0].hidden = true;
        td.parent().append(td2);
    }

    function submitSuccess(votes) {
        console.logs('submitSuccess');
    }

    function submitError(xhtml, error, errorThrown) {
        console.logs('submitError', error, errorThrown);
    }

    function submit() {
        var handlerUrl = runtime.handlerUrl(element, 'submit');

        var values = $('.input pre').toArray().map((e) => $(e).text());
        console.log('values', values);
        var names = $('.input').toArray().map((e) => $(e).attr('name'));
        console.log('names', names);
        var responses = {};
        names.forEach((o, i) => responses[o] = values[i]);
        console.log('responses', responses);
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({responses: responses}),
            success: submitSuccess,
            error: submitError
        });
    }

    $('.repeat').addClass('repeat-original');

    $('.input', element)
    .click(editField)
    .append(function (i, e) {
        var pre = $('<pre></pre>');
        pre.text(e);
        return pre;
    })
    .append(function (i, e) {
        var inner = $(this).contents().filter(function () {return this.nodeType === 3;}).text();
        return $('<textarea hidden></textarea>').blur(saveField).attr('placeholder', inner);
    })
    // remove the inner text node
    .contents().filter(function () {return this.nodeType === 3;}).remove();
    var tdAddButton = $('<button class="add"><i class="fa fa-2x fa-plus"></i></button>')
    var tdDeleteButton = $('<button class="delete"><i class="fa fa-2x fa-trash-o"></i></button>');
    tdAddButton.click(addRepeatingSection);
    tdDeleteButton.click(deleteRepeatingSection);
    $('#buttons', element).append(tdAddButton, tdDeleteButton);
    var submitButton = $('<button class="submit">Submit</button>');
    submitButton.click(submit);
    $('#worksheet', element).append(submitButton);
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
