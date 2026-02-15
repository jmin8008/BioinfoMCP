import ast
import re


REQUIRED_SECTIONS = [
    "Overview",
    "When to Use This Skill",
    "Core Capabilities",
    "Installation and Setup",
    "Quick Start",
    "Standard Workflow",
    "Common Tasks",
    "Key Parameters",
    "Best Practices",
    "Common Pitfalls",
    "Additional Resources",
    "Bundled Resources",
]

REQUIRED_FRONTMATTER_KEYS = ["name", "description", "license", "context", "metadata"]


def validate_skill_md(content):
    """Validate SKILL.md content.

    Returns (1, None) on success, (0, error_message) on failure.
    """
    if not content or not content.strip():
        return (0, "SKILL.md content is empty")

    # Check YAML frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return (0, "SKILL.md is missing YAML frontmatter (--- delimiters)")

    frontmatter_text = fm_match.group(1)

    # Check required frontmatter keys
    for key in REQUIRED_FRONTMATTER_KEYS:
        if f"{key}:" not in frontmatter_text:
            return (0, f"YAML frontmatter is missing required key: {key}")

    # Check required section headers
    for section in REQUIRED_SECTIONS:
        pattern = rf'#\s+{re.escape(section)}'
        if not re.search(pattern, content):
            return (0, f"SKILL.md is missing required section: '# {section}'")

    # Check that at least one code block exists
    if '```' not in content:
        return (0, "SKILL.md has no code blocks")

    return (1, None)


def validate_reference_md(content):
    """Validate reference markdown content.

    Returns (1, None) on success, (0, error_message) on failure.
    """
    if not content or not content.strip():
        return (0, "Reference document is empty")

    # Check that at least one header exists
    if not re.search(r'^#+\s+', content, re.MULTILINE):
        return (0, "Reference document has no headers")

    return (1, None)


def validate_example_script(content):
    """Validate example Python script.

    Empty content is acceptable (tool may not need an example script).
    If content exists, validate Python syntax with ast.parse().

    Returns (1, None) on success, (0, error_message) on failure.
    """
    if not content or not content.strip():
        return (1, None)

    try:
        ast.parse(content)
    except SyntaxError as e:
        return (0, f"Example script has SyntaxError: {e}")

    return (1, None)
