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
        return {
            "success": True,
            "message": f"Bucket policy updated for {bucket_name}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "s3.put_bucket_policy",
            "bucket": bucket_name,
            "policy_statements": len(policy.get("Statement", []))
        }
