import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
import tomli
import tomli_w


def prompt_with_default(prompt: str, default: str) -> str:
    """Prompt for input with a default value."""
    response = input(f"{prompt} [{default}]: ").strip()
    return response if response else default


def get_git_config(key: str) -> Optional[str]:
    """Get git config value."""
    try:
        return subprocess.check_output(
            ["git", "config", "user."+key], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return None


def update_pyproject_toml(
    project_name: str,
    project_description: str,
    author_name: str,
    author_email: str
) -> None:
    """Update pyproject.toml with new project information."""
    pyproject_path = Path("pyproject.toml")
    
    # Read existing toml
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)
    
    # Update project information
    config["project"]["name"] = project_name
    config["project"]["description"] = project_description
    config["project"]["authors"] = [
        {"name": author_name, "email": author_email}
    ]
    
    # Write updated toml
    with open(pyproject_path, "wb") as f:
        tomli_w.dump(config, f)


def run_command(command: str) -> None:
    """Run a shell command and exit if it fails."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        sys.exit(1)


def main() -> None:
    print("🚀 Initializing new Python project...")

    # Get project information
    project_name = prompt_with_default(
        "Project name", "my-python-project"
    )
    project_description = prompt_with_default(
        "Project description", "A Python project"
    )
    author_name = prompt_with_default(
        "Author name", get_git_config("name") or "Your Name"
    )
    author_email = prompt_with_default(
        "Author email", get_git_config("email") or "your.email@example.com"
    )

    # Handle example code
    code_choice = prompt_with_default(
        "How would you like to handle example code?\n"
        "1. Keep example code (useful for reference)\n"
        "2. Create minimal placeholder test (ensures checks pass)\n"
        "3. Remove all example code (clean slate)\n"
        "Choose option", "1"
    )

    if code_choice == "2":
        print("📝 Creating minimal placeholder test...")
        # Create minimal src module
        with open("src/example.py", "w") as f:
            f.write("""def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
""")
        
        # Create minimal test
        with open("tests/test_example.py", "w") as f:
            f.write("""from src.example import add

def test_add():
    assert add(1, 2) == 3
""")
    elif code_choice == "3":
        print("🧹 Removing all example code...")
        run_command("make clean-example")
    else:
        print("📚 Keeping example code for reference...")

    # Update pyproject.toml
    print("📝 Updating project configuration...")
    update_pyproject_toml(
        project_name,
        project_description,
        author_name,
        author_email
    )

    # Get current directory name and handle renaming
    current_dir = os.path.basename(os.getcwd())
    if current_dir == "python-collab-template" or current_dir == "python-project-test":
        parent_dir = os.path.dirname(os.getcwd())
        new_dir = os.path.join(parent_dir, project_name)
        print(f"📁 Renaming project directory to {project_name}...")
        if os.path.exists(new_dir):
            print(f"⚠️  Directory {project_name} already exists. Keeping current directory name.")
        else:
            os.chdir(parent_dir)
            os.rename(current_dir, project_name)
            os.chdir(project_name)

    # Install dependencies and set up environment
    print("🔨 Setting up development environment...")
    run_command("make setup")

    # Configure pre-commit hooks
    precommit_choice = prompt_with_default(
        "\nWould you like to enable pre-commit hooks?\n"
        "These hooks run automatically before each commit to ensure code quality:\n"
        "- Type checking (mypy)\n"
        "- Linting (ruff)\n"
        "- Formatting (ruff)\n"
        "- Tests (pytest)\n"
        "\nEnable pre-commit hooks? (y/n)", "y"
    )
    
    # Initialize new git repository
    print("🔄 Initializing git repository...")
    if os.path.exists(".git"):
        run_command("rm -rf .git")
    run_command("git init")
    
    if precommit_choice.lower() in ('y', 'yes'):
        print("🔧 Setting up pre-commit hooks...")
        run_command("uv run pre-commit install")
    else:
        print("⏩ Skipping pre-commit hooks setup")

    # Initial commit
    run_command("git add .")
    run_command('git commit -m "feat: Initial project setup"')

    print("✨ Project initialized successfully!")
    print("""
Next steps:
1. Update README.md with your project details
2. Review and update CHANGELOG.md
3. Start adding your code in src/
4. Run 'make check' to verify everything works

Happy coding! 🎉
""")


if __name__ == "__main__":
    main()
