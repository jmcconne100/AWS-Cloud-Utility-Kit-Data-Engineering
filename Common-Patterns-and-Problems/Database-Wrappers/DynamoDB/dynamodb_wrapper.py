import boto3
import botocore
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DynamoDBClient:
    def __init__(self, table_name: str, region: str = "us-west-1"):
        self.table_name = table_name
        self.region = region
        self.client = boto3.resource('dynamodb', region_name=region)
        self.table = self.client.Table(table_name)

    def put_item(self, item: Dict[str, Any]) -> bool:
        try:
            self.table.put_item(Item=item)
            logger.info(f"✅ Put item into {self.table_name}: {item}")
            return True
        except ClientError as e:
            logger.error(f"❌ Failed to put item: {e.response['Error']['Message']}")
            return False

    def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            logger.info(f"📥 Retrieved item: {item}")
            return item
        except ClientError as e:
            logger.error(f"❌ Failed to get item: {e.response['Error']['Message']}")
            return None

    def update_item(self, key: Dict[str, Any], update_expr: str, expr_attrs: Dict[str, Any]) -> bool:
        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attrs
            )
            logger.info(f"🔄 Updated item {key}")
            return True
        except ClientError as e:
            logger.error(f"❌ Failed to update item: {e.response['Error']['Message']}")
            return False

    def query_by_partition_key(self, partition_key: str, value: Any) -> list:
        try:
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key(partition_key).eq(value)
            )
            items = response.get('Items', [])
            logger.info(f"🔍 Query returned {len(items)} items")
            return items
        except ClientError as e:
            logger.error(f"❌ Failed to query: {e.response['Error']['Message']}")
            return []

    # Deduplication Helpers
    def was_processed(self, event_id: str) -> bool:
        item = self.get_item({"event_id": event_id})
        return item is not None

    def mark_processed(self, event_id: str) -> bool:
        return self.put_item({"event_id": event_id, "status": "processed", "timestamp": int(time.time())})
