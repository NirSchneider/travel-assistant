import os
from jinja2 import Environment, FileSystemLoader
from app.consts.roles import MessageRole


def _get_jinja_env():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.dirname(current_dir)
    
    return Environment(loader=FileSystemLoader(prompts_dir))


def render_template(template_name: str, **kwargs) -> str:
    env = _get_jinja_env()
    template = env.get_template(template_name)
    return template.render(**kwargs)


def build_system_message() -> dict:
    system_prompt_content = render_template("system_prompt.j2")
    
    return {
        "role": MessageRole.SYSTEM,
        "content": system_prompt_content
    }
