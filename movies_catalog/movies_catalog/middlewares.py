import time
import logging
logger = logging.getLogger(__name__)
class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()
        response = self.get_response(request)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Total request time for request:{request.get_full_path()} {total_time:.4f} seconds")
        return response
