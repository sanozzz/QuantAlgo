import pytest
import pandas as pd
from unittest.mock import Mock
from data_handler.data_fetcher import DataFetcher

# Load the sample data
sample_data_path = '/Users/sandeeparora/PycharmProjects/QuantAlgo/Sample_df.csv'  # Ensure this path is correct
sample_data = pd.read_csv(sample_data_path)

# Drop the 'Unnamed: 0' column if it exists
if 'Unnamed: 0' in sample_data.columns:
    sample_data.drop(columns=['Unnamed: 0'], inplace=True)

# Create a mock broker API
mock_broker_api = Mock()


def test_fetch_historical_data():
    # Initialize DataFetcher with the mock broker API
    data_fetcher = DataFetcher(mock_broker_api)

    # Mock the return value of the broker API's get_historical_data method
    mock_broker_api.get_historical_data.return_value = sample_data.to_dict(orient='records')

    # Fetch the data using DataFetcher
    historical_data = data_fetcher.fetch_historical_data('AAPL', '1d', '2024-06-01', '2024-06-02')

    # Ensure that historical_data is a DataFrame
    assert isinstance(historical_data, pd.DataFrame), f"Expected DataFrame, got {type(historical_data)}"

    # Compare the fetched data with the sample data
    pd.testing.assert_frame_equal(historical_data.reset_index(drop=True), sample_data)


def test_fetch_intraday_data():
    # Initialize DataFetcher with the mock broker API
    data_fetcher = DataFetcher(mock_broker_api)

    # Mock the return value of the broker API's get_intraday_data method
    mock_broker_api.get_intraday_data.return_value = sample_data.to_dict(orient='records')

    # Fetch the data using DataFetcher
    intraday_data = data_fetcher.fetch_intraday_data('AAPL', '1min')

    # Ensure that intraday_data is a DataFrame
    assert isinstance(intraday_data, pd.DataFrame), f"Expected DataFrame, got {type(intraday_data)}"

    # Compare the fetched data with the sample data
    pd.testing.assert_frame_equal(intraday_data.reset_index(drop=True), sample_data)
