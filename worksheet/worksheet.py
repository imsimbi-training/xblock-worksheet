"""A worksheet in tabular form that the student fills out with free text."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, Scope
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

        log.info('WorksheetBlock.studentView')
        html_ws = '<div id="worksheet">' + self.resource_string("static/html/worksheet.html") + '</div>'

        tree   = html.fragment_fromstring(html_ws)
        inputs = tree.xpath("//*[contains(concat(' ', @class, ' '), ' input ')]")
        for e in inputs:
            v = self.responses[e.get("name")]
            if v != None:
                e.text = v
                if "value" not in (" " + e.get("class") + " "):
                    e.set("class", e.get("class")+" value")
        htmlWithResponses = etree.tostring(tree, pretty_print=True).decode("utf-8")
        print(htmlWithResponses)

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
             """<worksheet/>
             """),
            ("Multiple WorksheetBlock",
             """<vertical_demo>
                <worksheet/>
                <worksheet/>
                <worksheet/>
                </vertical_demo>
             """),
        ]
