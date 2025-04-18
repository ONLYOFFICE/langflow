from typing import Any, Dict, List
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from qdrant_client.models import Filter
from langflow.custom import Component
from langflow.schema import Message
from langflow.io import (
    MessageInput,
    DataInput,
    Output,
)

from langflow.utils.qdrant import get_qdrant_client, check_collection_exists, create_collection, qdrant_inputs


class QdrantSearchFileComponent(Component):
    display_name = "Qdrant Search"
    description = "Search in Qdrant Vector Store"
    icon = "Qdrant"

    inputs = [
        *qdrant_inputs,
        MessageInput(
            name="question",
            display_name="Question",
        ),
        DataInput(
            name="folder",
            display_name="Folder",
        ),
    ]

    outputs = [
        Output(name="search",
               display_name="Search",
               method="search_documents"),
    ]

    def build_vector_store(self) -> Qdrant:
        try:
            collection_name: str = self.collection_name.get_text()
            embedding: Embeddings = self.embedding

            client = get_qdrant_client(
                self.qdrant_host.get_text(), self.qdrant_port.get_text())

            if not check_collection_exists(client, collection_name):
                # Get vector size from first document
                doc = Document(page_content='content for vectorize',
                               metadata={**self.metadata.data})
                vector = embedding.embed_query(doc.page_content)
                vector_size = len(vector)

                create_collection(
                    client, collection_name, vector_size)

            qdrant = Qdrant(client=client,
                            embeddings=embedding,
                            collection_name=collection_name)

            return qdrant

        except Exception as e:
            raise Exception(f"Error building vector store: {str(e)}")

    def search_documents(self) -> Message:

        folder_id: str = self.folder.data.get('id', 'unknown')

        if not folder_id:
            return Message(text="No folder id provided")

        question: str = self.question.get_text()

        if not question:
            return Message(text="No question provided")

        qdrant = self.build_vector_store()

        if not qdrant:
            return Message(text="Folder not found")

        filter: Filter = {"key": "metadata.folderId", "match": {
            "value": folder_id
        }}

        docs = qdrant.similarity_search(
            query=question,
            k=10,
            filter=filter
        )

        return Message(text="\n".join(f'{item.metadata.get('id')}:{item.metadata.get('title')}\n{item.page_content}\n\n' for item in docs))
