import streamlit as st
from APP import clone_repo
from Agent import analyze_repository
from TextAgent import explain_repository

st.set_page_config(
    page_title="Codebase Onboarding Agent",
    layout="wide"
)

st.title("Codebase Onboarding Agent")

st.write(
    "Enter a GitHub repository URL and let the AI analyze its architecture (WORKING WITH SMALL REPOS)"
)

st.write("By: https://github.com/mazen2y1")
repo_link = st.text_input(
    "GitHub Repository URL : ",
    placeholder="https://github.com/username/repository"
)

if st.button("Analyze Repository", type="primary"):

    if not repo_link:
        st.warning("Please enter a GitHub repository URL.")
    else:
        try:
            with st.spinner("Cloning repository..."):
                clone_repo(repo_link)
            with st.spinner("Analyzing repository..."):
                output_file = analyze_repository()
            with st.spinner("Generating explanation..."):
                explanation = explain_repository(output_file)

            st.success("Analysis completed successfully!")
            st.divider()
            st.header("Repository Explanation")
            st.markdown(explanation)
            st.divider()
        except Exception as e:
            st.error(f"Error: {e}")