from datetime import timedelta
from feast import Entity, FeatureView, Field, PushSource, RequestSource
from feast.types import Float64, Int64, String


# Entity representing a loan applicant
applicant = Entity(
    name="applicant_id",
    description="Unique identifier for a loan applicant",
)

# Push source - features are pushed in from the training notebook
applicant_push_source = PushSource(
    name="applicant_push_source",
    batch_source=None,
)

# Core loan applicant features for training and serving
applicant_features_view = FeatureView(
    name="applicant_features",
    entities=[applicant],
    ttl=timedelta(days=365),
    schema=[
        Field(name="AMT_INCOME_TOTAL",           dtype=Float64, description="Total annual income"),
        Field(name="AMT_CREDIT",                 dtype=Float64, description="Credit amount of the loan"),
        Field(name="AMT_ANNUITY",                dtype=Float64, description="Loan annuity payment"),
        Field(name="AMT_GOODS_PRICE",            dtype=Float64, description="Price of goods for the loan"),
        Field(name="DAYS_BIRTH",                 dtype=Int64,   description="Age in days (negative value)"),
        Field(name="DAYS_EMPLOYED",              dtype=Int64,   description="Days employed (negative = currently employed)"),
        Field(name="REGION_POPULATION_RELATIVE", dtype=Float64, description="Normalized region population density"),
        Field(name="CNT_FAM_MEMBERS",            dtype=Float64, description="Number of family members"),
        Field(name="FLAG_MOBIL",                 dtype=Int64,   description="Has mobile phone (1=yes, 0=no)"),
        Field(name="FLAG_EMAIL",                 dtype=Int64,   description="Has email address (1=yes, 0=no)"),
        Field(name="FLAG_WORK_PHONE",            dtype=Int64,   description="Has work phone (1=yes, 0=no)"),
    ],
    source=applicant_push_source,
    description="Core loan applicant financial and demographic features for XGBoost classifier",
    tags={"team": "microloan", "model": "loan-classifier", "version": "1.0"},
)

# Request-time features provided at inference time (not stored in feature store)
live_application_source = RequestSource(
    name="live_application",
    schema=[
        Field(name="requested_loan_amount", dtype=Float64),
        Field(name="loan_purpose",          dtype=String),
    ],
)
