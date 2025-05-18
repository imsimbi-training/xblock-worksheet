/* Javascript for WorksheetBlock. */
function WorksheetBlock(runtime, element) {  
    var added_repeats = $('.repeat-clone', element).length;
    var dirty = false;
    const instance_id = element.id;
    function setDirty(isDirty) {
        dirty = isDirty;
        $('.submit', element).prop('disabled', !dirty);
    }
    function beforeUnload(event) {
        console.log('beforeUnload', dirty);
        if (dirty) {
            console.log('preventDefault');
            event.preventDefault();
            event.returnValue = '';
        }
    }
    function editField(event) {
        var inputContainer = $(event.target.parentElement);
        var pre = $('pre', inputContainer);
        var ta = $('textarea', inputContainer);
        var w = pre.width();
        var h = pre.height();
        ta.width(w+20);
        ta.height(h+20);
        ta.addClass('visible')
        pre.removeClass('visible')
        ta.focus();
    }
    function saveField(event) {
        var inputContainer = $(event.target.parentElement);
        var ta = $('textarea', inputContainer);
        var pre = $('pre', inputContainer);
        ta.removeClass('visible')
        pre.addClass('visible')
        var text = ta.val();
        pre.text(text || ta.attr('placeholder'));
        if (text) inputContainer.addClass('value'); else inputContainer.removeClass('value');
        setDirty(true);
    }
    function deleteRepeatingSection(event) {
        var clones = $('.repeat.repeat-clone', element);
        if (clones.length > 0) {
            clones.last().remove();
            added_repeats -= 1;
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
        added_repeats += 1;

        // repeat.children[0].hidden = true;
        repeat.parent().append(clone);
    }

    function submitSuccess(votes) {
        console.log('submitSuccess');
        setDirty(false);
        $('.input', element)
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
            data: JSON.stringify({student_answer: responses, added_repeats: added_repeats}),
            success: submitSuccess,
            error: submitError
        });
    }

    $('.input', element)
    .append(function (i, e) {
        // e is the inner text
        var pre = $('<pre class="visible"></pre>').css({
            width: '100%',
            height: '100%',
            // margin: 0,
            // padding: '0.5em',
            // 'box-sizing': 'border-box',
            // overflow: 'auto'
          });
        pre.text(e);
        return pre;
    })
    .append(function (i, e) {
        var inner = $(this).contents().filter(function () {return this.nodeType === 3;}).text();
        var value = $(this).hasClass('value');
        let ta = $('<textarea></textarea>').blur(saveField).attr('placeholder', inner).on('keydown', function(e) {
            // For Mac: Command (metaKey), for Windows/Linux: Control (ctrlKey)
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                $(this).blur();
                // Optionally, prevent the default newline
                e.preventDefault();
            }
        });
        if (value) ta = ta.val(inner);
        return ta;
    })
    // remove the inner text node
    .contents().filter(function () {return this.nodeType === 3;}).remove();
    $('.input', element)
    .on('click', editField);    
    var numRepeats = $('.repeat').length;
    if (numRepeats > 0) {
        var tdAddButton = $('<button class="add"><i class="fa fa-2x fa-plus"></i></button>')
        var tdDeleteButton = $('<button class="delete"><i class="fa fa-2x fa-trash-o"></i></button>');
        tdAddButton.on('click', addRepeatingSection);
        tdDeleteButton.on('click', deleteRepeatingSection);
        $('#buttons', element).append(tdAddButton, tdDeleteButton);
    }
    var submitButton = $('<button class="submit">Submit</button>');
    submitButton.on('click', submit).prop('disabled', true);
    $('.worksheet-root', element).append(submitButton);
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
    window.addEventListener('beforeunload', beforeUnload);
}
