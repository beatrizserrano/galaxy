"""
API operations on the contents of a history dataset.
"""
import logging
from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
)

from fastapi import (
    Body,
    Depends,
    Path,
    Query,
    Request,
)
from starlette.responses import (
    FileResponse,
    StreamingResponse,
)

from galaxy.schema import (
    FilterQueryParams,
    SerializationParams,
)
from galaxy.schema.fields import EncodedDatabaseIdField
from galaxy.schema.schema import (
    AnyHDA,
    AnyHistoryContentItem,
    DatasetAssociationRoles,
    DatasetSourceType,
    UpdateDatasetPermissionsPayload,
)
from galaxy.webapps.galaxy.api.common import (
    get_filter_query_params,
    get_query_parameters_from_request_excluding,
    get_update_permission_payload,
    query_serialization_params,
)
from galaxy.webapps.galaxy.services.datasets import (
    ConvertedDatasetsMap,
    DatasetInheritanceChain,
    DatasetsService,
    DatasetStorageDetails,
    DatasetTextContentDetails,
    RequestDataType,
)
from . import (
    depends,
    DependsOnTrans,
    Router,
)

log = logging.getLogger(__name__)

router = Router(tags=["datasets"])

DatasetIDPathParam: EncodedDatabaseIdField = Path(..., description="The encoded database identifier of the dataset.")

HistoryIDPathParam: EncodedDatabaseIdField = Path(..., description="The encoded database identifier of the History.")

DatasetSourceQueryParam: DatasetSourceType = Query(
    default=DatasetSourceType.hda,
    description="Whether this dataset belongs to a history (HDA) or a library (LDDA).",
)


