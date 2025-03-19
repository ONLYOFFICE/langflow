from langflow.custom import Component
from langflow.io import DataInput, Output, MessageInput
from langflow.schema.message import Message

SYSTEM_PROMPT = """ 
You are a helpful assistant that can use tools to answer questions and perform tasks.
Inside input found title of documents or folders. Later your need use tools with this ids.
If name of folders or documents not available - do not use tools.
If you dont see file or folder from user question - just return user question.
If extensions is empty - it is folder. This folder can has subfolders or files 
from user query. Your asnwer ONLY id for file or files that ACCEPT USER.
File or folder ID or title MAY BE inside HISTORY with @ID.
@1 - is it file with id 1.
@folder-1 - is it folder with id 1.
Example: 1,2,3,4 
Without spaces. No need to use @.

List of available folders and documents:
{folders_and_documents}

HISTORY:
{memory}
"""


class SystemPromptComponent(Component):
    """
    Component that formats a system prompt with available folders and documents.
    Creates a structured prompt that instructs an AI assistant about available documents and folders.
    """

    display_name = "System Prompt"
    description = "Creates a system prompt that informs the AI assistant about available folders and documents."
    icon = "terminal"
    name = "SystemPrompt"

    inputs = [
        DataInput(
            name="document_context",
            display_name="Folders and Documents",
            info="List of available folders and documents to include in the system prompt",
            required=True,
        ),
        MessageInput(
            name="memory",
            display_name="Chat memory",
            info="Chat memory"
        )
    ]

    outputs = [
        Output(
            display_name="System Prompt",
            name="system_prompt",
            method="format_system_prompt",
        ),
    ]

    def format_system_prompt(self) -> Message:
        """
        Formats a system prompt with the provided folders and documents information.

        Returns:
            Message: A message containing the formatted system prompt
        """
        # Get the document context
        folders_and_documents = self.document_context.data.get("content", [])

        formated_content = "\n".join(
            f'Title: {str(item.get('title'))} id: {str(item.get('id'))} extension: {str(item.get('fileExst', ''))}' for item in folders_and_documents)

        # Format the system prompt template with the document context
        formatted_prompt = SYSTEM_PROMPT.format(
            folders_and_documents=formated_content,
            memory=self.memory.get_text()
        )

        # Create a new message with the formatted prompt
        # Preserve metadata from the document context message
        system_prompt_msg = Message(
            text=formatted_prompt,
        )

        return system_prompt_msg
