"""
Module to handle publicly exposed S3 buckets
"""
from datetime import datetime

from .base import BaseReaperModule
from ..sdks.aws import MockAWSS3


class S3VisibilityReaper(BaseReaperModule):
    """Module to handle publicly exposed S3 buckets."""
    
    def validate(self) -> str:
        """Validate required fields for S3 bucket event"""
        if self.event.get("bucket_name") and self.event.get("region"):
            return "[Validate] SUCCESS: Required fields 'bucket_name' and 'region' are present."
        return "[Validate] FAILED: Event is missing 'bucket_name' or 'region'."
    
    def execute(self) -> str:
        """Execute S3 bucket security remediation"""
        bucket = self.event.get('bucket_name')
        region = self.event.get('region')
        
        if self.dry_run_mode:
            # Simulate API calls without actually executing
            mock_response = {
                "dry_run": True,
                "action": "put_public_access_block",
                "bucket": bucket,
                "region": region,
                "timestamp": datetime.now().isoformat(),
                "would_execute": f"s3.put_public_access_block for {bucket}"
            }
            self.api_responses.append(mock_response)
            return f"[Execute]  DRY RUN: Would restrict public permissions on S3 bucket '{bucket}'."
        else:
            # Execute actual API calls (using mock for demo)
            try:
                api_response1 = MockAWSS3.put_public_access_block(bucket, region)
                self.api_responses.append(api_response1)
                
                # Also update bucket policy
                restrictive_policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket}/*",
                        "Condition": {"Bool": {"aws:SecureTransport": "false"}}
                    }]
                }
                api_response2 = MockAWSS3.put_bucket_policy(bucket, restrictive_policy)
                self.api_responses.append(api_response2)
                
                return f"[Execute]  ACTION: Restricted public permissions on S3 bucket '{bucket}'."
            
            except (ConnectionError, FileNotFoundError) as e:
                error_response = {
                    "success": False,
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
                self.api_responses.append(error_response)
                return f"[Execute]  EXCEPTION: Network/Access error - {str(e)}"
            
            except (PermissionError, ValueError) as e:
                error_response = {
                    "success": False,
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
                self.api_responses.append(error_response)
                return f"[Execute]  EXCEPTION: Permission/Validation error - {str(e)}"
            
            except Exception as e:
                error_response = {
                    "success": False,
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
                self.api_responses.append(error_response)
                return f"[Execute]  EXCEPTION: Unexpected error - {str(e)}"
    
    def report(self) -> str:
        """Generate execution report"""
        mode = "DRY RUN" if self.dry_run_mode else "LIVE"
        bucket = self.event.get('bucket_name')
        return f"[Report]   {mode}: Public access block applied to '{bucket}'"
