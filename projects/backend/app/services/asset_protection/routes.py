"""
API routes for Asset Protection endpoints.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from .asset_protection_service import get_asset_protection_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/asset-protection", tags=["asset-protection"])


# ==================== Request Models ====================

class ProtectUrlRequest(BaseModel):
    """Request for protecting a URL-based asset."""
    url: str = Field(..., description="URL of the asset to protect")
    asset_name: str = Field(..., description="Name/description of the asset")
    asset_type: str = Field(..., description="Type: certificate, document, image, credit_file, other")
    owner_address: str = Field(..., description="Algorand address of the asset owner")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class VerifyAssetRequest(BaseModel):
    """Request for verifying an asset."""
    content_hash: str = Field(..., description="Hash of the asset to verify")


# ==================== Endpoints ====================

@router.post("/protect/url")
async def protect_url_asset(request: ProtectUrlRequest) -> Dict[str, Any]:
    """
    Protect a URL-based asset by registering on Algorand blockchain.
    
    This endpoint:
    1. Fetches content from the URL
    2. Creates a cryptographic hash
    3. Registers the asset on Algorand
    4. Returns verification details
    
    Supported asset types:
    - certificate: Educational or professional certificate
    - document: Legal or official document
    - image: Image or artwork
    - credit_file: Credit or financial record
    - other: Other digital asset
    """
    service = get_asset_protection_service()
    
    # Validate asset type
    valid_types = ["certificate", "document", "image", "credit_file", "other"]
    if request.asset_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid asset type. Must be one of: {valid_types}"
        )
    
    result = await service.protect_url(
        url=request.url,
        asset_name=request.asset_name,
        asset_type=request.asset_type,
        owner_address=request.owner_address,
        metadata=request.metadata
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Protection failed"))
    
    return result


@router.post("/protect/file")
async def protect_file_asset(
    file: UploadFile = File(..., description="File to protect"),
    asset_name: str = Form(..., description="Name/description of the asset"),
    asset_type: str = Form(..., description="Type: certificate, document, image, credit_file, other"),
    owner_address: str = Form(..., description="Algorand address of the asset owner"),
    metadata: Optional[str] = Form(default=None, description="Additional metadata as JSON string")
) -> Dict[str, Any]:
    """
    Protect a file by registering on Algorand blockchain.
    
    Upload a file to protect it with blockchain registration.
    The file content is hashed and registered on Algorand.
    """
    service = get_asset_protection_service()
    
    # Validate asset type
    valid_types = ["certificate", "document", "image", "credit_file", "other"]
    if asset_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid asset type. Must be one of: {valid_types}"
        )
    
    # Read file content
    content = await file.read()
    
    # Parse metadata if provided
    parsed_metadata = None
    if metadata:
        import json
        try:
            parsed_metadata = json.loads(metadata)
        except:
            pass
    
    result = await service.protect_content(
        content=content,
        asset_name=asset_name,
        asset_type=asset_type,
        owner_address=owner_address,
        filename=file.filename,
        metadata=parsed_metadata
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Protection failed"))
    
    return result


@router.get("/verify/{content_hash}")
async def verify_asset(content_hash: str) -> Dict[str, Any]:
    """
    Verify an asset by its content hash.
    
    Returns verification details including:
    - Whether the asset is registered on blockchain
    - Registration timestamp
    - Asset metadata
    """
    service = get_asset_protection_service()
    
    result = await service.verify_asset(content_hash)
    
    return result


@router.post("/verify")
async def verify_with_content(request: VerifyAssetRequest) -> Dict[str, Any]:
    """
    Verify an asset with content hash.
    
    Returns verification details.
    """
    service = get_asset_protection_service()
    
    result = await service.verify_asset(request.content_hash)
    
    return result


@router.get("/assets/{owner_address}")
async def get_protected_assets(owner_address: str) -> Dict[str, Any]:
    """
    Get all protected assets for an owner address.
    
    Returns list of assets registered on Algorand for the given address.
    """
    service = get_asset_protection_service()
    
    result = await service.get_protected_assets(owner_address)
    
    return result


@router.get("/types")
async def get_asset_types() -> Dict[str, str]:
    """
    Get supported asset types.
    
    Returns a dictionary of asset types and their descriptions.
    """
    return {
        "certificate": "Educational or professional certificate",
        "document": "Legal or official document",
        "image": "Image or artwork",
        "credit_file": "Credit or financial record",
        "other": "Other digital asset"
    }
