"""Streamlit entry point; importing this file cannot spawn request workers."""

from census_web.app import main

if __name__ == "__main__":
    main()
