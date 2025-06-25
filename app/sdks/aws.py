"""
Mock AWS S3 API for testing bucket policy changes
"""
from datetime import datetime
from typing import Dict, Any

from .base import BaseSDK


class MockAWSS3(BaseSDK):
    """Mock AWS S3 API for testing bucket policy changes"""
    
    def is_available(self) -> bool:
        """Check if SDK is available"""
        return True
    
    def get_name(self) -> str:
        """Return SDK name"""
        return "MockAWSS3"
    
    @staticmethod
    def put_public_access_block(bucket_name: str, region: str) -> Dict[str, Any]:
        """Simulate applying public access block to S3 bucket"""
        # Simulate various exceptions
        if "exception" in bucket_name.lower():
            raise ConnectionError(f"Network error connecting to AWS S3 in region {region}")
        
        if "permission" in bucket_name.lower():
            raise PermissionError(f"Access denied: insufficient permissions for bucket {bucket_name}")
        
        if "notfound" in bucket_name.lower():
            raise FileNotFoundError(f"Bucket {bucket_name} not found in region {region}")
        
        return {
            "success": True,
            "message": f"Public access block applied to bucket {bucket_name}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "s3.put_public_access_block",
            "bucket": bucket_name,
            "region": region
        }
    
    @staticmethod
    def put_bucket_policy(bucket_name: str, policy: Dict) -> Dict[str, Any]:
        """Simulate updating S3 bucket policy"""
        # Simulate policy validation errors
        if "invalid" in bucket_name.lower():
            raise ValueError(f"Invalid bucket policy format for {bucket_name}")
        
        return {
            "success": True,
            "message": f"Bucket policy updated for {bucket_name}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "s3.put_bucket_policy",
            "bucket": bucket_name,
            "policy_statements": len(policy.get("Statement", []))
        }
