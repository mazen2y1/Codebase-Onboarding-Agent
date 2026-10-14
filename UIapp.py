import os
import shutil
import streamlit as st
from dotenv import load_dotenv
from APP import load_github_repo, load_uploaded_zip
from Agent import ask_repository
load_dotenv()

st.set_page_config(page_title="Codebase Onboarding Agent", page_icon="🧭", layout="wide")
st.title("Codebase Onboarding Agent")

def get_secret(name: str, default: str | None = None):
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return value or os.getenv(name, default)

api_key = get_secret("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
model_name = get_secret("GOOGLE_MODEL_NAME", os.getenv("GOOGLE_MODEL_NAME", "gemini-3-flash-preview"))

with st.sidebar:
    st.header("Load a repository")
    source_type = st.radio("Repository source", ["GitHub URL", "Upload ZIP"])

    if source_type == "GitHub URL":
        repo_url = st.text_input("Public GitHub repository URL", placeholder="https://github.com/owner/repository")
        if st.button("Load repository", type="primary", use_container_width=True):
            if not repo_url.strip():
                st.warning("Enter a GitHub URL first")
            else:
                try:
                    with st.spinner("Downloading repository"):
                        repo_root, repo_label = load_github_repo(repo_url)
                    old_root = st.session_state.get("repo_root")
                    if old_root and old_root != repo_root:
                        shutil.rmtree(os.path.dirname(old_root), ignore_errors=True)
                    st.session_state.repo_root = repo_root
                    st.session_state.repo_label = repo_label
                    st.session_state.messages = []
                    st.success("Repository loaded")
                except Exception as exc:
                    st.error(f"Could not load repository: {exc}")
    else:
        uploaded_zip = st.file_uploader("Upload repository ZIP", type=["zip"])
        if st.button("Load ZIP", type="primary", use_container_width=True):
            if uploaded_zip is None:
                st.warning("Choose a ZIP file first.")
            else:
                try:
                    with st.spinner("Extracting repository"):
                        repo_root, repo_label = load_uploaded_zip(uploaded_zip)
                    old_root = st.session_state.get("repo_root")
                    if old_root and old_root != repo_root:
                        shutil.rmtree(os.path.dirname(old_root), ignore_errors=True)
                    st.session_state.repo_root = repo_root
                    st.session_state.repo_label = repo_label
                    st.session_state.messages = []
                    st.success("Repository loaded")
                except Exception as exc:
                    st.error(f"Could not load ZIP: {exc}")

    st.divider()
    st.caption("Error")

if not api_key:
    st.warning("Add GOOGLE_API_KEY")

repo_root = st.session_state.get("repo_root")
if not repo_root or not os.path.isdir(repo_root):
    st.info("Load a repository from the sidebar to start asking questions.")
    st.stop()

st.success(f"Loaded repository: **{st.session_state.get('repo_label', 'Repository')}**")

with st.expander("Repository files", expanded=False):
    from tools.list_files import list_files
    try:
        file_items = list_files(repo_root, recursive=True)
        st.write(f"Showing {len(file_items)} entries (maximum 2,000).")
        st.code("\n".join(f"{'[DIR] ' if item['type'] == 'directory' else ''}{item['path']}" for item in file_items) or "No files found.")
    except Exception as exc:
        st.error(f"Could not list files: {exc}")

st.subheader("Ask about your code")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Example: How does authentication work?")
if question:
    if not api_key:
        st.error("Missing GOOGLE_API_KEY")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Exploring repository files"):
                try:
                    history = st.session_state.messages[:-1]
                    answer = ask_repository(
                        question=question,
                        repo_root=repo_root,
                        history=history,
                        api_key=api_key,
                        model_name=model_name,
                    )
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as exc:
                    st.error(f"The agent could not answer: {exc}")
                    st.session_state.messages.pop()
