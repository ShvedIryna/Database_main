import requests
import time
import random
import threading
import argparse
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class LoadGenerator:
    def __init__(self, base_url, num_threads=10, duration=300, ramp_up=30):
        self.base_url = base_url.rstrip('/')
        self.num_threads = num_threads
        self.duration = duration
        self.ramp_up = ramp_up

        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        self.stats_lock = threading.Lock()
        self.start_time = None
        self.running = False

        self.endpoints = [
            ('GET', '/api/movies'),
            ('GET', '/api/actors'),
        ]

    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    def make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method == 'GET':
                response = requests.get(url, timeout=15, verify=True)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=15, verify=True)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=15, verify=True)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=15, verify=True)
            else:
                return False, 0

            response_time = (time.time() - start_time) * 1000

            with self.stats_lock:
                self.stats['total_requests'] += 1
                if 200 <= response.status_code < 300:
                    self.stats['successful_requests'] += 1
                else:
                    self.stats['failed_requests'] += 1
                    self.stats['errors'].append(f"{method} {endpoint}: {response.status_code}")
                self.stats['response_times'].append(response_time)

            return response.status_code < 400, response_time

        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            with self.stats_lock:
                self.stats['total_requests'] += 1
                self.stats['failed_requests'] += 1
                self.stats['errors'].append(f"{method} {endpoint}: {str(e)}")
                self.stats['response_times'].append(response_time)
            return False, response_time

    def generate_load(self, thread_id):
        requests_count = 0

        while self.running:
            method, endpoint = random.choice(self.endpoints)

            if endpoint == '/api/movies' and random.random() < 0.2:
                movie_data = {
                    'title': f'Test Movie {random.randint(1000, 9999)}',
                    'release_year': random.randint(2000, 2024),
                    'duration': random.randint(90, 180),
                    'description': 'Test movie description'
                }
                self.make_request('POST', '/api/movies', movie_data)
            else:
                self.make_request(method, endpoint)

            requests_count += 1

            delay = random.uniform(0.01, 0.3)
            time.sleep(delay)

        self.log(f"Thread {thread_id} completed: {requests_count} requests")

    def run(self):
        self.log(f"Starting load generator")
        self.log(f"URL: {self.base_url}")
        self.log(f"Threads: {self.num_threads}")
        self.log(f"Duration: {self.duration} seconds")
        self.log(f"Ramp-up: {self.ramp_up} seconds")

        try:
            response = requests.get(f"{self.base_url}/swagger/", timeout=5)
            if response.status_code != 200:
                self.log(f"Warning: service responded with code {response.status_code}", 'WARNING')
        except Exception as e:
            self.log(f"Warning: failed to verify service: {e}", 'WARNING')

        self.start_time = time.time()
        self.running = True

        threads = []
        threads_per_second = max(1, self.num_threads / self.ramp_up)

        self.log("Starting ramp-up period...")
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.generate_load, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

            if i < self.num_threads - 1:
                time.sleep(self.ramp_up / self.num_threads)

        self.log("All threads started. Waiting for completion...")

        try:
            time.sleep(self.duration)
        except KeyboardInterrupt:
            self.log("Interrupt signal received", 'WARNING')

        self.running = False
        self.log("Stopping threads...")

        for thread in threads:
            thread.join(timeout=5)

        elapsed_time = time.time() - self.start_time
        self.print_stats(elapsed_time)

    def print_stats(self, elapsed_time):
        print("\n" + "="*60)
        print("LOAD GENERATOR STATISTICS")
        print("="*60)
        print(f"Execution time: {elapsed_time:.2f} seconds")
        print(f"Total requests: {self.stats['total_requests']}")
        print(f"Successful requests: {self.stats['successful_requests']}")
        print(f"Failed requests: {self.stats['failed_requests']}")

        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
            print(f"Success rate: {success_rate:.2f}%")
            print(f"Requests per second: {self.stats['total_requests'] / elapsed_time:.2f}")

        if self.stats['response_times']:
            avg_time = statistics.mean(self.stats['response_times'])
            median_time = statistics.median(self.stats['response_times'])
            min_time = min(self.stats['response_times'])
            max_time = max(self.stats['response_times'])

            print(f"\nResponse time (ms):")
            print(f"  Average: {avg_time:.2f}")
            print(f"  Median: {median_time:.2f}")
            print(f"  Minimum: {min_time:.2f}")
            print(f"  Maximum: {max_time:.2f}")

            if len(self.stats['response_times']) > 1:
                std_dev = statistics.stdev(self.stats['response_times'])
                print(f"  Standard deviation: {std_dev:.2f}")

        if self.stats['errors']:
            print(f"\nLast 10 errors:")
            for error in self.stats['errors'][-10:]:
                print(f"  - {error}")

        print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Load generator for REST API')
    parser.add_argument('--url', '-u', required=True, help='Base URL of REST service')
    parser.add_argument('--threads', '-t', type=int, default=10, help='Number of parallel threads (default: 10)')
    parser.add_argument('--duration', '-d', type=int, default=300, help='Test duration in seconds (default: 300)')
    parser.add_argument('--ramp-up', '-r', type=int, default=30, help='Ramp-up time in seconds (default: 30)')

    args = parser.parse_args()

    generator = LoadGenerator(
        base_url=args.url,
        num_threads=args.threads,
        duration=args.duration,
        ramp_up=args.ramp_up
    )

    try:
        generator.run()
    except KeyboardInterrupt:
        print("\nLoad generator interrupted...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
