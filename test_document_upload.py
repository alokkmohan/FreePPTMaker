import streamlit as st
from document_upload_component import document_upload_component

def main():
    st.title("Test: Document Upload Component")
    file_name, file_content = document_upload_component()
    if file_name:
        st.success(f"Uploaded: {file_name}")
        st.write(f"File size: {len(file_content)} bytes")
        if file_name.endswith('.txt'):
            st.text_area("Preview", file_content.decode('utf-8')[:500], height=200)
        else:
            st.info("Preview only available for .txt files.")
    else:
        st.info("No file uploaded yet.")

if __name__ == "__main__":
    main()
