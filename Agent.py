from dotenv import load_dotenv
from google import genai
from pathlib import Path
import json

load_dotenv()

client = genai.Client()
def analyze_repository():

    repo_folder = Path("REPODATA")
    files = []

    for file in repo_folder.rglob("*"):

        if not file.is_file():
            continue

        if file.name in [".env", ".gitignore"] or file.suffix in [".md", ".csv"]:
            continue

        if ".git" in file.parts:
            continue

        try:
            content = file.read_text(encoding="utf-8")
        
            files.append(
                f"""FILE: {file.relative_to(repo_folder)}
{content}"""
            )

        except UnicodeDecodeError:
            continue

    repository = "\n\n".join(files)

    prompt = f"""
Analyze this GitHub repository.

Do not invent information.
Only report information directly supported by the repository files.

Explain:
1. The architecture
2. The main files
3. How the components communicate
4. The main flow of the application

Repository:

{repository}
"""

    interaction = client.interactions.create(
        agent="antigravity-preview-09-2026",
        input=prompt,
        environment="remote",
    )

    output_folder = Path("REPOJSON")
    output_folder.mkdir(exist_ok=True)

    repo_name = repo_folder.name
    output_file = output_folder / f"{repo_name}.json"

    data = {
        "repository": repo_name,
        "analysis": interaction.output_text
    }

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_file