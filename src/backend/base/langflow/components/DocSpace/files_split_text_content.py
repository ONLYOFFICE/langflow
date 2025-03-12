from typing import Dict, Any, List
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document

from langflow.custom import Component
from langflow.io import DataInput, IntInput, MessageTextInput, Output
from langflow.schema import Data, Message


class SplitTextToDocumentsComponent(Component):
    display_name: str = "Split Text to Documents"
    description: str = "Split text into chunks based on specified criteria."
    icon = "scissors-line-dashed"
    name = "SplitTextToDocuments"

    inputs = [
        DataInput(
            name="data_inputs",
            display_name="Input Content",
            info="The content to split.",
            required=True,
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="Number of characters to overlap between chunks.",
            value=200,
        ),
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info="The maximum number of characters in each chunk.",
            value=1000,
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info="The character to split on. Defaults to newline.",
            value="\n",
        ),
    ]

    outputs = [
        Output(display_name="Documents", name="documents", method="split_text"),
    ]

    def split_text(self) -> Data:
        """Split text content into chunks using CharacterTextSplitter.

        Returns:
            Data object containing list of Document objects with chunked content.
        """
        try:
            data_input = self.data_inputs
            if not isinstance(data_input, Data) or not data_input.data:
                return Data(data={"documents": []})

            files: List[Dict[str, Any]] = data_input.data.get("files", [])
            if not files:
                return Data(data={"documents": []})

            splitter = CharacterTextSplitter(
                chunk_overlap=self.chunk_overlap,
                chunk_size=self.chunk_size,
                separator=self.separator,
            )

            all_docs = {}

            for file in files:
                try:
                    text = file.get('text')
                    if not text:
                        print(
                            f"No text content found in file {file.get('id', 'unknown')}")
                        continue

                    metadata = {
                        "version": file.get('version', ''),
                        "title": file.get('title', ''),
                        "id": file.get('id', ''),
                        "extension": file.get('extension', '')
                    }

                    # Split the text into chunks
                    chunks = splitter.split_text(text)

                    # Create Document objects for each chunk
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                **metadata,
                                "page": i,
                                "total_pages": len(chunks)
                            }
                        )
                        all_docs[f'doc-{doc.metadata["id"]}-{i}'] = doc

                except Exception as e:
                    print(
                        f"Error processing file {file.get('id', 'unknown')}: {str(e)}")
                    continue

            return Data(data=all_docs)

        except Exception as e:
            raise ValueError(f"Error splitting text: {str(e)}")
