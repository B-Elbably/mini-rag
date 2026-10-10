from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
import aiofiles
from models import ResponseSignal
import logging
from .schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemas import DataChunk

logger = logging.getLogger('uvicorn.error')

base_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@base_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings),
):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_upload_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal}
        )
    # project_dir_path = ProjectController().get_project_path(project_id)
    file_path, file_id = data_controller.generate_unique_filename(original_filename=file.filename, project_id=project_id)
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": file_id,
            "project_id": str(project.id),
        }

    )

@base_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    if file_content is None:
        logger.warning(
            "Processing failed: file '%s' was not found or has an unsupported extension "
            "for project '%s'",
            file_id,
            project_id,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value,
                "detail": "file_id must be the complete uploaded filename, including its extension",
            }
        )

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        logger.warning(
            "Processing failed: file '%s' produced no chunks for project '%s'",
            file_id,
            project_id,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value,
                "detail": (
                    "the file contains no extractable text; "
                    "use a text-based PDF or run OCR on this scanned PDF"
                ),
            }
        )

    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    if do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "no_records": no_records,
        }
    )