@router.cbv
class FastAPIDatasets:
    service: DatasetsService = depends(DatasetsService)

    @router.get(
        "/api/datasets",
        summary="Search datasets or collections using a query system.",
    )
    def index(
        self,
        trans=DependsOnTrans,
        history_id: Optional[EncodedDatabaseIdField] = Query(
            default=None,
            description="Optional identifier of a History. Use it to restrict the search whithin a particular History.",
        ),
        serialization_params: SerializationParams = Depends(query_serialization_params),
        filter_query_params: FilterQueryParams = Depends(get_filter_query_params),
    ) -> List[AnyHistoryContentItem]:
        return self.service.index(trans, history_id, serialization_params, filter_query_params)

    @router.get(
        "/api/datasets/{dataset_id}/storage",
        summary="Display user-facing storage details related to the objectstore a dataset resides in.",
    )
    def show_storage(
        self,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
        hda_ldda: DatasetSourceType = DatasetSourceQueryParam,
    ) -> DatasetStorageDetails:
        return self.service.show_storage(trans, dataset_id, hda_ldda)

    @router.get(
        "/api/datasets/{dataset_id}/inheritance_chain",
        summary="For internal use, this endpoint may change without warning.",
        include_in_schema=True,  # Can be changed to False if we don't really want to expose this
    )
    def show_inheritance_chain(
        self,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
        hda_ldda: DatasetSourceType = DatasetSourceQueryParam,
    ) -> DatasetInheritanceChain:
        return self.service.show_inheritance_chain(trans, dataset_id, hda_ldda)

    @router.get(
        "/api/datasets/{dataset_id}/get_content_as_text",
        summary="Returns dataset content as Text.",
    )
    def get_content_as_text(
        self,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
    ) -> DatasetTextContentDetails:
        return self.service.get_content_as_text(trans, dataset_id)

    @router.get(
        "/api/datasets/{dataset_id}/converted/{ext}",
        summary="Return information about datasets made by converting this dataset to a new format.",
    )
    def converted_ext(
        self,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
        ext: str = Path(
            ...,
            description="File extension of the new format to convert this dataset to.",
        ),
        serialization_params: SerializationParams = Depends(query_serialization_params),
    ) -> AnyHDA:
        """
        Return information about datasets made by converting this dataset to a new format.

        If there is no existing converted dataset for the format in `ext`, one will be created.

        **Note**: `view` and `keys` are also available to control the serialization of the dataset.
        """
        return self.service.converted_ext(trans, dataset_id, ext, serialization_params)

    @router.get(
        "/api/datasets/{dataset_id}/converted",
        summary=("Return a a map with all the existing converted datasets associated with this instance."),
    )
    def converted(
        self,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
    ) -> ConvertedDatasetsMap:
        """
        Return a map of `<converted extension> : <converted id>` containing all the *existing* converted datasets.
        """
        return self.service.converted(trans, dataset_id)

    @router.put(
        "/api/datasets/{dataset_id}/permissions",
        summary="Set permissions of the given history dataset to the given role ids.",
    )
    def update_permissions(
        self,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
        # Using a generic Dict here as an attempt on supporting multiple aliases for the permissions params.
        payload: Dict[str, Any] = Body(
            default=...,
            example=UpdateDatasetPermissionsPayload(),
        ),
    ) -> DatasetAssociationRoles:
        """Set permissions of the given history dataset to the given role ids."""
        update_payload = get_update_permission_payload(payload)
        return self.service.update_permissions(trans, dataset_id, update_payload)

    @router.get(
        "/api/histories/{history_id}/contents/{history_content_id}/extra_files",
        summary="Generate list of extra files.",
        tags=["histories"],
    )
    def extra_files(
        self,
        trans=DependsOnTrans,
        history_id: EncodedDatabaseIdField = HistoryIDPathParam,
        history_content_id: EncodedDatabaseIdField = DatasetIDPathParam,
    ):
        return self.service.extra_files(trans, history_content_id)

    @router.get(
        "/api/histories/{history_id}/contents/{history_content_id}/display",
        name="history_contents_display",
        summary="Displays dataset (preview) content.",
        tags=["histories"],
        response_class=StreamingResponse,
    )
    def display(
        self,
        request: Request,
        trans=DependsOnTrans,
        history_id: EncodedDatabaseIdField = HistoryIDPathParam,
        history_content_id: EncodedDatabaseIdField = DatasetIDPathParam,
        preview: bool = Query(
            default=False,
            description=(
                "Whether to get preview contents to be directly displayed on the web. "
                "If preview is False (default) the contents will be downloaded instead."
            ),
        ),
        filename: Optional[str] = Query(
            default=None,
            description="TODO",
        ),
        to_ext: Optional[str] = Query(
            default=None,
            description=(
                "The file extension when downloading the display data. Use the value `data` to "
                "let the server infer it from the data type."
            ),
        ),
        raw: bool = Query(
            default=False,
            description=(
                "The query parameter 'raw' should be considered experimental and may be dropped at "
                "some point in the future without warning. Generally, data should be processed by its "
                "datatype prior to display."
            ),
        ),
    ):
        """Streams the preview contents of a dataset to be displayed in a browser."""
        extra_params = get_query_parameters_from_request_excluding(request, {"preview", "filename", "to_ext", "raw"})
        display_data, headers = self.service.display(
            trans, history_content_id, history_id, preview, filename, to_ext, raw, **extra_params
        )
        return StreamingResponse(display_data, headers=headers)

    @router.get(
        "/api/histories/{history_id}/contents/{history_content_id}/metadata_file",
        summary="Returns the metadata file associated with this history item.",
        tags=["histories"],
        response_class=FileResponse,
    )
    def get_metadata_file(
        self,
        trans=DependsOnTrans,
        history_id: EncodedDatabaseIdField = HistoryIDPathParam,
        history_content_id: EncodedDatabaseIdField = DatasetIDPathParam,
        metadata_file: str = Query(
            ...,
            description="The name of the metadata file to retrieve.",
        ),
    ):
        metadata_file_path, headers = self.service.get_metadata_file(trans, history_content_id, metadata_file)
        return FileResponse(path=cast(str, metadata_file_path), headers=headers)

    @router.get(
        "/api/datasets/{dataset_id}",
        summary="Displays information about and/or content of a dataset.",
    )
    def show(
        self,
        request: Request,
        trans=DependsOnTrans,
        dataset_id: EncodedDatabaseIdField = DatasetIDPathParam,
        hda_ldda: DatasetSourceType = Query(
            default=DatasetSourceType.hda,
            description=("The type of information about the dataset to be requested."),
        ),
        data_type: Optional[RequestDataType] = Query(
            default=None,
            description=(
                "The type of information about the dataset to be requested. "
                "Each of these values may require additional parameters in the request and "
                "may return different responses."
            ),
        ),
        serialization_params: SerializationParams = Depends(query_serialization_params),
    ):
        """
        **Note**: Due to the multipurpose nature of this endpoint, which can receive a wild variety of parameters
        and return different kinds of responses, the documentation here will be limited.
        To get more information please check the source code.
        """
        exclude_params = {"hda_ldda", "data_type"}
        exclude_params.update(SerializationParams.__fields__.keys())
        extra_params = get_query_parameters_from_request_excluding(request, exclude_params)

        return self.service.show(trans, dataset_id, hda_ldda, serialization_params, data_type, **extra_params)
