import rollbar
import streamlit as st

from app.common.log import logger


class RollbarService:
    @staticmethod
    def initialize():
        logger.info("[Rollbar] Initializing Rollbar...")
        
        rollbar.init(
            access_token=st.secrets["ROLLBAR_ACCESS_TOKEN"],
            environment=st.secrets["STREAMLIT_ENV"],
        )
        
        logger.info("[Rollbar] Rollbar Initialized!")
