import pytest

import prompts
from prompts.templates import render


def test_render():
    tpl = """
    A test string"""
    assert render(tpl) == "A test string"

    tpl = """
    A test string
    """
    assert render(tpl) == "A test string"

    tpl = """
        A test
        Another test
    """
    assert render(tpl) == "A test\nAnother test"

    tpl = """A test
        Another test
    """
    assert render(tpl) == "A test\nAnother test"

    tpl = """
        A test line
            An indented line
    """
    assert render(tpl) == "A test line\n    An indented line"

    tpl = """
        A test line
            An indented line

    """
    assert render(tpl) == "A test line\n    An indented line\n"


def test_render_escaped_linebreak():
    tpl = """
        A long test \
        that we break \
        in several lines
    """
    assert render(tpl) == "A long test that we break in several lines"

    tpl = """
        Break in \
        several lines \
        But respect the indentation
            on line breaks.
        And after everything \
        Goes back to normal
    """
    assert (
        render(tpl)
        == "Break in several lines But respect the indentation\n    on line breaks.\nAnd after everything Goes back to normal"
    )


def test_render_jinja():
    """Make sure that we can use basic Jinja2 syntax, and give examples
    of how we can use it for basic use cases.
    """

    # Notice the newline after the end of the loop
    examples = ("one", "two")
    prompt = render(
        """
        {% for e in examples %}
        Example: {{e}}
        {% endfor -%}""",
        examples=examples,
    )
    assert prompt == "Example: one\nExample: two\n"

    # We can remove the newline by cloing with -%}
    examples = ("one", "two")
    prompt = render(
        """
        {% for e in examples %}
        Example: {{e}}
        {% endfor -%}

        Final""",
        examples=examples,
    )
    assert prompt == "Example: one\nExample: two\nFinal"

    # Same for conditionals
    tpl = """
        {% if is_true %}
        true
        {% endif -%}

        final
        """
    assert render(tpl, is_true=True) == "true\nfinal"
    assert render(tpl, is_true=False) == "final"

    # Ignore leading white spaces
    examples = ("one", "two")
    prompt = render(
        """
        {% for e in examples %}
          {{- e }}
        {% endfor %}
        """,
        examples=examples,
    )
    assert prompt == "one\ntwo\n"

    # Do not ignore leading white spaces
    examples = ("one", "two")
    prompt = render(
        """
        {% for e in examples %}
          {{ e }}
        {% endfor %}
        """,
        examples=examples,
    )
    assert prompt == "  one\n  two\n"


def test_prompt_basic():
    @prompts.template
    def test_tpl(variable):
        """{{variable}} test"""

    assert test_tpl.template == "{{variable}} test"
    assert list(test_tpl.signature.parameters.keys()) == ["variable"]

    with pytest.raises(TypeError):
        test_tpl(v="test")

    p = test_tpl("test")
    assert p == "test test"

    p = test_tpl(variable="test")
    assert p == "test test"

    @prompts.template
    def test_single_quote_tpl(variable):
        "${variable} test"

    p = test_tpl("test")
    assert p == "test test"


def test_prompt_kwargs():
    @prompts.template
    def test_kwarg_tpl(var, other_var="other"):
        """{{var}} and {{other_var}}"""

    assert test_kwarg_tpl.template == "{{var}} and {{other_var}}"
    assert list(test_kwarg_tpl.signature.parameters.keys()) == ["var", "other_var"]

    p = test_kwarg_tpl("test")
    assert p == "test and other"

    p = test_kwarg_tpl("test", other_var="kwarg")
    assert p == "test and kwarg"

    p = test_kwarg_tpl("test", "test")
    assert p == "test and test"


def test_no_prompt():
    with pytest.raises(TypeError, match="template"):

        @prompts.template
        def test_empty(variable):
            pass

    with pytest.raises(TypeError, match="template"):

        @prompts.template
        def test_only_code(variable):
            return variable


@pytest.mark.filterwarnings("ignore: The model")
def test_dispatch():

    @prompts.template
    def simple_prompt(query: str):
        """{{ query }}"""

    @simple_prompt.register("provider/name")
    def simple_prompt_name(query: str):
        """name: {{ query }}"""

    assert list(simple_prompt.registry.keys()) == ["provider/name"]
    assert callable(simple_prompt)
    assert callable(simple_prompt["provider/name"])

    assert simple_prompt.model is None
    assert simple_prompt_name.model == "provider/name"
    assert simple_prompt["provider/name"].model == "provider/name"

    assert simple_prompt("test") == "test"
    assert simple_prompt_name("test") == "name: test"

    assert simple_prompt("test") == "test"
    assert simple_prompt["gpt2"]("test") == "test"
    assert simple_prompt["provider/name"]("test") == "name: test"


def test_special_tokens():

    @prompts.template
    def simple_prompt(query: str):
        """{{ bos + query + eos }}"""

    assert simple_prompt("test") == "test"
    assert simple_prompt["openai-community/gpt2"]("test") == "test<|endoftext|>"
    assert simple_prompt["mistralai/Mistral-7B-v0.1"]("test") == "<s>test</s>"


def test_warn():

    @prompts.template
    def simple_prompt():
        """test"""

    with pytest.warns(UserWarning, match="not present in the special token"):
        simple_prompt["non-existent-model"]()
