from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    BooleanMixin,
    Component,
    CreateFileOptions,
    DataOutput,
    ErrorResponse,
    FolderIdInput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

NAME_ENABLE_EXTERNAL_EXT = "enable_external_ext"
DESCRIPTION_FOLDER_ID = "The ID of the folder to create the file in."
DESCRIPTION_TITLE = "The title of the file to create."
DESCRIPTION_TEMPLATE_ID = "The ID of the template to use for the file."
DESCRIPTION_FORM_ID = "The ID of the form to use for the file."
DESCRIPTION_ENABLE_EXTERNAL_EXT = "Enable external extensions for the file."
DESCRIPTION_COMPONENT = "Create a new file in the specified folder in ONLYOFFICE DocSpace."


class OnlyofficeDocspaceCreateFile(Component, BooleanMixin):
    display_name = "Create File"
    description = DESCRIPTION_COMPONENT
    name = "OnlyofficeDocspaceCreateFile"


    inputs = [
        AuthTextInput(),
        FolderIdInput(info=DESCRIPTION_FOLDER_ID),
        MessageTextInput(
            name="title",
            display_name="Title",
            info=DESCRIPTION_TITLE,
        ),
        MessageTextInput(
            name="template_id",
            display_name="Template ID",
            info=DESCRIPTION_TEMPLATE_ID,
            required=False,
        ),
        MessageTextInput(
            name="form_id",
            display_name="Form ID",
            info=DESCRIPTION_FORM_ID,
            required=False,
        ),
        MessageTextInput(
            name=NAME_ENABLE_EXTERNAL_EXT,
            display_name="Enable External Ext",
            info=DESCRIPTION_ENABLE_EXTERNAL_EXT,
            required=False,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        folder_id: int = Field(..., description=DESCRIPTION_FOLDER_ID)
        title: str = Field(..., description=DESCRIPTION_TITLE)
        template_id: int | None = Field(None, description=DESCRIPTION_TEMPLATE_ID)
        form_id: int | None = Field(None, description=DESCRIPTION_FORM_ID)
        enable_external_ext: bool | None = Field(None, description=DESCRIPTION_ENABLE_EXTERNAL_EXT)


    def _create_schema(self) -> Schema:
        template_id: int | None = None
        if self.template_id:
            template_id = self.template_id

        form_id: int | None = None
        if self.form_id:
            form_id = self.form_id

        enable_external_ext = self.boolean(NAME_ENABLE_EXTERNAL_EXT)

        return self.Schema(
            folder_id=self.folder_id,
            title=self.title,
            template_id=template_id,
            form_id=form_id,
            enable_external_ext=enable_external_ext,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._create_file(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_create_file",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._create_file(schema)


    async def _create_file(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = CreateFileOptions(
            title=schema.title,
            templateId=schema.template_id,
            formId=schema.form_id,
            enableExternalExt=schema.enable_external_ext,
        )
        result, response = client.files.create_file(schema.folder_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
