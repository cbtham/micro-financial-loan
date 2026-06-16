# TrustyAI Bias Monitoring Configuration Guide

## Status: TrustyAI Successfully Installed ✓

You can now configure bias metrics via the OpenShift AI Dashboard.

## What You'll Configure

For your microloan model, you'll create bias metrics to monitor fairness in loan approval decisions across different demographic groups.

## Dashboard Configuration Steps

### 1. Navigate to Bias Metrics
- In your project (`a-rh-department`), go to **Settings** tab
- You should see "**TrustyAI installed**" confirmation
- Go to **Develop & train** → **Experiments** (or the bias metrics section)
- Click "**Configure metric**"

### 2. Fill in the Bias Metric Form

Here's what to enter for each field based on your loan approval model:

#### **Metric name**
```
Income-Based Loan Fairness
```
Description: Monitors whether loan approval rates are fair across different income levels

#### **Metric type**
Select: **SPD** (Statistical Parity Difference)

**What is SPD?**
- Measures the difference in approval rates between privileged and unprivileged groups
- Range: -1 to +1
- Target: Close to 0 (indicates fairness)
- Example: If high-income applicants have 80% approval but low-income have 40%, SPD = 0.40 (problematic)

Alternative: **DIR** (Disparate Impact Ratio)
- Ratio of approval rates (unprivileged / privileged)
- Range: 0 to infinity
- Target: Close to 1.0
- Legal threshold: Often 0.8 (80% rule in fair lending)

#### **Protected attribute**
```
input-0
```
This is your **AMT_INCOME_TOTAL** feature (total income)

#### **Privileged value**
```
200000
```
Income threshold - applicants above this are considered "privileged"
(You can adjust based on your data distribution - median is around 180,000)

#### **Unprivileged value**
```
100000
```
Income threshold - applicants below this are considered "unprivileged"

#### **Output** (Target field)
```
predict
```
or `output-0` - this is your model's prediction field

#### **Output value** (Favorable outcome)
```
0
```
Your model outputs: 0 = Approved (repaid), 1 = Rejected (default risk)

#### **Violation threshold**
```
0.1
```
Alert if SPD exceeds ±0.1 (10% difference in approval rates)

For DIR, use: `0.8` (80% rule - unprivileged group should get at least 80% of privileged group's approval rate)

#### **Metric batch size**
```
5000
```
(Keep default - this is how many predictions to analyze per metric calculation)

### 3. Click "Configure"

The system will create the bias metric and start monitoring.

## Example Configuration: Age-Based Fairness

You can create multiple metrics. Here's another example:

**Metric name:** Age-Based Loan Fairness  
**Metric type:** SPD  
**Protected attribute:** input-4 (DAYS_BIRTH)  
**Privileged value:** -10950 (Age 30 - days are negative)  
**Unprivileged value:** -18250 (Age 50)  
**Output:** predict  
**Output value:** 0 (approved)  
**Violation threshold:** 0.1  

## Understanding Your Features

Your model has 49 features after preprocessing. Here's the mapping:

| Input Name | Feature | Description |
|-----------|---------|-------------|
| input-0 | AMT_INCOME_TOTAL | Total income (key for income bias) |
| input-1 | AMT_CREDIT | Credit amount |
| input-2 | AMT_ANNUITY | Loan annuity amount |
| input-3 | AMT_GOODS_PRICE | Price of goods |
| input-4 | DAYS_BIRTH | Age in days (negative, -365 = 1 year old) |
| input-5 | DAYS_EMPLOYED | Employment length in days |
| input-6 | REGION_POPULATION_RELATIVE | Region population density |
| input-7 | CNT_FAM_MEMBERS | Number of family members |
| input-8+ | Binary/Categorical | FLAG_MOBIL, FLAG_EMAIL, etc. + one-hot encoded categories |

## Generating Data for Monitoring

TrustyAI needs prediction data to calculate bias metrics. You have two options:

### Option 1: Use Your Web Application
Simply use your loan prediction web app normally. Each prediction will be logged to TrustyAI automatically.

### Option 2: Send Test Predictions (Already Done!)
I created a script that sent 100 test predictions:
```bash
cd /Users/ctham/Code/microfinanceloanocpai/PredictiveModelWorkbench
python3 send_test_predictions.py
```

However, note: **The logging might not be working yet** (we were troubleshooting the logger URL). You may need to:

1. Check if predictions are flowing: Use your web app and submit a few loan applications
2. Verify in dashboard: Go to **Model metrics** to see if data appears
3. If still no data: The InferenceService logger configuration may need adjustment

## Viewing Bias Metrics

Once configured and data flows:

1. Go to **Model serving** → **Deployed models**
2. Find `microloan-xgboost`
3. Click on it → **Metrics** tab
4. You'll see:
   - Bias trend over time
   - Current SPD/DIR values
   - Alerts if threshold is exceeded
   - Data drift metrics (if configured)

## Recommended Metrics for Loan Models

Create these 3 bias metrics for comprehensive fairness monitoring:

1. **Income Fairness** (High vs Low income applicants)
2. **Age Fairness** (Young vs Older applicants)  
3. **Employment Fairness** (Long-term vs Short-term employed)

## Why This Matters for Your Demo

With bias monitoring, you can demonstrate:

✅ **Regulatory Compliance** - Show you monitor for fair lending practices  
✅ **Responsible AI** - Complete pipeline: XGBoost predictions → LLM explanations → Bias monitoring  
✅ **Production Readiness** - Enterprise-grade ML Ops with fairness guarantees  
✅ **Trust & Transparency** - Stakeholders can see the model is fair  

## Troubleshooting

### "Bias metrics for this model have not been configured"
- Normal on first setup - click "Configure metric" to add one

### "No data available"
- Send predictions through your model (use web app or test script)
- Check InferenceService has logger configured: `oc get inferenceservice microloan-xgboost -o yaml | grep logger`
- May take a few minutes for data to appear

### "Metric calculation failed"
- Ensure you have enough data (at least 100 predictions)
- Verify protected attribute exists in your input data
- Check that privileged/unprivileged values match your data range

## Next Steps

1. **Configure your first metric** using the dashboard (screenshot 2 shows the form)
2. **Generate prediction data** by using your web application
3. **Monitor results** in the Model metrics view
4. **Set up alerts** for bias threshold violations
5. **Create additional metrics** for comprehensive fairness monitoring

## Files Created for Reference

- `TRUSTYAI_SETUP.md` - Detailed setup guide with CLI approach
- `send_test_predictions.py` - Script to generate test predictions
- `prepare_trustyai_data.py` - Data preparation utilities

## Support

If you encounter issues:
- Check TrustyAI service logs: `oc logs -l app=trustyai-service -n a-rh-department`
- Verify InferenceService config: `oc describe inferenceservice microloan-xgboost -n a-rh-department`
- Review TrustyAI documentation: https://trustyai.org/docs/
