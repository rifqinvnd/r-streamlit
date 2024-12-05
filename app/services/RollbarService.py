import rollbar
import streamlit as st

from app.common.log import logger


class RollbarService:
    @staticmethod
    def initialize():
        logger.info("[Rollbar] Initializing Rollbar...")
        
        rollbar.init(
            access_token='f8edea8a1a304fce90dbb9704df9771a',
            environment=st.secrets["STREAMLIT_ENV"],
        )
        
        logger.info("[Rollbar] Rollbar Initialized!")
