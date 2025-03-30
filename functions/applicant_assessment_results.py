import pandas as pd

# Step 7: Affordability assessment

def assess_affordability(required_amount, conservative_forecast, optimistic_forecast):
    """
    Assess if the applicant is likely to meet the required threshold
    """
    if conservative_forecast >= required_amount:
        return {
            'assessment': 'High confidence',
            'probability': 'Over 90%',
            'recommendation': 'Approve',
            'buffer': conservative_forecast - required_amount
        }
    elif optimistic_forecast >= required_amount:
        return {
            'assessment': 'Moderate confidence',
            'probability': '50-90%',
            'recommendation': 'Approve with monitoring',
            'buffer': optimistic_forecast - required_amount
        }
    else:
        return {
            'assessment': 'Low confidence',
            'probability': 'Under 50%',
            'recommendation': 'Request additional financial guarantees',
            'buffer': optimistic_forecast - required_amount
        }


#  Combine results and hyper parametres into a data frame
    
def get_overall_assessment (experiment_id, required_amount, affordability_assessment, train_data, 
                            final_p10, final_median, final_p90, actual_final=None, error=None, 
                            within_interval=None):

    # Create dictionaries for each section
    affordability_data = {
        'Required amount': f"£{required_amount:.2f}",
        'Assessment': affordability_assessment['assessment'],
        'Probability of meeting threshold': affordability_assessment['probability'],
        'Recommendation': affordability_assessment['recommendation'],
        'Buffer amount (median forecast)': f"£{affordability_assessment['buffer']:.2f}"
    }

    forecast_data = {
        'Current balance': f"£{train_data['balance'].iloc[-1]:.2f}",
        'Forecast for 30 days later (median)': f"£{final_median:.2f}",
        'Conservative forecast (10th percentile)': f"£{final_p10:.2f}",
        'Optimistic forecast (90th percentile)': f"£{final_p90:.2f}",
        'Forecast range width': f"£{final_p90 - final_p10:.2f}"
    }

    ###################### If block for when used for future forecasting when the actual future balance is not known ###################### 
    # Check if comparative metrics have data and format accordingly
    if actual_final is not None and not pd.isna(actual_final):
        actual_final_value = f"£{actual_final:.2f}"
    else:
        actual_final_value = "No data"

    if error is not None and not pd.isna(error) and actual_final is not None and not pd.isna(actual_final):
        error_value = f"£{error:.2f} ({100 * error / actual_final:.2f}%)"
    else:
        error_value = "No data"

    if within_interval is not None and not pd.isna(within_interval):
        within_interval_value = within_interval
    else:
        within_interval_value = "No data"
    ###################### End: If block for when used for future forecasting when the actual future balance is not known ###################### 



    comparative_data = {
        'Actual final balance': actual_final_value,
        'Forecast error': error_value,
        'Actual balance within 80% prediction interval': within_interval_value
    }

    # Create a DataFrame with separate sections
    overall_assessment_df = pd.DataFrame({
        'Category': ['Affordability'] * len(affordability_data) + 
                    ['Forecast'] * len(forecast_data) + 
                    ['Comparative'] * len(comparative_data),
        'Metric': list(affordability_data.keys()) + list(forecast_data.keys()) + list(comparative_data.keys()),
        'Value': list(affordability_data.values()) + list(forecast_data.values()) + list(comparative_data.values())
    })

    overall_assessment_df['ExperimentID'] = experiment_id

    return overall_assessment_df