"""Domain resource endpoints illustrating clean architecture separation."""

from contracts.models import PaginatedResponse, StandardResponse
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter()


class ResourceItem(BaseModel):
    id: str
    name: str
    description: str
    status: str = "active"


class CreateResourceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)


mock_db: list[ResourceItem] = [
    ResourceItem(id="res-1", name="Core Engine", description="Computation and rules pipeline"),
    ResourceItem(id="res-2", name="Event Gateway", description="Distributed async broker"),
]


@router.get("", response_model=StandardResponse[PaginatedResponse[ResourceItem]])
async def list_resources(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> StandardResponse[PaginatedResponse[ResourceItem]]:
    total = len(mock_db)
    paginated = PaginatedResponse[ResourceItem](
        items=mock_db,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1,
    )
    return StandardResponse[PaginatedResponse[ResourceItem]](success=True, data=paginated)


@router.post("", response_model=StandardResponse[ResourceItem], status_code=201)
async def create_resource(payload: CreateResourceRequest) -> StandardResponse[ResourceItem]:
    item = ResourceItem(
        id=f"res-{len(mock_db) + 1}",
        name=payload.name,
        description=payload.description,
    )
    mock_db.append(item)
    return StandardResponse[ResourceItem](success=True, data=item, message="Resource created")
