# AI Pipelines

## qwen3_microloan_pipeline.yaml

Kubeflow Pipeline (KFP v2) for Qwen3 LLM fine-tuning on the microloan explanation dataset.

### Steps
1. Load training data from MinIO (`data/training/feature_explanations_dataset.json`)
2. Format chat data (Qwen3 system/user/assistant format)
3. Fine-tune Qwen3 with LoRA on GPU
4. Merge LoRA adapters into full model
5. Upload merged model to MinIO (`models/generative/qwen3-loan-advisor/`)
6. Register model to Model Registry

### Parameters to update before running
| Parameter | Value |
|---|---|
| `minio_endpoint` | `https://minio-api-a-rh-department.apps.ocp.q7fmx.sandbox5373.opentlc.com` |
| `minio_access_key` | `minio` |
| `minio_secret_key` | `minio123!` |
| `dataset_path` | `s3://data/training/feature_explanations_dataset.json` |
| `output_model_name` | `qwen3-loan-advisor` |

### Upload to RHOAI
1. RHOAI Dashboard → `a-rh-department` project → Pipelines → Import pipeline
2. Upload this YAML file
3. Create run with updated parameters
