import datetime
import os


class BaseCrawler:
    """
    Base class for all crawlers.
    """

    def __init__(self, topic: str, desc: str, tags: list, source_desc: str):
        self.topic = topic
        self.desc = desc
        self.tags = tags
        self.source_desc = source_desc
        
        self.raw_data = None
        self.processed_data = None

    def crawl(self):
        """
        Crawls and returns the raw content.
        """
        raise NotImplementedError
    
    def process(self):
        """
        Processes the raw content and returns the processed content.
        """
        raise NotImplementedError
    
    def export_csv(self, path: str):
        """
        Exports the processed data to a CSV file.
        """
        assert self.processed_data is not None, "No data to export."
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        self.processed_data.to_csv(path)
    
    def _handle_crawl_failure(self, req):
        """
        Handles the failure of a request.
        """
        logger.error(f"Failed to crawl data for {self.topic}")
        logger.error(f"Request failed with status code {req.status_code}")
        logger.error(f"Response: {req.text}")
        raise Exception("Request failed")
    
    def _gen_default_export_name(self):
        """
        Generates a default export name.
        """
        current_time = datetime.datetime.now().strftime("%Y%m%d")
        return f"{self.topic.replace(' ', '_').lower()}/{current_time}.csv"