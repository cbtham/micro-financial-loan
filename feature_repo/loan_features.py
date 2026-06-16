from datetime import timedelta
from feast import Entity, Feature, FeatureView, Field, FileSource, RequestSource
from feast.types import Float64, Int64, String, Bool


# Entity representing a loan applicant
applicant = Entity(
    name="applicant_id",
    description="Unique identifier for a loan applicant",
)

# Offline source - parquet file uploaded during training
applicant_stats_source = FileSource(
    name="applicant_stats_source",
    path="data/applicant_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Core numeric and binary loan applicant features
applicant_features_view = FeatureView(
    name="applicant_features",
    entities=[applicant],
    ttl=timedelta(days=365),
    schema=[
        Field(name="AMT_INCOME_TOTAL",          dtype=Float64, description="Total annual income"),
        Field(name="AMT_CREDIT",                dtype=Float64, description="Credit amount of the loan"),
        Field(name="AMT_ANNUITY",               dtype=Float64, description="Loan annuity payment"),
        Field(name="AMT_GOODS_PRICE",           dtype=Float64, description="Price of goods for the loan"),
        Field(name="DAYS_BIRTH",                dtype=Int64,   description="Age in days (negative value)"),
        Field(name="DAYS_EMPLOYED",             dtype=Int64,   description="Days employed (negative = employed)"),
        Field(name="REGION_POPULATION_RELATIVE",dtype=Float64, description="Normalized region population density"),
        Field(name="CNT_FAM_MEMBERS",           dtype=Float64, description="Number of family members"),
        Field(name="FLAG_MOBIL",                dtype=Int64,   description="Has mobile phone (1/0)"),
        Field(name="FLAG_EMAIL",                dtype=Int64,   description="Has email (1/0)"),
        Field(name="FLAG_WORK_PHONE",           dtype=Int64,   description="Has work phone (1/0)"),
    ],
    source=applicant_stats_source,
    description="Core loan applicant financial and demographic features",
    tags={"team": "microloan", "model": "xgboost-classifier"},
)

# Request-time features for live inference
live_application_source = RequestSource(
    name="live_application",
    schema=[
        Field(name="requested_loan_amount", dtype=Float64),
        Field(name="loan_purpose",          dtype=String),
    ],
)
