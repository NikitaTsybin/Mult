import pandas
import streamlit
import streamlit.web.cli as stcli
import sys
if __name__ == "__main__":
    sys.argv=["streamlit", "run", "moments.py"]
    sys.exit(stcli.main())
