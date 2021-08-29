/* Javascript for WorksheetBlock. */
function WorksheetBlock(runtime, element) {  
    var addedRepeats = 0;
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
        var clones = $('.repeat.repeat-clone', element);
        if (clones.length > 0) {
            clones.last().remove();
            addedRepeats -= 1;
        }
    }

    function addRepeatingSection(event) {
        var repeat = $('.repeat.repeat-original', element);
        var numClones = $('.repeat.repeat-clone', element).length;
        var clone = repeat.clone(true);
        $('.input', clone).each((function() {
            var placeholder = $('textarea', this).attr('placeholder');
            $('textarea', this).val('');
            $('pre', this).text(placeholder);
            var name = $(this).attr('name');
            name = name.concat('[',numClones+1,']');
            $(this).attr('name', name).removeClass('value');
        }))
        clone.addClass('repeat-clone');
        clone.removeClass('repeat-original');
        addedRepeats += 1;

        // repeat.children[0].hidden = true;
        repeat.parent().append(clone);
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
            data: JSON.stringify({responses: responses, addedRepeats: addedRepeats}),
            success: submitSuccess,
            error: submitError
        });
    }

    $('.repeat').not('.repeat-clone').addClass('repeat-original');

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
    var numRepeats = $('.repeat').length;
    if (numRepeats > 0) {
        var tdAddButton = $('<button class="add"><i class="fa fa-2x fa-plus"></i></button>')
        var tdDeleteButton = $('<button class="delete"><i class="fa fa-2x fa-trash-o"></i></button>');
        tdAddButton.click(addRepeatingSection);
        tdDeleteButton.click(deleteRepeatingSection);
        $('#buttons', element).append(tdAddButton, tdDeleteButton);
    }
    var submitButton = $('<button class="submit">Submit</button>');
    submitButton.click(submit);
    $('#worksheet', element).append(submitButton);
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
