import os
import argparse
from skill_converter import BioinfoSkillConverter
from pathlib import Path


def convert_skill(tool_name, manual, run_help_command, model="openai",
                  author="BioinfoMCP", license_name="BSD-3-Clause"):
    """Run the skill converter with retry logic."""
    converter = BioinfoSkillConverter(model=model, author=author, license_name=license_name)

    result = converter.autogenerate_skill(tool_name, manual, run_help_command)

    while not result[0]:
        if result[2] is None or not any(result[2].values()):
            # No usable content at all, regenerate from scratch
            print(f"[Retry] No content found, regenerating...")
            result = converter.autogenerate_skill(tool_name, manual, run_help_command)
        else:
            # Has partial content, refine based on error
            print(f"[Retry] Refining: {result[1]}")
            result = converter.refine_after_feedback(
                tool_name, contents=result[2], error_message=result[1]
            )

    return result[2]


def write_skill_files(tool_name, contents, output_dir):
    """Write the skill package files to disk."""
    skill_dir = Path(output_dir) / tool_name
    refs_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"

    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(refs_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    # Write SKILL.md
    with open(skill_dir / "SKILL.md", "w") as f:
        f.write(contents["skill_md"])
    print(f"  Written: {skill_dir / 'SKILL.md'}")

    # Write reference document
    with open(refs_dir / f"{tool_name}_reference.md", "w") as f:
        f.write(contents["reference_md"])
    print(f"  Written: {refs_dir / f'{tool_name}_reference.md'}")

    # Write example script (only if non-empty)
    if contents["example_script"] and contents["example_script"].strip():
        with open(scripts_dir / f"{tool_name}_example.py", "w") as f:
            f.write(contents["example_script"])
        print(f"  Written: {scripts_dir / f'{tool_name}_example.py'}")

    return skill_dir


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert bioinformatics tool documentation into Claude Scientific Skills"
    )
    parser.add_argument('--name', type=str, required=True,
                        help="Tool name (e.g., qiime_tools_import)")
    parser.add_argument('--manual', type=str, required=True,
                        help="Path to help document (PDF or MD file)")
    parser.add_argument('--run_help_command', type=bool, default=False,
                        help="Run help command instead of reading document")
    parser.add_argument('--output_location', type=str, default='./skills/',
                        help="Output directory for generated skills")
    parser.add_argument('--model', type=str, default='openai',
                        choices=['openai', 'azure', 'gemini'],
                        help="LLM backend to use (default: openai)")
    parser.add_argument('--author', type=str, default='BioinfoMCP',
                        help="Skill author name for YAML frontmatter")
    parser.add_argument('--license', type=str, default='BSD-3-Clause',
                        help="License for YAML frontmatter")
    args = parser.parse_args()

    print(f"{'=='*30}")
    print(f"Generating Claude Scientific Skill for: {args.name}")
    print(f"Manual: {args.manual}")
    print(f"Output: {args.output_location}")
    print(f"Model: {args.model}")
    print(f"{'=='*30}")

    # Run conversion
    contents = convert_skill(
        args.name, args.manual, args.run_help_command,
        model=args.model, author=args.author, license_name=args.license
    )

    # Write output files
    skill_dir = write_skill_files(args.name, contents, args.output_location)

    print(f"\n{'=='*30}")
    print(f"SUCCESS: Skill generated at {skill_dir}")
    print(f"  - SKILL.md")
    print(f"  - references/{args.name}_reference.md")
    if contents["example_script"] and contents["example_script"].strip():
        print(f"  - scripts/{args.name}_example.py")
    print(f"{'=='*30}")
