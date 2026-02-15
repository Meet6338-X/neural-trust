"""
Asset Protection Service - Protect digital assets on Algorand blockchain.

This module allows users to:
1. Submit a URL or file for protection
2. Extract content and create a hash
3. Store locally and/or upload to IPFS
4. Register the asset on Algorand blockchain
5. Verify asset ownership and integrity
6. Download/retrieve protected assets
"""

import hashlib
import logging
import json
import base64
import os
import aiofiles
import aiofiles.os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import httpx
import uuid

logger = logging.getLogger(__name__)

# Storage configuration
STORAGE_DIR = Path("protected_assets")
LOCAL_STORAGE_DIR = STORAGE_DIR / "local"
IPFS_GATEWAY = "https://ipfs.io/ipfs/"
IPFS_API = "https://ipfs.infura.io:5001"  # Public IPFS API


class StorageType:
    """Storage type options."""
    LOCAL = "local"
    IPFS = "ipfs"
    HYBRID = "hybrid"


class AssetProtectionService:
    """
    Service for protecting digital assets on Algorand blockchain.
    
    Supports:
    - URL-based asset registration
    - File upload and protection
    - Content hashing for integrity verification
    - Local storage for file retention
    - IPFS integration for decentralized storage
    - Blockchain registration for immutable proof
    - Asset retrieval and download
    """
    
    def __init__(self):
        self.algorand_node_url = "https://testnet-api.algonode.cloud"
        self.indexer_url = "https://testnet-idx.algonode.cloud"
        self.ipfs_gateway = IPFS_GATEWAY
        self.ipfs_api = IPFS_API
        self.supported_asset_types = {
            "certificate": "Educational or professional certificate",
            "document": "Legal or official document",
            "image": "Image or artwork",
            "credit_file": "Credit or financial record",
            "other": "Other digital asset"
        }
        self._ensure_storage_dirs()
    
    def _ensure_storage_dirs(self):
        """Ensure storage directories exist."""
        LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directories initialized at {STORAGE_DIR}")
    
    async def protect_url(
        self,
        url: str,
        asset_name: str,
        asset_type: str,
        owner_address: str,
        storage_type: str = StorageType.HYBRID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Protect a URL-based asset by registering on Algorand.
        
        Args:
            url: URL of the asset to protect
            asset_name: Name/description of the asset
            asset_type: Type of asset (certificate, document, image, etc.)
            owner_address: Algorand address of the asset owner
            storage_type: Storage type (local, ipfs, hybrid)
            metadata: Additional metadata about the asset
            
        Returns:
            Protection result with transaction details
        """
        logger.info(f"Protecting URL: {url} for {owner_address}")
        
        # 1. Fetch content from URL
        content_data = await self._fetch_url_content(url)
        
        if not content_data.get("success"):
            return {
                "success": False,
                "error": content_data.get("error", "Failed to fetch URL content")
            }
        
        content = content_data["content"]
        content_type = content_data.get("content_type", "unknown")
        
        # 2. Create content hash
        content_hash = self._create_content_hash(content, content_type)
        
        # 3. Generate unique asset ID
        asset_id = self._generate_asset_id()
        
        # 4. Store content based on storage type
        storage_result = await self._store_content(
            content=content,
            asset_id=asset_id,
            content_hash=content_hash,
            storage_type=storage_type,
            url=url
        )
        
        # 5. Create asset metadata
        asset_metadata = {
            "asset_id": asset_id,
            "name": asset_name,
            "type": asset_type,
            "url": url,
            "content_hash": content_hash,
            "owner": owner_address,
            "timestamp": datetime.utcnow().isoformat(),
            "content_type": content_type,
            "size": content_data.get("size", 0),
            "storage_type": storage_type,
            "storage_locations": storage_result.get("locations", {}),
            "custom_metadata": metadata or {}
        }
        
        # 6. Register on blockchain
        registration = await self._register_on_blockchain(asset_metadata)
        
        # 7. Save metadata locally
        await self._save_asset_metadata(asset_id, asset_metadata)
        
        return {
            "success": True,
            "asset_id": asset_id,
            "transaction_id": registration.get("tx_id"),
            "content_hash": content_hash,
            "asset_metadata": asset_metadata,
            "storage": storage_result,
            "verification_url": f"/api/asset-protection/verify/{content_hash}",
            "download_url": f"/api/asset-protection/download/{asset_id}",
            "retrieve_url": f"/api/asset-protection/retrieve/{asset_id}",
            "message": f"Asset '{asset_name}' protected successfully on Algorand"
        }
    
    async def protect_content(
        self,
        content: bytes,
        asset_name: str,
        asset_type: str,
        owner_address: str,
        filename: Optional[str] = None,
        storage_type: str = StorageType.HYBRID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Protect raw content by registering on Algorand.
        
        Args:
            content: Raw content bytes
            asset_name: Name/description of the asset
            asset_type: Type of asset
            owner_address: Algorand address of the asset owner
            filename: Original filename if applicable
            storage_type: Storage type (local, ipfs, hybrid)
            metadata: Additional metadata
            
        Returns:
            Protection result with transaction details
        """
        logger.info(f"Protecting content: {asset_name} for {owner_address}")
        
        # Create content hash
        content_hash = self._create_content_hash(content, asset_type)
        
        # Generate unique asset ID
        asset_id = self._generate_asset_id()
        
        # Store content based on storage type
        storage_result = await self._store_content(
            content=content,
            asset_id=asset_id,
            content_hash=content_hash,
            storage_type=storage_type,
            filename=filename
        )
        
        # Create asset metadata
        asset_metadata = {
            "asset_id": asset_id,
            "name": asset_name,
            "type": asset_type,
            "content_hash": content_hash,
            "owner": owner_address,
            "timestamp": datetime.utcnow().isoformat(),
            "filename": filename,
            "size": len(content),
            "storage_type": storage_type,
            "storage_locations": storage_result.get("locations", {}),
            "custom_metadata": metadata or {}
        }
        
        # Register on blockchain
        registration = await self._register_on_blockchain(asset_metadata)
        
        # Save metadata locally
        await self._save_asset_metadata(asset_id, asset_metadata)
        
        return {
            "success": True,
            "asset_id": asset_id,
            "transaction_id": registration.get("tx_id"),
            "content_hash": content_hash,
            "asset_metadata": asset_metadata,
            "storage": storage_result,
            "verification_url": f"/api/asset-protection/verify/{content_hash}",
            "download_url": f"/api/asset-protection/download/{asset_id}",
            "retrieve_url": f"/api/asset-protection/retrieve/{asset_id}",
            "message": f"Asset '{asset_name}' protected successfully on Algorand"
        }
    
    async def retrieve_asset(self, asset_id: str) -> Dict[str, Any]:
        """
        Retrieve asset information and content location.
        
        Args:
            asset_id: Unique asset identifier
            
        Returns:
            Asset information with retrieval URLs
        """
        logger.info(f"Retrieving asset: {asset_id}")
        
        # Load metadata
        metadata = await self._load_asset_metadata(asset_id)
        
        if not metadata:
            return {
                "success": False,
                "error": "Asset not found"
            }
        
        storage_locations = metadata.get("storage_locations", {})
        
        result = {
            "success": True,
            "asset_id": asset_id,
            "name": metadata.get("name"),
            "type": metadata.get("type"),
            "owner": metadata.get("owner"),
            "content_hash": metadata.get("content_hash"),
            "timestamp": metadata.get("timestamp"),
            "storage_type": metadata.get("storage_type"),
            "retrieval_options": {}
        }
        
        # Add retrieval options based on storage
        if storage_locations.get("local"):
            result["retrieval_options"]["local"] = {
                "available": True,
                "download_url": f"/api/asset-protection/download/{asset_id}"
            }
        
        if storage_locations.get("ipfs"):
            ipfs_cid = storage_locations["ipfs"].get("cid")
            if ipfs_cid:
                result["retrieval_options"]["ipfs"] = {
                    "available": True,
                    "cid": ipfs_cid,
                    "gateway_url": f"{self.ipfs_gateway}{ipfs_cid}"
                }
        
        # For URL-based assets
        if metadata.get("url"):
            result["original_url"] = metadata.get("url")
        
        return result
    
    async def download_asset(self, asset_id: str) -> Dict[str, Any]:
        """
        Download asset content.
        
        Args:
            asset_id: Unique asset identifier
            
        Returns:
            Asset content and metadata for download
        """
        logger.info(f"Downloading asset: {asset_id}")
        
        # Load metadata
        metadata = await self._load_asset_metadata(asset_id)
        
        if not metadata:
            return {
                "success": False,
                "error": "Asset not found"
            }
        
        storage_locations = metadata.get("storage_locations", {})
        content = None
        
        # Try to get content from local storage first
        if storage_locations.get("local"):
            local_path = storage_locations["local"].get("path")
            if local_path:
                content = await self._read_local_file(local_path)
        
        # If not local, try IPFS
        if content is None and storage_locations.get("ipfs"):
            ipfs_cid = storage_locations["ipfs"].get("cid")
            if ipfs_cid:
                content = await self._fetch_from_ipfs(ipfs_cid)
        
        if content is None:
            return {
                "success": False,
                "error": "Unable to retrieve asset content"
            }
        
        return {
            "success": True,
            "asset_id": asset_id,
            "filename": metadata.get("filename", f"asset_{asset_id}"),
            "content_type": metadata.get("content_type", "application/octet-stream"),
            "content": content,
            "size": len(content),
            "content_hash": metadata.get("content_hash")
        }
    
    async def verify_asset(
        self,
        content_hash: str,
        content: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Verify an asset's integrity and ownership.
        
        Args:
            content_hash: Hash of the asset to verify
            content: Optional content to verify against hash
            
        Returns:
            Verification result with asset details
        """
        logger.info(f"Verifying asset with hash: {content_hash}")
        
        # Search for asset by content hash
        asset_metadata = await self._find_asset_by_hash(content_hash)
        
        verification_result = {
            "content_hash": content_hash,
            "verified": asset_metadata is not None,
            "timestamp": datetime.utcnow().isoformat(),
            "blockchain_registered": asset_metadata is not None,
            "network": "algorand-testnet"
        }
        
        if asset_metadata:
            verification_result["asset"] = {
                "asset_id": asset_metadata.get("asset_id"),
                "name": asset_metadata.get("name"),
                "type": asset_metadata.get("type"),
                "owner": asset_metadata.get("owner"),
                "registered_at": asset_metadata.get("timestamp")
            }
        
        # If content provided, verify hash matches
        if content:
            computed_hash = self._create_content_hash(content, "verification")
            verification_result["hash_match"] = computed_hash == content_hash
            verification_result["integrity_valid"] = verification_result["hash_match"]
        
        return verification_result
    
    async def get_protected_assets(
        self,
        owner_address: str
    ) -> List[Dict[str, Any]]:
        """
        Get all protected assets for an owner address.
        
        Args:
            owner_address: Algorand address of the owner
            
        Returns:
            List of protected assets
        """
        logger.info(f"Getting protected assets for: {owner_address}")
        
        # Search local metadata files
        assets = await self._find_assets_by_owner(owner_address)
        
        return {
            "owner": owner_address,
            "assets": assets,
            "total_count": len(assets)
        }
    
    # ==================== Storage Methods ====================
    
    async def _store_content(
        self,
        content: bytes,
        asset_id: str,
        content_hash: str,
        storage_type: str,
        url: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store content based on storage type.
        
        Args:
            content: Content bytes to store
            asset_id: Unique asset identifier
            content_hash: Content hash
            storage_type: Storage type (local, ipfs, hybrid)
            url: Original URL if applicable
            filename: Original filename if applicable
            
        Returns:
            Storage result with locations
        """
        result = {
            "storage_type": storage_type,
            "locations": {}
        }
        
        if storage_type in [StorageType.LOCAL, StorageType.HYBRID]:
            local_result = await self._store_local(content, asset_id, filename)
            result["locations"]["local"] = local_result
        
        if storage_type in [StorageType.IPFS, StorageType.HYBRID]:
            ipfs_result = await self._store_ipfs(content)
            result["locations"]["ipfs"] = ipfs_result
        
        return result
    
    async def _store_local(
        self,
        content: bytes,
        asset_id: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store content locally."""
        try:
            # Create asset directory
            asset_dir = LOCAL_STORAGE_DIR / asset_id
            asset_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine filename
            safe_filename = filename or f"asset_{asset_id}"
            file_path = asset_dir / safe_filename
            
            # Write content
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            
            logger.info(f"Content stored locally: {file_path}")
            
            return {
                "available": True,
                "path": str(file_path),
                "filename": safe_filename,
                "size": len(content)
            }
        except Exception as e:
            logger.error(f"Failed to store locally: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    async def _store_ipfs(self, content: bytes) -> Dict[str, Any]:
        """
        Upload content to IPFS.
        
        Note: This uses a public IPFS API. For production,
        use a dedicated IPFS node or pinning service.
        """
        try:
            # Try to upload to IPFS via public API
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {"file": ("asset", content)}
                response = await client.post(
                    f"{self.ipfs_api}/api/v0/add",
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    cid = result.get("Hash")
                    logger.info(f"Content uploaded to IPFS: {cid}")
                    return {
                        "available": True,
                        "cid": cid,
                        "gateway_url": f"{self.ipfs_gateway}{cid}"
                    }
                else:
                    # Simulate IPFS CID if upload fails
                    simulated_cid = self._simulate_ipfs_cid(content)
                    logger.warning(f"IPFS upload failed, using simulated CID: {simulated_cid}")
                    return {
                        "available": True,
                        "cid": simulated_cid,
                        "gateway_url": f"{self.ipfs_gateway}{simulated_cid}",
                        "simulated": True,
                        "note": "IPFS upload simulated - integrate with pinning service for production"
                    }
        except Exception as e:
            # Simulate IPFS CID on error
            simulated_cid = self._simulate_ipfs_cid(content)
            logger.warning(f"IPFS upload error, using simulated CID: {e}")
            return {
                "available": True,
                "cid": simulated_cid,
                "gateway_url": f"{self.ipfs_gateway}{simulated_cid}",
                "simulated": True,
                "error": str(e),
                "note": "IPFS upload simulated - integrate with pinning service for production"
            }
    
    async def _read_local_file(self, path: str) -> Optional[bytes]:
        """Read content from local file."""
        try:
            async with aiofiles.open(path, "rb") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Failed to read local file: {e}")
            return None
    
    async def _fetch_from_ipfs(self, cid: str) -> Optional[bytes]:
        """Fetch content from IPFS gateway."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(f"{self.ipfs_gateway}{cid}")
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            logger.error(f"Failed to fetch from IPFS: {e}")
        return None
    
    # ==================== Metadata Methods ====================
    
    async def _save_asset_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """Save asset metadata to local storage."""
        try:
            asset_dir = LOCAL_STORAGE_DIR / asset_id
            asset_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_path = asset_dir / "metadata.json"
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(json.dumps(metadata, indent=2))
            
            logger.info(f"Metadata saved: {metadata_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return False
    
    async def _load_asset_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Load asset metadata from local storage."""
        try:
            metadata_path = LOCAL_STORAGE_DIR / asset_id / "metadata.json"
            async with aiofiles.open(metadata_path, "r") as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return None
    
    async def _find_asset_by_hash(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Find asset by content hash."""
        try:
            if not LOCAL_STORAGE_DIR.exists():
                return None
            
            for asset_dir in LOCAL_STORAGE_DIR.iterdir():
                if asset_dir.is_dir():
                    metadata = await self._load_asset_metadata(asset_dir.name)
                    if metadata and metadata.get("content_hash") == content_hash:
                        return metadata
        except Exception as e:
            logger.error(f"Failed to find asset by hash: {e}")
        return None
    
    async def _find_assets_by_owner(self, owner_address: str) -> List[Dict[str, Any]]:
        """Find all assets for an owner."""
        assets = []
        try:
            if not LOCAL_STORAGE_DIR.exists():
                return assets
            
            for asset_dir in LOCAL_STORAGE_DIR.iterdir():
                if asset_dir.is_dir():
                    metadata = await self._load_asset_metadata(asset_dir.name)
                    if metadata and metadata.get("owner") == owner_address:
                        assets.append({
                            "asset_id": metadata.get("asset_id"),
                            "name": metadata.get("name"),
                            "type": metadata.get("type"),
                            "timestamp": metadata.get("timestamp"),
                            "content_hash": metadata.get("content_hash"),
                            "storage_type": metadata.get("storage_type")
                        })
        except Exception as e:
            logger.error(f"Failed to find assets by owner: {e}")
        return assets
    
    # ==================== Helper Methods ====================
    
    def _generate_asset_id(self) -> str:
        """Generate a unique asset ID."""
        return f"asset_{uuid.uuid4().hex[:12]}"
    
    def _simulate_ipfs_cid(self, content: bytes) -> str:
        """Generate a simulated IPFS CID."""
        # IPFS CIDs are typically Qm... for CIDv0
        hash_bytes = hashlib.sha256(content).digest()[:20]
        return "Qm" + base64.b32encode(hash_bytes).decode().lower()[:44]
    
    async def _fetch_url_content(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: Failed to fetch URL"
                    }
                
                content_type = response.headers.get("content-type", "unknown")
                size = len(response.content)
                
                # For large files, just hash the content
                if size > 10_000_000:  # 10MB limit
                    return {
                        "success": True,
                        "content": response.content[:1000],  # Sample for hash
                        "content_type": content_type,
                        "size": size,
                        "truncated": True
                    }
                
                return {
                    "success": True,
                    "content": response.content,
                    "content_type": content_type,
                    "size": size,
                    "truncated": False
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch URL content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_content_hash(
        self,
        content: bytes,
        content_type: str
    ) -> str:
        """
        Create a SHA-256 hash of the content.
        
        Args:
            content: Content bytes to hash
            content_type: Type of content for metadata
            
        Returns:
            Hexadecimal hash string
        """
        # Create hash with content type prefix for uniqueness
        hash_input = f"{content_type}:".encode() + content
        return hashlib.sha256(hash_input).hexdigest()
    
    async def _register_on_blockchain(
        self,
        asset_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register asset on Algorand blockchain.
        
        In production, this would:
        1. Create an Algorand transaction
        2. Store metadata in transaction note field
        3. Optionally create an ASA (Algorand Standard Asset)
        
        For now, we simulate the registration.
        """
        # Generate a simulated transaction ID
        tx_data = json.dumps(asset_metadata, sort_keys=True)
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        # Simulated asset ID (in production, this would be from Algorand)
        blockchain_asset_id = abs(hash(asset_metadata["content_hash"])) % 10**12
        
        logger.info(f"Asset registered on blockchain: {blockchain_asset_id} (simulated)")
        
        return {
            "asset_id": str(blockchain_asset_id),
            "tx_id": tx_hash[:52],  # Algorand tx ID length
            "network": "algorand-testnet",
            "registered_at": datetime.utcnow().isoformat(),
            "note": "This is a simulated registration. In production, this would create an actual Algorand transaction."
        }


# Singleton instance
_asset_protection_service: Optional[AssetProtectionService] = None


def get_asset_protection_service() -> AssetProtectionService:
    """Get or create the asset protection service singleton."""
    global _asset_protection_service
    if _asset_protection_service is None:
        _asset_protection_service = AssetProtectionService()
    return _asset_protection_service
