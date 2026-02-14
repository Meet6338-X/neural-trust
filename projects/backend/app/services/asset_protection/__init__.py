"""
Asset Protection Module for ChainGuardian.

This module provides functionality to protect digital assets
by registering them on the Algorand blockchain.
"""

from .asset_protection_service import AssetProtectionService, get_asset_protection_service
from .routes import router as asset_protection_router

__all__ = [
    "AssetProtectionService",
    "get_asset_protection_service",
    "asset_protection_router"
]
