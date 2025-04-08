import requests
import concurrent.futures
from urllib.parse import urljoin


BASE_URL = ""
MAX_DEPTH = 3 
MAX_WORKERS = 10 
TIMEOUT = 5


PATH_SUFFIXES = [
    "/a/../",
    "/a/..;/",
    "/.;/"
]

def generate_path_variants(base_path):

    variants = [base_path]
    
    def recurse(current_paths, depth):
        if depth >= MAX_DEPTH:
            return
        new_paths = []
        for path in current_paths:
            for suffix in PATH_SUFFIXES:
                new_path = path + suffix
                new_paths.append(new_path)
                variants.append(new_path)
        recurse(new_paths, depth + 1)
    
    recurse([base_path], 1)
    return list(set(variants)) 

def load_endpoints(file_path):

    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def test_url(url):

    try:
        response = requests.get(url, timeout=TIMEOUT, allow_redirects=False)
        return (url, response.status_code, len(response.content))
    except requests.exceptions.RequestException as e:
        return (url, str(e), 0)

def main():
 
    endpoints = load_endpoints("Pasted_Text_1744091565862.txt")
    

    all_urls = []
    for endpoint in endpoints:
        variants = generate_path_variants(endpoint)
        all_urls.extend(variants)
    

    full_urls = [urljoin(BASE_URL, url) for url in all_urls]
    

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(test_url, url): url for url in full_urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                url, status, length = future.result()
                print(f"[{status}] ({length}B) {url}")
            except Exception as e:
                print(f"Error: {url} - {str(e)}")

if __name__ == "__main__":
    main()
