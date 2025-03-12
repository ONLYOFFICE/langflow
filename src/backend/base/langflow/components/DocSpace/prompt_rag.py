from langflow.custom import Component
from langflow.io import MessageInput, Output
from langflow.schema.message import Message

RAG_PROMPT = """ 
DOCUMENTS:
{document}

INSTRUCTIONS:
Answer the users QUESTION using the DOCUMENTS text above.
Keep your answer ground in the facts of the DOCUMENTS.
If the DOCUMENTS doesn't contain the facts to answer the QUESTION return 'Not known'
"""


class RagPromptComponent(Component):
    """
    Component that formats a RAG prompt with document context.
    Creates a structured prompt for retrieval-augmented generation.
    """

    display_name = "RAG Prompt"
    description = "Creates a structured RAG prompt with document context for retrieval-augmented generation."
    icon = "file-text"
    name = "RagPrompt"

    inputs = [
        MessageInput(
            name="document_context",
            display_name="Document context",
            info="The context of the document to combine with others",
            required=True,
        ),
    ]

    outputs = [
        Output(
            display_name="RAG Prompt",
            name="rag_prompt",
            method="format_rag_prompt",
        ),
    ]

    def format_rag_prompt(self) -> Message:
        """
        Formats a RAG prompt with the provided document context.

        Returns:
            Message: A message containing the formatted RAG prompt
        """
        # Get the document context
        doc_msg = self.document_context
        document_content = doc_msg.get_text() if doc_msg else ""

        # Format the RAG prompt template with the document context
        formatted_prompt = RAG_PROMPT.format(document=document_content)

        # Create a new message with the formatted prompt
        # Preserve metadata from the document context message
        rag_prompt_msg = Message(
            text=formatted_prompt,
            sender=doc_msg.sender if doc_msg else None,
            sender_name=doc_msg.sender_name if doc_msg else None,
            session_id=doc_msg.session_id if doc_msg else None,
            flow_id=doc_msg.flow_id if doc_msg else None,
        )

        return rag_prompt_msg
