"""A worksheet in tabular form that the student fills out with free text."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, Scope, XMLString
import logging;
from lxml import etree, html
from io import StringIO

log = logging.getLogger(__name__)
class WorksheetBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    responses = Dict(
        default={}, scope=Scope.user_state,
        help="A map of the user responses on the worksheet",
    )

    html = XMLString(
        default="<div></div>",
        scope=Scope.content,
        help="HTML fragment for the worksheet structure",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the WorksheetBlock, shown to students
        when viewing courses.
        """
        print(self.html)
        log.info('WorksheetBlock.studentView')
        html_ws = '<div id="worksheet">' + self.html + '</div>'

        tree   = html.fragment_fromstring(html_ws)
        inputs = tree.xpath("//*[contains(concat(' ', @class, ' '), ' input ')]")
        for e in inputs:
            v = self.responses[e.get("name")]
            if v != None:
                e.text = v
                if "value" not in (" " + e.get("class") + " "):
                    e.set("class", e.get("class")+" value")
        # we use c14n (canonical) to prevent <div></div> being collapsed to <div/>
        # because it causes strange behaviour in the XBlock
        htmlWithResponses = etree.tostring(tree, method="c14n", pretty_print=True).decode("utf-8")

        frag = Fragment(htmlWithResponses.format(self=self))
        frag.add_css(self.resource_string("static/css/worksheet.css"))
        frag.add_javascript(self.resource_string("static/js/src/worksheet.js"))
        frag.initialize_js('WorksheetBlock')

        return frag

    @XBlock.json_handler
    def submit(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Update the worksheet responses
        """

        log.info('data %O', data)
        self.responses = data['responses']

        return {'responses': data['responses'] }

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("WorksheetBlock",
             """
<worksheet>
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
</worksheet>
             """),
        ]
