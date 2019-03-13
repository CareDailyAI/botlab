# Data Requests

This microservice package requests all "important" time-series data history from the Location at least once per week (2 AM on Saturday), to deliver into other machine learning services for the purpose of model generation.

The historical data is extracted from the database in a way that is friendly to scaling machine learning services across millions of accounts.

Please see `com.ppc.Lesson10-MachineLearning` for more details.

### Data Stream Messages

* `download_data` : Request that we download all data from the user's account now.