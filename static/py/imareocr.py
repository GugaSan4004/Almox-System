import os, json

import io
import time
import datetime
from pdf2image import convert_from_path
from google.oauth2.service_account import Credentials

class init:
    def __init__(self, path, vision_db):
        raw = os.environ.get("GOOGLE_VISION_JSON")
        
        if not raw:
            raise SystemExit("Credencial Google Vision não configurada")

        self.credentials = Credentials.from_service_account_info(
            json.loads(raw),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        os.environ["PATH"] += os.pathsep + r"C:\poppler\Library\bin"

        from google.cloud import vision_v1
        from google.cloud import monitoring_v3
        from google.protobuf import timestamp_pb2
        
        self.vision = vision_v1
        self.vision_db = vision_db
        self.timestamp = timestamp_pb2
        self.monitoring = monitoring_v3
        self.project_id = "rock-tower-480410-d2"
        
    def can_i_run(self) -> bool:
        today = datetime.datetime.now()
        day = today.day
        today_str = today.date().isoformat()

        if day < 18:
            self.vision_db.clearUsage()
            return True

        baseline, baseline_date = self.vision_db.getUsage()
        
        
        already_ran_today = (baseline_date == today_str)
        
        should_refresh = (
            (baseline is None and day >= 18) or
            (day in (18, 25) and not already_ran_today)
        )
        
        
        if should_refresh:
            client = self.monitoring.MetricServiceClient()
            project_name = f"projects/{self.project_id}"

            now = datetime.datetime.now(datetime.timezone.utc)
            start_of_month = datetime.datetime(now.year, now.month, 1)

            end_time = self.timestamp.Timestamp()
            end_time.FromDatetime(now)
            start_time = self.timestamp.Timestamp()
            start_time.FromDatetime(start_of_month)

            interval = self.monitoring.TimeInterval(end_time=end_time, start_time=start_time)
            
            filter_str = (
                f'metric.type="serviceruntime.googleapis.com/api/request_count" AND '
                f'resource.labels.project_id="{self.project_id}"'
            )

            aggregation = self.monitoring.Aggregation(
                alignment_period={"seconds": 600},
                per_series_aligner=self.monitoring.Aggregation.Aligner.ALIGN_SUM,
                cross_series_reducer=self.monitoring.Aggregation.Reducer.REDUCE_SUM
            )
            
            results = client.list_time_series(
                request={
                    "name": project_name,
                    "filter": filter_str,
                    "interval": interval,
                    "view": self.monitoring.ListTimeSeriesRequest.TimeSeriesView.FULL,
                    "aggregation": aggregation,
                },
                timeout=10.0
            )

            total_requests = 0
            for result in results:
                for point in result.points:
                    total_requests += point.value.int64_value
                    
            total_requests += 1
            
            self.vision_db.setUsage(total_requests)
            baseline = total_requests

        return baseline < 980

    def load_image(self, img_path: str):
        if img_path.lower().endswith(".pdf"):
            pages = convert_from_path(img_path, dpi=200)
            temp_img = img_path.replace(".pdf", "_page1.jpg")
            pages[0].save(temp_img, "JPEG")
            return temp_img
        
        return img_path

    def extractText(self, path):
        if(self.can_i_run()):
            path = self.load_image(path)
            client = self.vision.ImageAnnotatorClient(credentials=self.credentials)

            with io.open(path, "rb") as img_file:
                content = img_file.read()

            image = self.vision.Image(content=content)

            image_context = self.vision.ImageContext(
                language_hints=["mul-Latn-t-i0-handwrit"]
            )
            response = client.document_text_detection( # type: ignore
                image=image, image_context=image_context
            )

            text = response.full_text_annotation.text

            return text.replace("»", "").replace("«", "").replace("(", "").replace(")", "")
        else:
            return ""