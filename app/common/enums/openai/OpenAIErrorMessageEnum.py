import openai


OPENAI_ERROR_MESSAGE_ENUM = {
    openai.APIError: "OpenAI API returned an API Error.",
    openai.AuthenticationError: "OpenAI API returned an Authentication Error.",
    openai.APIConnectionError: "OpenAI API returned an API Connection Error.",
    openai.BadRequestError: "OpenAI API returned a Bad Request Error.",
    openai.InternalServerError: "OpenAI API returned an Internal Server Error.",
    openai.NotFoundError: "OpenAI API returned a Not Found Error.",
    openai.UnprocessableEntityError: "OpenAI API returned an Unprocessable Entity Error.",
    openai.RateLimitError: "OpenAI API returned a Rate Limit Error.",
    openai.Timeout: "OpenAI API returned a Timeout.",
}
