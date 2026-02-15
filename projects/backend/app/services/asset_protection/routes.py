"""
API routes for Asset Protection endpoints.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from .asset_protection_service import get_asset_protection_service, StorageType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/asset-protection", tags=["asset-protection"])


# ==================== Request Models ====================

class ProtectUrlRequest(BaseModel):
    """Request for protecting a URL-based asset."""
    url: str = Field(..., description="URL of the asset to protect")
    asset_name: str = Field(..., description="Name/description of the asset")
    asset_type: str = Field(..., description="Type: certificate, document, image, credit_file, other")
    owner_address: str = Field(..., description="Algorand address of the asset owner")
    storage_type: str = Field(default=StorageType.HYBRID, description="Storage type: local, ipfs, hybrid")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ProtectFileRequest(BaseModel):
    """Request for protecting a file-based asset."""
    asset_name: str = Field(..., description="Name/description of the asset")
    asset_type: str = Field(..., description="Type: certificate, document, image, credit_file, other")
    owner_address: str = Field(..., description="Algorand address of the asset owner")
    storage_type: str = Field(default=StorageType.HYBRID, description="Storage type: local, ipfs, hybrid")
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
    3. Stores content based on storage_type (local, ipfs, hybrid)
    4. Registers the asset on Algorand
    5. Returns verification and download details
    
    Storage Types:
    - **local**: Store file on server only
    - **ipfs**: Upload to IPFS decentralized storage
    - **hybrid**: Both local and IPFS storage (recommended)
    
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
    
    # Validate storage type
    valid_storage = [StorageType.LOCAL, StorageType.IPFS, StorageType.HYBRID]
    if request.storage_type not in valid_storage:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid storage type. Must be one of: {valid_storage}"
        )
    
    result = await service.protect_url(
        url=request.url,
        asset_name=request.asset_name,
        asset_type=request.asset_type,
        owner_address=request.owner_address,
        storage_type=request.storage_type,
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
    storage_type: str = Form(default=StorageType.HYBRID, description="Storage type: local, ipfs, hybrid"),
    metadata: Optional[str] = Form(default=None, description="Additional metadata as JSON string")
) -> Dict[str, Any]:
    """
    Protect a file by registering on Algorand blockchain.
    
    Upload a file to protect it with blockchain registration.
    The file content is hashed, stored, and registered on Algorand.
    
    Storage Types:
    - **local**: Store file on server only
    - **ipfs**: Upload to IPFS decentralized storage
    - **hybrid**: Both local and IPFS storage (recommended)
    """
    service = get_asset_protection_service()
    
    # Validate asset type
    valid_types = ["certificate", "document", "image", "credit_file", "other"]
    if asset_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid asset type. Must be one of: {valid_types}"
        )
    
    # Validate storage type
    valid_storage = [StorageType.LOCAL, StorageType.IPFS, StorageType.HYBRID]
    if storage_type not in valid_storage:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid storage type. Must be one of: {valid_storage}"
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
        storage_type=storage_type,
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
    - Owner information
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


@router.get("/retrieve/{asset_id}")
async def retrieve_asset(asset_id: str) -> Dict[str, Any]:
    """
    Retrieve asset information and content locations.
    
    Returns:
    - Asset metadata (name, type, owner, timestamp)
    - Content hash for verification
    - Retrieval options based on storage type:
      - **local**: Download URL for server-stored file
      - **ipfs**: IPFS gateway URL for decentralized access
      - **original_url**: For URL-based assets
    """
    service = get_asset_protection_service()
    
    result = await service.retrieve_asset(asset_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Asset not found"))
    
    return result


@router.get("/download/{asset_id}")
async def download_asset(asset_id: str):
    """
    Download protected asset content.
    
    Returns the original file content for download.
    Content is retrieved from:
    1. Local storage (if available)
    2. IPFS gateway (if uploaded to IPFS)
    
    Returns the file with appropriate headers for download.
    """
    service = get_asset_protection_service()
    
    result = await service.download_asset(asset_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Asset not found"))
    
    # Return file response
    return Response(
        content=result["content"],
        media_type=result.get("content_type", "application/octet-stream"),
        headers={
            "Content-Disposition": f'attachment; filename="{result["filename"]}"',
            "Content-Length": str(result["size"]),
            "X-Content-Hash": result.get("content_hash", ""),
            "X-Asset-ID": asset_id
        }
    )


@router.get("/assets/{owner_address}")
async def get_protected_assets(owner_address: str) -> Dict[str, Any]:
    """
    Get all protected assets for an owner address.
    
    Returns list of assets registered on Algorand for the given address.
    Each asset includes:
    - asset_id: Unique identifier
    - name: Asset name
    - type: Asset type
    - timestamp: Registration time
    - content_hash: For verification
    - storage_type: Where content is stored
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


@router.get("/storage-types")
async def get_storage_types() -> Dict[str, Any]:
    """
    Get available storage types for asset protection.
    
    Returns storage options with descriptions and recommendations.
    """
    return {
        "types": {
            StorageType.LOCAL: {
                "name": "Local Storage",
                "description": "Store files on the server only",
                "pros": ["Fast access", "No external dependencies"],
                "cons": ["Single point of failure", "Limited to server availability"]
            },
            StorageType.IPFS: {
                "name": "IPFS Storage",
                "description": "Upload to IPFS decentralized network",
                "pros": ["Decentralized", "Censorship resistant", "Persistent"],
                "cons": ["Slower access", "Requires IPFS gateway"]
            },
            StorageType.HYBRID: {
                "name": "Hybrid Storage (Recommended)",
                "description": "Store locally AND upload to IPFS",
                "pros": ["Best of both worlds", "Redundancy", "Fast local access + decentralized backup"],
                "cons": ["Higher storage usage"]
            }
        },
        "default": StorageType.HYBRID,
        "recommendation": "Use hybrid storage for maximum protection and availability"
    }
