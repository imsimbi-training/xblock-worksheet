/* Javascript for WorksheetBlock. */
function WorksheetBlock(runtime, element) {  
    console.log('runtime', runtime);
    function editField(event) {
        var pre = $('pre', event.target.parentElement);
        var inputContainer = pre.parent();
        var ta = $('textarea', inputContainer);
        ta.show();
        pre.hide();
        ta.focus();
    }
    function saveField(event) {
        var ta = $('textarea', event.target.parentElement);
        var inputContainer = ta.parent();
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
        var td = $('.repeat.repeat-original', element);
        var td2 = td.clone(true);
        $('.input', td2).each((function() {
            var placeholder = $('textarea', this).attr('placeholder');
            $('textarea', this).val('');
            $('pre', this).text(placeholder);
        }))
        td2.addClass('repeat-clone');
        td2.removeClass('repeat-original');
        // td.children[0].hidden = true;
        td.parent().append(td2);
    }

    function submitSuccess(votes) {
        console.log('submitSuccess');
    }

    function submitError(xhtml, error, errorThrown) {
        console.log('submitError', error, errorThrown);
    }

    function submit() {
        var handlerUrl = runtime.handlerUrl(element, 'submit');

        var values = $('.input.value pre').toArray().map((e) => $(e).text());
        var names = $('.input.value').toArray().map((e) => $(e).attr('name'));
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
