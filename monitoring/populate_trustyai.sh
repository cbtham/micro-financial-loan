#!/bin/bash
#
# Quick fix: Send predictions to microloan-xgboost and verify TrustyAI logging
#

echo "============================================"
echo "TrustyAI Data Population - Quick Fix"
echo "============================================"
echo ""

# Step 1: Send predictions through the model
echo "Step 1: Sending 20 test predictions to microloan-xgboost..."
echo ""

MODEL_URL="https://microloan-xgboost-a-rh-department.apps.cluster-94v2k.94v2k.sandbox393.opentlc.com/v2/models/microloan-xgboost/infer"

# Send a few predictions
for i in {1..20}; do
  curl -sk $MODEL_URL \
    -H "Content-Type: application/json" \
    -d '{
      "inputs": [{
        "name": "predict",
        "shape": [1, 49],
        "datatype": "FP64",
        "data": [[207000.0, 465457.5, 52641.0, 418500.0, -13297.0, -762.0, 0.00963, 4.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]]
      }]
    }' > /dev/null 2>&1
  
  if [ $((i % 5)) -eq 0 ]; then
    echo "  ✓ Sent $i predictions"
  fi
done

echo ""
echo "✓ Sent 20 predictions to microloan-xgboost"
echo ""

# Step 2: Wait a moment for logging
echo "Step 2: Waiting 5 seconds for TrustyAI to process..."
sleep 5

# Step 3: Check if TrustyAI has the data
echo ""
echo "Step 3: Checking TrustyAI for model data..."
export TOKEN=$(oc whoami -t)
export TRUSTY_ROUTE=https://$(oc get route/trustyai-service -n a-rh-department --template={{.spec.host}})

MODELS=$(curl -sk -H "Authorization: Bearer ${TOKEN}" $TRUSTY_ROUTE/info 2>/dev/null | jq -r 'keys[]' 2>/dev/null)

if [ -z "$MODELS" ]; then
  echo "⚠ No models found in TrustyAI yet"
  echo ""
  echo "This means the logger isn't working. Let's check the InferenceService..."
  echo ""
  oc get inferenceservice microloan-xgboost -n a-rh-department -o jsonpath='{.spec.predictor.logger}' | jq '.'
  echo ""
  echo "Possible issues:"
  echo "1. Logger URL might be incorrect (should be internal service URL)"
  echo "2. TrustyAI service might need restart"
  echo "3. Predictions might not be flowing through the logger"
else
  echo "✓ Found models in TrustyAI:"
  echo "$MODELS"
  echo ""
  echo "You can now configure bias metrics for these models!"
fi

echo ""
echo "============================================"
