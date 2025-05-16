# Introduction
This project is based on the code from the Deeplearning training class: [MCP: Build Rich-Context AI Apps with Anthropic](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic). 

The goal is to clean up the flow in the code with the following modifications
* Use value in `response.stop_reason` as the control of the flow, instead of checking to see if the response has only 1 text content.  This allows further error checking and should be easier to expand
* More explicit generate->tool use->generate loop by processing all the contents in the responses and create the complete user content for the next loop
* Ehanced the chat_loop() to remember the history for a smoother expeirence.  For example, the user can type "retrieve the third item for me please" and with the history the bot will know which one the user is referring to.

# Initialize
After cloning the project, the following command will help set up the environment
```
# Install uv if not already
brew install uv

# create local environment
uv venv
source .venv/bin/activate

# install packages
uv pip install .

# set up Anthropic API set
# create a file .env with the following content
ANTHROPIC_API_KEY=sk-ant-...<your API key from https://console.anthropic.com/settings/keys> 

# start chat bot
uv run chat.py
```
