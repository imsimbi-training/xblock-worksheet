"""A worksheet in tabular form that the student fills out with free text."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, Scope, XMLString, Integer, String
from xblockutils.studio_editable import StudioEditableXBlockMixin
import logging
import requests

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
        'html_url',
        'css_url',
    ]

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    display_name = String(
        display_name= 'Display Name',
        help= 'This is the title for this question type',
        default='Worksheet',
        scope=Scope.settings,
    )

    html_url = String(
        display_name= 'HTML URL',
        help= 'This is the HTML that defines the worksheet structure',
        default='',
        scope=Scope.settings,
    )

    css_url = String(
        display_name= 'CSS URL',
        help= 'This is the CSS that styles the worksheet structure',
        default='',
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

    resourceCache = {}

    # content = XMLString(
    #     default="""<div class="input" name="cell1"></div>""",
    #     scope=Scope.content,
    #     help="HTML fragment for the worksheet structure",
    # )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def resource_from_url(self, url):
        """Handy helper for getting resources from a URL."""
        try:
            if self.resourceCache.get(url):
                return self.resourceCache.get(url)
            response = requests.get(url)
            if response.status_code == requests.codes.ok:   # pylint: disable=no-member
                data = response.text
                self.resourceCache[url] = data
                return data
            return None
        except:
            log.info('Error loading URL', exc_info=True)
            return None

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
        content = self.resource_from_url(self.html_url) or "<div><p>Empty worksheet</p></div>"
        css = self.resource_from_url(self.css_url) or ""
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
        frag.add_css(css)
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
                <worksheet
                    display_name="Test"
                    html_url="https://imsimbi-documents-public.s3.amazonaws.com/workbooks/worksheet.html"
                    css_url="https://imsimbi-documents-public.s3.amazonaws.com/workbooks/worksheet.css"
                >
                </worksheet>
                """
            ),
        ]
