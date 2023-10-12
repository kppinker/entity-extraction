import requests
import json
import boto3
import re
import pandas as pd
import awswrangler as wr
import os

def extract(job):
    
    prompt = f"Return a JSON object with the following keys: 'job_title', 'company', and 'salary' from the following JSON:\n {job}"
    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 100,
    })
    
    response = boto3.client('bedrock-runtime').invoke_model(body=body, modelId="anthropic.claude-v2")
    
    response_body = json.loads(response.get("body").read())
    response_completion = response_body.get("completion")
    # print(response_completion)
    
    response_json = {}
    matches = re.findall(r'\{.*?\}', response_completion, re.DOTALL)
    if matches:
        response_json = json.loads(matches[0])
    # print(response_json)

    return response_json

url = "https://boards-api.greenhouse.io/v1/boards/camundaservices/jobs?content=true"
response = requests.get(url)
content = json.loads(response.content.decode('utf-8'))
jobs = content["jobs"]

jsons = [extract(job) for job in jobs]
# print(jsons)

df = pd.DataFrame.from_dict(jsons)
print(df)

# wr.s3.to_parquet(
#     dataframe=df,
#     path=f"s3://{os.environ['OUTPUT_BUCKET_NAME']}/output.parquet"
# )
