import os
import subprocess
import re
import pymupdf
from pathlib import Path
from dotenv import load_dotenv
from skill_validator import validate_skill_md, validate_reference_md, validate_example_script

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / '.env')


class BioinfoSkillConverter():
    def __init__(self, model="openai", author="BioinfoMCP", license_name="BSD-3-Clause"):
        sys_prompt_path = Path(__file__).parent / 'system_prompt.txt'
        with open(sys_prompt_path, 'r') as f:
            self.sys_prompt = f.read()
        self.api_model_name = os.getenv('MODEL_NAME')
        self.author = author
        self.license_name = license_name

        if model == "azure":
            from openai import AzureOpenAI
            api_subscription_key = os.getenv('AZURE_OPENAI_KEY')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION')
            api_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            self.client = AzureOpenAI(
                api_version=api_version,
                azure_endpoint=api_endpoint,
                api_key=api_subscription_key,
            )

        elif model == "openai":
            from openai import OpenAI
            openai_api_key = os.getenv('OPENAI_API_KEY')
            self.client = OpenAI(
                api_key=openai_api_key
            )

        elif model == "gemini":
            from openai import OpenAI
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            self.client = OpenAI(
                api_key=gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

        print(f"Successfully created a {self.api_model_name} model")

    def is_tool_available(self, tool_name):
        """Check whether that tool is installed or not"""
        try:
            subprocess.run([tool_name, '--version'],
                           capture_output=True, timeout=20, text=True)
            print(f"{tool_name} is installed")
            return True
        except:
            print(f"{tool_name} is not installed!")
            return False

    def extract_help_document(self, tool_name, manual, run_help_command=False):
        """Extract help text from tool or document.

        Supports PDF files and markdown (.md) files.
        """
        if not run_help_command:
            manual_path = str(manual)
            if manual_path.lower().endswith('.md'):
                with open(manual_path, 'r') as f:
                    return f.read()
            else:
                doc = pymupdf.open(manual_path)
                manual_content = ""
                for page in doc:
                    text = page.get_text()
                    manual_content += text
                return manual_content

        if self.is_tool_available(tool_name):
            try:
                result = subprocess.run([tool_name, manual],
                                        capture_output=True, timeout=30, text=True)
                return result.stdout + result.stderr
            except:
                return None

    def generate_prompt(self, tool_name, help_docs):
        """Generate the prompt for Claude Scientific Skills generation."""
        prompt = f"""
Convert the following bioinformatics tool documentation into a Claude Scientific Skill package.

Tool Name: {tool_name}
Skill Author: {self.author}
License: {self.license_name}

Help Document:
{help_docs}

Generate the complete skill package with all three blocks:
1. ===SKILL.md=== - The full SKILL.md with YAML frontmatter and all required sections
2. ===REFERENCE.md=== - Comprehensive parameter reference
3. ===EXAMPLE_SCRIPT.py=== - A working Python example script

Make sure to extract ALL parameters and cover ALL subcommands from the documentation.
"""
        return prompt

    def parse_skill(self, llm_response):
        """Parse the LLM response into three skill components.

        Extracts content between ===SKILL.md===, ===REFERENCE.md===, and
        ===EXAMPLE_SCRIPT.py=== delimiters.

        Returns (success_int, error_message_or_none, dict_of_contents).
        """
        skill_md = ""
        reference_md = ""
        example_script = ""

        # Extract SKILL.md block
        skill_match = re.search(
            r'===SKILL\.md===(.*?)(?:===REFERENCE\.md===|$)',
            llm_response, re.DOTALL
        )
        if skill_match:
            skill_md = skill_match.group(1).strip()

        # Extract REFERENCE.md block
        ref_match = re.search(
            r'===REFERENCE\.md===(.*?)(?:===EXAMPLE_SCRIPT\.py===|$)',
            llm_response, re.DOTALL
        )
        if ref_match:
            reference_md = ref_match.group(1).strip()

        # Extract EXAMPLE_SCRIPT.py block
        script_match = re.search(
            r'===EXAMPLE_SCRIPT\.py===(.*?)$',
            llm_response, re.DOTALL
        )
        if script_match:
            example_script = script_match.group(1).strip()
            # Remove markdown code fences if present
            code_block = re.findall(r'```python\n(.*?)\n```', example_script, re.DOTALL)
            if code_block:
                example_script = code_block[0]

        contents = {
            "skill_md": skill_md,
            "reference_md": reference_md,
            "example_script": example_script,
        }

        # Validate each component
        ok, err = validate_skill_md(skill_md)
        if not ok:
            return (0, f"SKILL.md validation failed: {err}", contents)

        ok, err = validate_reference_md(reference_md)
        if not ok:
            return (0, f"Reference validation failed: {err}", contents)

        ok, err = validate_example_script(example_script)
        if not ok:
            return (0, f"Example script validation failed: {err}", contents)

        return (1, None, contents)

    def refine_after_feedback(self, tool_name, contents, error_message):
        """Request the LLM to fix errors in the generated skill."""
        existing = ""
        if contents.get("skill_md"):
            existing += f"===SKILL.md===\n{contents['skill_md']}\n\n"
        if contents.get("reference_md"):
            existing += f"===REFERENCE.md===\n{contents['reference_md']}\n\n"
        if contents.get("example_script"):
            existing += f"===EXAMPLE_SCRIPT.py===\n```python\n{contents['example_script']}\n```\n"

        prompt = f"""
The initial skill package for {tool_name}:

{existing}

contains the following error:
{error_message}

Please fix the content and ensure that:
1. SKILL.md has valid YAML frontmatter with name, description, license, context, metadata keys
2. SKILL.md contains ALL required sections: Overview, When to Use This Skill, Core Capabilities, Installation and Setup, Quick Start, Standard Workflow, Common Tasks, Key Parameters, Best Practices, Common Pitfalls, Additional Resources, Bundled Resources
3. SKILL.md contains at least one code block
4. Reference document is not empty and has headers
5. Example script (if present) has valid Python syntax

Provide the corrected output with all three blocks using the ===SKILL.md===, ===REFERENCE.md===, and ===EXAMPLE_SCRIPT.py=== delimiters.
"""
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.sys_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            model=self.api_model_name,
            temperature=0.1
        )
        response_content = response.choices[0].message.content
        return self.parse_skill(response_content)

    def autogenerate_skill(self, tool_name, manual, run_help_command):
        """Main entry point: generate a complete Claude Scientific Skill package."""
        help_docs = self.extract_help_document(tool_name, manual, run_help_command)
        prompt = self.generate_prompt(tool_name, help_docs)

        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.sys_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            temperature=0.1,
            model=self.api_model_name
        )
        response_content = response.choices[0].message.content
        return self.parse_skill(response_content)
