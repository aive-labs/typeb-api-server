from jinja2 import Environment, FileSystemLoader, select_autoescape


def create_contents_html(body: str) -> str:
    body_bytes = body.encode("utf-8")

    html_content = (
        b"{% extends 'base.html' %}\n"
        b"{% block content %}\n" + body_bytes + b"\n"
        b"{% endblock %}"
    )

    env = Environment(
        loader=FileSystemLoader(
            searchpath="src/content/resources/html_template"
        ),  # 템플릿 파일이 위치한 경로 설정
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.from_string(html_content.decode("utf-8"))
    return template.render()
