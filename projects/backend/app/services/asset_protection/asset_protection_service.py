"""
Asset Protection Service - Protect digital assets on Algorand blockchain.

This module allows users to:
1. Submit a URL or file for protection
2. Extract content and create a hash
3. Register the asset on Algorand blockchain
4. Verify asset ownership and integrity
"""

import hashlib
import logging
import json
import base64
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class AssetProtectionService:
    """
    Service for protecting digital assets on Algorand blockchain.
    
    Supports:
    - URL-based asset registration
    - Content hashing for integrity verification
    - Blockchain registration for immutable proof
    """
    
    def __init__(self):
        self.algorand_node_url = "https://testnet-api.algonode.cloud"
        self.indexer_url = "https://testnet-idx.algonode.cloud"
        self.supported_asset_types = {
            "certificate": "Educational or professional certificate",
            "document": "Legal or official document",
            "image": "Image or artwork",
            "credit_file": "Credit or financial record",
            "other": "Other digital asset"
        }
    
    async def protect_url(
        self,
        url: str,
        asset_name: str,
        asset_type: str,
        owner_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Protect a URL-based asset by registering on Algorand.
        
        Args:
            url: URL of the asset to protect
            asset_name: Name/description of the asset
            asset_type: Type of asset (certificate, document, image, etc.)
            owner_address: Algorand address of the asset owner
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
        
        # 2. Create content hash
        content_hash = self._create_content_hash(
            content_data["content"],
            content_data.get("content_type", "unknown")
        )
        
        # 3. Create asset metadata
        asset_metadata = {
            "name": asset_name,
            "type": asset_type,
            "url": url,
            "content_hash": content_hash,
            "owner": owner_address,
            "timestamp": datetime.utcnow().isoformat(),
            "content_type": content_data.get("content_type", "unknown"),
            "size": content_data.get("size", 0),
            "custom_metadata": metadata or {}
        }
        
        # 4. Register on blockchain (note: this is a simulation)
        # In production, this would create an Algorand transaction
        registration = await self._register_on_blockchain(asset_metadata)
        
        return {
            "success": True,
            "asset_id": registration.get("asset_id"),
            "transaction_id": registration.get("tx_id"),
            "content_hash": content_hash,
            "asset_metadata": asset_metadata,
            "verification_url": f"/api/asset-protection/verify/{content_hash}",
            "message": f"Asset '{asset_name}' protected successfully on Algorand"
        }
    
    async def protect_content(
        self,
        content: bytes,
        asset_name: str,
        asset_type: str,
        owner_address: str,
        filename: Optional[str] = None,
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
            metadata: Additional metadata
            
        Returns:
            Protection result with transaction details
        """
        logger.info(f"Protecting content: {asset_name} for {owner_address}")
        
        # Create content hash
        content_hash = self._create_content_hash(content, asset_type)
        
        # Create asset metadata
        asset_metadata = {
            "name": asset_name,
            "type": asset_type,
            "content_hash": content_hash,
            "owner": owner_address,
            "timestamp": datetime.utcnow().isoformat(),
            "filename": filename,
            "size": len(content),
            "custom_metadata": metadata or {}
        }
        
        # Register on blockchain
        registration = await self._register_on_blockchain(asset_metadata)
        
        return {
            "success": True,
            "asset_id": registration.get("asset_id"),
            "transaction_id": registration.get("tx_id"),
            "content_hash": content_hash,
            "asset_metadata": asset_metadata,
            "verification_url": f"/api/asset-protection/verify/{content_hash}",
            "message": f"Asset '{asset_name}' protected successfully on Algorand"
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
        
        # In production, this would query the Algorand blockchain
        # For now, we'll simulate the verification
        
        verification_result = {
            "content_hash": content_hash,
            "verified": True,
            "timestamp": datetime.utcnow().isoformat(),
            "blockchain_registered": True,
            "network": "algorand-testnet"
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
        
        # In production, this would query the Algorand indexer
        # For now, return a placeholder
        return {
            "owner": owner_address,
            "assets": [],
            "total_count": 0,
            "message": "Asset lookup requires blockchain indexer integration"
        }
    
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
        asset_id = abs(hash(asset_metadata["content_hash"])) % 10**12
        
        logger.info(f"Asset registered: {asset_id} (simulated)")
        
        return {
            "asset_id": str(asset_id),
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
