"""A worksheet in structured using HTML/CSS that the student fills out with multiple free text responses."""

import importlib
import logging
import requests
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, Scope, Integer, String, Boolean
from xblock.utils.studio_editable import StudioEditableXBlockMixin

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
        'html_content',
        'disable_cache',
    ]

    display_name = String(
        display_name= 'Display Name',
        help= 'This is the title for this question type',
        default='Worksheet',
        scope=Scope.settings,
    )

    html_url = String(
        display_name= 'HTML URL',
        help= 'This is the HTML that defines the worksheet structure. HTML URL or HTML Content must be specified',
        default='',
        scope=Scope.settings,
    )

    html_content = String(
        display_name= 'HTML Content',
        help= 'This is the HTML that defines the worksheet structure. HTML URL or HTML Content must be specified',
        default='',
        scope=Scope.settings,
        multiline_editor=True,
    )

    student_answer = Dict(
        default={}, scope=Scope.user_state,
        help="A map of the user responses on the worksheet",
    )

    added_repeats = Integer(
        default=0, scope=Scope.user_state,
        help="Number of clones of the repeating section that the student added",
    )

    disable_cache = Boolean(
        display_name= 'Disable Cache',
        help= 'Disable caching of the HTML and CSS files (for testing updates to these files)',
        default=False,
        scope=Scope.settings,
    )

    resourceCache = {}

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def resource_from_url(self, url):
        """Handy helper for getting resources from a URL."""
        try:
            if not self.disable_cache and self.resourceCache.get(url):
                return self.resourceCache.get(url)
            if self.disable_cache:
                self.resourceCache.pop(url)
            response = requests.get(url)
            log.info('resource_from_url request %s %i', url, response.status_code);
            if response.status_code == requests.codes.ok:   # pylint: disable=no-member
                data = response.text
                self.resourceCache[url] = data
                log.info('resource_from_url response %s', data);
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

        
        content = self.html_content if self.html_content else (self.resource_from_url(self.html_url) or "<div><p>Empty worksheet</p></div>")
        try:
            html_ws = '<div id="worksheet">' + content + '</div>'
            tree = html.fragment_fromstring(html_ws)
            if self.student_answer != None:
                for count in range(self.added_repeats):
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
                    v = self.student_answer.get(e.get("name"))
                    if v != None:
                        e.text = v
                        if "value" not in (" " + e.get("class") + " "):
                            e.set("class", e.get("class")+" value")
            # we use c14n (canonical) to prevent <div></div> being collapsed to <div/>
            # because that causes strange behaviour in the XBlock
            html_output = etree.tostring(tree, method="c14n", pretty_print=True).decode("utf-8")

        except Exception:
            log.error('WorksheetBlock.student_view error parsing and enriching html', exc_info=True)
            html_output =  '<div>Invalid HTML</div>'
        log.info('WorksheetBlock.student_view html_output %s', html_output)
        frag = Fragment(html_output.format(self=self))
        css_str = importlib.resources.files(__package__).joinpath("static/css/worksheet.css").read_text(encoding="utf-8")
        frag.add_css(str(css_str))
        frag.add_javascript(self.resource_string("static/js/src/worksheet.js"))
        frag.initialize_js('WorksheetBlock')
        log.info('WorksheetBlock.student_view final fragment %s', frag)
        return frag


    @XBlock.json_handler
    def submit(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Update the worksheet responses
        """

        log.info('data %s', str(data))
        self.student_answer = data.get('student_answer') or {}
        self.added_repeats = data.get('added_repeats') or 0
        state = {'student_answer': self.student_answer, 'added_repeats': self.added_repeats }
        print(state)
        return state

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("WorksheetBlock1",
                """
                <worksheet
                    display_name="Test"
                    html_url="https://imsimbi-documents-public.s3.amazonaws.com/workbooks/worksheet.html"
                >
                </worksheet>
                """
            ),
             ("WorksheetBlock2",
                """
                <worksheet
                    display_name="Test"
                    html_url="https://imsimbi-documents-public.s3.amazonaws.com/workbooks/worksheet-activities.html"
                >
                </worksheet>
                """
            ),
        ]
