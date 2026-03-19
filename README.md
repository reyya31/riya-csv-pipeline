# Riya CSV Pipeline Processor

A fully serverless, event-driven CSV processing pipeline built on AWS.
When a CSV file is uploaded to the inbound S3 bucket, it automatically
gets processed and stored in the outbound bucket with a log entry in DynamoDB.

---

## Architecture Flow
```
S3 (inbound) → SQS Queue → Lambda Function → S3 (outbound)
                                           → DynamoDB (log)
```

---

## Flow Explanation

1. A CSV file is uploaded to `riya-inbound-bucket/uploads/`
2. S3 sends an event notification to the SQS queue
3. SQS triggers the Lambda function
4. Lambda reads the CSV file using Pandas
5. Adds a `processed_at` timestamp column to the CSV
6. Writes the processed CSV to `riya-outbound-bucket/processed/`
7. Logs the file path, timestamp, and status in DynamoDB

---

## AWS Services Used

| Service | Purpose |
|---|---|
| S3 (inbound) | Stores incoming raw CSV files |
| S3 (outbound) | Stores processed CSV files |
| SQS | Event queue that triggers Lambda |
| Lambda | Processes the CSV file using Python |
| DynamoDB | Logs every processed file with status |
| CloudWatch | Stores Lambda execution logs |

---

## Project Structure
```
riya-csv-pipeline/
├── lambda_function.py   # Main Lambda handler
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Implementation Details

### lambda_function.py
- Reads SQS event records
- Extracts S3 bucket name and file key from the event
- Skips non-CSV files
- Reads CSV from inbound bucket using Pandas
- Adds `processed_at` UTC timestamp column
- Writes processed CSV to outbound bucket
- Logs entry to DynamoDB with `object_key`, `processed_at`, and `status`
- Returns `batchItemFailures` for partial batch failure handling

---

## Environment Variables

| Variable | Value |
|---|---|
| `OUTBOUND_BUCKET` | `riya-outbound-bucket` |
| `LOG_TABLE` | `pipeline_processing_log` |

---

## DynamoDB Log Table

Table name: `pipeline_processing_log`

| Column | Type | Description |
|---|---|---|
| `object_key` | String | File path of the processed CSV |
| `processed_at` | String | UTC timestamp of processing |
| `status` | String | SUCCESS or FAILURE |

---

## How to Test

1. Upload any `.csv` file to `riya-inbound-bucket/uploads/`
2. Wait a few seconds for Lambda to trigger
3. Check `riya-outbound-bucket/processed/uploads/` for the processed file
4. Check `pipeline_processing_log` DynamoDB table for the log entry
5. Check CloudWatch logs for Lambda execution details

---

## Dependencies
```
boto3
pandas
```
```

---

Copy this into your `README.md` file, then run:
```
git add README.md
git commit -m "add detailed README"
git push