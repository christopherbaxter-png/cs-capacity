# CSM capacity model

A starter model for estimating monthly CSM workload against available portfolio hours.

## Files
- `CSM_Capacity_Model.xlsx`: the workbook (Inputs, Demand, Capacity, Scenarios)
- `build.py`: script that regenerates the workbook with openpyxl

## Using the model
1. Replace the yellow input cells on the **Inputs** tab.
2. Read the result on the **Capacity** tab (utilisation, status, CSMs needed).
3. Test scenarios on the **Scenarios** tab by editing the blue cells.

## Important
All starting numbers are illustrative placeholders, not real data. Replace account counts, headcount, hours per touchpoint and reactive hours before using the results.

Touchpoint cadences follow the value realisation touchpoint map (five stages). Health-score bands are not used.
