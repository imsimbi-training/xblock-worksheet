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
        "display_name",
        "html_url",
        "html_content",
        "initial_repeats",
        "disable_cache",
    ]

    display_name = String(
        display_name="Display Name",
        help="This is the title for this question type",
        default="Worksheet", #type: ignore
        scope=Scope.settings,
    )

    html_url = String(
        display_name="HTML URL",
        help="This is the HTML that defines the worksheet structure. HTML URL or HTML Content must be specified",
        default="", #type: ignore
        scope=Scope.settings,
    )

    html_content = String(
        display_name="HTML Content",
        help="This is the HTML that defines the worksheet structure. HTML URL or HTML Content must be specified",
        default="", #type: ignore
        scope=Scope.settings,
        multiline_editor=True,
    )

    initial_repeats = Integer(
        display_name="Initial Repeats",
        help="This is the number of repeated sections that should be displayed initially",
        default=0, #type: ignore
        scope=Scope.settings,
    )

    student_answer = Dict(
        default={},#type: ignore
        scope=Scope.user_state,
        help="A map of the user responses on the worksheet",
    )

    added_repeats = Integer(
        default=0, #type: ignore
        scope=Scope.user_state,
        help="Number of clones of the repeating section that the student added",
    )

    disable_cache = Boolean(
        display_name="Disable Cache",
        help="Disable caching of the HTML and CSS files (for testing updates to these files)",
        default=False, #type: ignore
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
                self.resourceCache.pop(url, None)
            response = requests.get(url, timeout=10)
            log.info("resource_from_url request %s %i", url, response.status_code)
            if response.status_code == requests.codes.ok:  # pylint: disable=no-member
                data = response.text
                self.resourceCache[url] = data
                log.info("resource_from_url response %s", data)
                return data
            return None
        except:
            log.info("Error loading URL", exc_info=True)
            return None

    # Displays the worksheet
    def student_view(self, context=None):
        """
        The primary view of the WorksheetBlock, shown to students
        when viewing courses.
        """
        instance_id = str(self.scope_ids.usage_id)
        repeats = max(self.initial_repeats or 0, self.added_repeats or 0)

        content = (
            self.html_content
            if self.html_content
            else (
                self.resource_from_url(self.html_url)
                or "<div><p>Empty worksheet</p></div>"
            )
        )
        try:
            html_ws = (
                f'<div id="worksheet-{instance_id}" class="worksheet-root">'
                + content
                + "</div>"
            )
            tree = html.fragment_fromstring(html_ws)
            repeat_element_list = tree.xpath(
                "//*[contains(concat(' ', @class, ' '), ' repeat ')]"
            )
            repeat_element = (
                repeat_element_list[0]
                if len(repeat_element_list) > 0
                else None
            )

            if self.student_answer is not None:
                if repeat_element is not None:
                    for count in range(repeats):
                        try:
                            clone = deepcopy(repeat_element)
                            repeat_element.getparent().append(clone)
                            inputs = clone.xpath(
                                ".//*[contains(concat(' ', @class, ' '), ' input ')]"
                            )
                            for input_element in inputs:
                                name = (
                                    input_element.get("name") + "[" + str(count + 1) + "]"
                                )
                                input_element.set("name", name)
                            clone.set("class", clone.get("class") + " repeat-clone")
                            repeat_element.getparent().append(clone)
                        except Exception as ex:
                            log.info(
                                "repeat or input elements not found: %s", ex, exc_info=True
                            )

                inputs = tree.xpath(
                    "//*[contains(concat(' ', @class, ' '), ' input ')]"
                )
                for input_element in inputs:
                    value = self.student_answer.get(input_element.get("name"))
                    if value is not None:
                        input_element.text = value
                        if "value" not in (" " + input_element.get("class") + " "):
                            input_element.set(
                                "class", input_element.get("class") + " value"
                            )
            if repeat_element is not None:
                repeat_element.set(
                    "class", repeat_element.get("class") + " repeat-original"
                )
            # we use c14n (canonical) to prevent <div></div> being collapsed to <div/>
            # because that causes strange behaviour in the XBlock
            html_output = etree.tostring(tree, method="c14n", pretty_print=True).decode(
                "utf-8"
            )

        except Exception:
            log.error(
                "WorksheetBlock.student_view error parsing and enriching html",
                exc_info=True,
            )
            html_output = "<div>Invalid HTML</div>"
        log.info("WorksheetBlock.student_view html_output %s", html_output)
        frag = Fragment(html_output.format(self=self))
        css_str = (
            importlib.resources.files(__package__)
            .joinpath("static/css/worksheet.css")
            .read_text(encoding="utf-8")
        )
        frag.add_css(str(css_str))
        frag.add_javascript(self.resource_string("static/js/src/worksheet.js"))
        frag.initialize_js("WorksheetBlock")
        log.info("WorksheetBlock.student_view final fragment %s", frag)
        return frag

    @XBlock.json_handler
    def submit(self, data, suffix=""):  # pylint: disable=unused-argument
        """
        Update the worksheet responses
        """

        log.info("data %s", str(data))
        self.student_answer = data.get("student_answer") or {}
        self.added_repeats = data.get("added_repeats") or 0
        state = {
            "student_answer": self.student_answer,
            "added_repeats": self.added_repeats,
        }
        log.info("submit state %s", state)
        return state

    @staticmethod
    def workbench_scenarios():
        """canned scenarios for display in the workbench."""
        return [
            (
                "WorksheetBlock1",
                """
                    <worksheet
                        display_name="Test 1"
                        html_url="https://imsimbi-documents-public.s3.amazonaws.com/workbooks/worksheet.html"
                        initial_repeats="2"
                    >
                    </worksheet>
                    """,
            ),
            (
                "WorksheetBlock2",
                """
                    <worksheet
                        display_name="Test 2"
                        html_url="https://imsimbi-documents-public.s3.amazonaws.com/workbooks/worksheet-activities.html"
                        initial_repeats="2"
                    >
                    </worksheet>
                    """,
            ),
            (
                "Worksheet Leadership qualities",
                """
                    <worksheet
                        display_name="Leadership qualities"
                        html_url="https://imsimbi-documents-public.s3.us-east-1.amazonaws.com/workbooks/leadership-roles-and-qualities.html"
                    >
                    </worksheet>
                    """,
            ),
        ]
