"""A worksheet in tabular form that the student fills out with free text."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, Scope, XMLString, Integer, String
from xblockutils.studio_editable import StudioEditableXBlockMixin
import logging;
from lxml import etree, html
from copy import deepcopy

log = logging.getLogger(__name__)
class WorksheetBlock(StudioEditableXBlockMixin, XBlock):
    """
    An HTML worksheet with sections to be filled in by a student.
    Typically it could be in the structure of a table or other graphical structure
    of organising information
    """

    editable_fields = [
        'display_name',
    ]

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    display_name = String(
        display_name= 'Display Name',
        help= 'This is the title for this question type',
        default='Worksheet',
        scope=Scope.settings,
    )

    responses = Dict(
        default={}, scope=Scope.user_state,
        help="A map of the user responses on the worksheet",
    )

    addedRepeats = Integer(
        default=0, scope=Scope.user_state,
        help="Number of clones of the repeating section that the student added",
    )

    # content = XMLString(
    #     default="""<div class="input" name="cell1"></div>""",
    #     scope=Scope.content,
    #     help="HTML fragment for the worksheet structure",
    # )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # Displays the worksheet
    def student_view(self, context=None):
        """
        The primary view of the WorksheetBlock, shown to students
        when viewing courses.
        """
       
        # # log.info('WorksheetBlock.student_view %s %s', self, context)
        # # if not self.content:
        # #     html_output = '<div>Empty worksheet</div>'
        # else:
        content = self.resource_string("static/html/worksheet.html")
        print("student_view %s %s %s", self.studio_view, self.author_view)
        try:
            html_ws = '<div id="worksheet">' + content + '</div>'
            tree = html.fragment_fromstring(html_ws)
            if self.responses != None:
                # add the values from state into the worksheet
                # FIXME if added repeating fields are included in the responses
                # then we must add these to the HTML following the same algorithm used in the JS

                for count in range(self.addedRepeats):
                    try:
                        repeat = tree.xpath("//*[contains(concat(' ', @class, ' '), ' repeat ')]")[0]
                        clone = deepcopy(repeat)
                        inputs = clone.xpath("//*[contains(concat(' ', @class, ' '), ' input ')]")
                        for input in inputs:                            
                            name = input.get("name")+"["+str(count+1)+"]"
                            input.set("name", name)
                        clone.set("class", clone.get("class")+" repeat-clone")
                        repeat.getparent().append(clone)
                    except Exception as ex:
                        print(ex)
                        pass

                inputs = tree.xpath("//*[contains(concat(' ', @class, ' '), ' input ')]")
                for e in inputs:
                    v = self.responses.get(e.get("name"))
                    if v != None:
                        e.text = v
                        if "value" not in (" " + e.get("class") + " "):
                            e.set("class", e.get("class")+" value")
            # we use c14n (canonical) to prevent <div></div> being collapsed to <div/>
            # because it causes strange behaviour in the XBlock
            html_output = etree.tostring(tree, method="c14n", pretty_print=True).decode("utf-8")

        except Exception:
            log.error('WorksheetBlock.student_view error parsing and enriching html', exc_info=True)
            html_output =  '<div>Invalid HTML</div>'
        log.info('WorksheetBlock.student_view html_output %s', html_output)
        frag = Fragment(html_output.format(self=self))
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
        self.responses = data.get('responses') or {}
        self.addedRepeats = data.get('addedRepeats') or 0
        state = {'responses': self.responses, 'addedRepeats': self.addedRepeats }
        print(state)
        return state


    # parses the HTML content inside the <worksheet> tag
    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Parse the XML for an HTML block.

        The entire subtree under `node` is re-serialized, and set as the
        content of the XBlock.

        """
        block = runtime.construct_xblock_from_class(cls, keys)

        block.content = str(node.text or "")
        for child in node:
            block.content += etree.tostring(child, encoding='unicode')

        return block

    def add_xml_to_node(self, node):
        """
        Set attributes and children on `node` to represent ourselves as XML.

        We parse our HTML content, and graft those nodes onto `node`.

        """
        xml = "<html_demo>" + self.content + "</html_demo>"
        html_node = etree.fromstring(xml)

        node.tag = html_node.tag
        node.text = html_node.text
        for child in html_node:
            node.append(child)

    # def studio_view(self, context):
    #     """
    #     Create a fragment used to display the edit view in the Studio.
    #     """
    #     html_str = pkg_resources.resource_string(__name__, "static/html/worksheet_studio.html")
    #     href = self.href or ''
    #     frag = Fragment(html_str.format(href=href, maxwidth=self.maxwidth, maxheight=self.maxheight))

    #     return frag

    # @XBlock.json_handler
    # def studio_submit(self, data, suffix=''):
    #     """
    #     Called when submitting the form in Studio.
    #     """
    #     self.href = data.get('href')
    #     self.maxwidth = data.get('maxwidth')
    #     self.maxheight = data.get('maxheight')

    #     return {'result': 'success'}


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
