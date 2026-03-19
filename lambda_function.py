import os
import json
import boto3
import pandas as pd
import io
from datetime import datetime, timezone
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')

OUTBOUND_BUCKET = os.environ['OUTBOUND_BUCKET']
LOG_TABLE = os.environ['LOG_TABLE']

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def lambda_handler(event, context):
    failures = []

    for record in event['Records']:
        message_id = record['messageId']
        try:
            payload = json.loads(record['body'])
            for s3_event in payload['Records']:
                bucket = s3_event['s3']['bucket']['name']
                key = unquote_plus(s3_event['s3']['object']['key'])

                if not key.endswith('.csv'):
                    continue

                # Read CSV from inbound bucket
                obj = s3.get_object(Bucket=bucket, Key=key)
                df = pd.read_csv(io.BytesIO(obj['Body'].read()))
                df['processed_at'] = utc_now()

                # Write CSV to outbound bucket
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                out_key = f"processed/{key}"
                s3.put_object(Bucket=OUTBOUND_BUCKET, Key=out_key, Body=buffer.getvalue())

                # Write log to DynamoDB
                ddb.put_item(
                    TableName=LOG_TABLE,
                    Item={
                        'object_key': {'S': key},
                        'processed_at': {'S': utc_now()},
                        'status': {'S': 'SUCCESS'}
                    }
                )
        except Exception:
            failures.append({'itemIdentifier': message_id})

    return {'batchItemFailures': failures}