from google.cloud import monitoring_v3
import time

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/rock-tower-480410-d2"

now = time.time()
seconds = int(now)
nanos = int((now - seconds) * 10 ** 9)
interval = monitoring_v3.TimeInterval(
    {
        "end_time": {"seconds": seconds, "nanos": nanos},
        "start_time": {"seconds": (seconds - 1200), "nanos": nanos},
    }
)


results = client.list_time_series(
    request={
        "name": project_name,
        "filter": 'metric.type = "serviceruntime.googleapis.com/api/request_count" AND resource.labels.method = "compute.v1.ZonesService.List"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }
)

print(results)