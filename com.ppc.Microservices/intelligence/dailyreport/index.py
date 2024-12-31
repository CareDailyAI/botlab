MICROSERVICES = {
    # Map locations to their microservices
    "LOCATION_MICROSERVICES": [
        {
            "module": "intelligence.dailyreport.location_dailyreport_microservice",
            "class": "LocationDailyReportMicroservice"
        },
        {
            "module": "intelligence.dailyreport.location_dailyreport_gpt_microservice",
            "class": "LocationDailyReportGPTMicroservice"
        },
        {
            "module": "intelligence.dailyreport.location_dailyreport_summary_microservice",
            "class": "LocationDailyReportSummaryMicroservice"
        }
    ]
}
