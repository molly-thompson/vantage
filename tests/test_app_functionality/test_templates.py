import pytest
from django.contrib.messages import add_message
from django.contrib.messages import constants as message_levels
from django.http import HttpRequest
from django.template.loader import render_to_string


# TEST BASE.HTML
def test_base_template_renders_child_blocks() -> None:
    content = render_to_string("test_base.html")

    assert "<title>Test Page</title>" in content
    assert '<link href="https://some_stylesheet.com">' in content
    assert "<p>Test content</p>" in content
    assert '<script src="some_js_file.js"></script>' in content


def test_base_template_renders_messages(message_request: HttpRequest) -> None:
    add_message(
        message_request,
        message_levels.SUCCESS,
        "Test success message",
    )

    content = render_to_string(
        "test_base.html",
        request=message_request,
    )

    assert "Test success message" in content


@pytest.mark.parametrize(
    ("message_level", "message_type"),
    [
        (message_levels.SUCCESS, "success"),
        (message_levels.WARNING, "warning"),
        (message_levels.ERROR, "error"),
        (message_levels.INFO, "info"),
    ],
)
def test_base_template_renders_message_type(
    message_request: HttpRequest,
    message_level: int,
    message_type: str,
) -> None:
    add_message(
        message_request,
        message_level,
        "Test message",
    )

    content = render_to_string(
        "test_base.html",
        request=message_request,
    )

    assert "Test message" in content
    assert f"text-{message_type}" in content
    assert f"bg-{message_type}/10" in content
    assert f"border-{message_type}/20" in content
