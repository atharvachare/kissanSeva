"""
KisanSeva Integration Test & Debugging Helper
Tests the ML-Frontend integration
"""

import requests
import json
import base64
import sys
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(status, message):
    """Print colored status message"""
    if status == 'success':
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    elif status == 'error':
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    elif status == 'info':
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")
    elif status == 'warn':
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")

def test_backend_connection(backend_url='http://localhost:5000'):
    """Test if backend is running"""
    print(f"\n{Colors.BOLD}1. Testing Backend Connection{Colors.RESET}")
    try:
        response = requests.get(f'{backend_url}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status('success', f"Backend is running: {data['service']} v{data['version']}")
            return True
        else:
            print_status('error', f"Backend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_status('error', f"Cannot connect to {backend_url}")
        print_status('info', "Make sure to run: python backend.py")
        return False
    except Exception as e:
        print_status('error', f"Connection error: {str(e)}")
        return False

def test_models_loaded(backend_url='http://localhost:5000'):
    """Test if ML models are loaded"""
    print(f"\n{Colors.BOLD}2. Testing ML Models{Colors.RESET}")
    try:
        response = requests.get(f'{backend_url}/api/models-info', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status('success', "Models information retrieved:")
            for model, path in data['models'].items():
                print(f"  - {model}: {path}")
            print(f"  Input size: {data['input_size']}")
            print(f"  Languages: {', '.join(data['supported_languages'])}")
            return True
        else:
            print_status('error', f"Failed to get models info: {response.status_code}")
            return False
    except Exception as e:
        print_status('error', f"Models check failed: {str(e)}")
        return False

def test_image_analysis(test_image_path, backend_url='http://localhost:5000', language='hindi'):
    """Test image analysis with a test image"""
    print(f"\n{Colors.BOLD}3. Testing Image Analysis{Colors.RESET}")
    
    if not Path(test_image_path).exists():
        print_status('error', f"Test image not found: {test_image_path}")
        print_status('info', "Available test images in test_images/ folder")
        return False
    
    try:
        # Read and encode image
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        print_status('info', f"Analyzing: {test_image_path} (language: {language})")
        
        # Send request
        response = requests.post(
            f'{backend_url}/api/analyze',
            json={
                'image': f'data:image/jpeg;base64,{image_data}',
                'language': language
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'success':
                print_status('success', "Analysis completed successfully!")
                print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
                print(f"  Crop: {data['cropName']}")
                print(f"  Disease: {data['diseaseName']}")
                print(f"  Confidence: {data['confidence']} ({data['confidenceScore']})")
                print(f"  Status: {data['healthStatus']}")
                
                if 'recommendations' in data:
                    recs = data['recommendations']
                    if isinstance(recs, dict):
                        print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
                        if 'Crop' in recs:
                            print(f"  Crop: {recs['Crop']}")
                        if 'Disease' in recs:
                            print(f"  Disease: {recs['Disease']}")
                        if 'Identification' in recs and recs['Identification']:
                            print(f"  Identification:")
                            for item in recs['Identification'][:2]:
                                print(f"    - {item}")
                        if 'Treatment' in recs and recs['Treatment']:
                            print(f"  Treatment:")
                            for item in recs['Treatment'][:2]:
                                print(f"    - {item}")
                
                return True
            else:
                print_status('warn', f"Status: {data['status']}")
                if 'message' in data:
                    print_status('info', f"Message: {data['message']}")
                return False
        else:
            print_status('error', f"Server error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_status('error', f"Analysis failed: {str(e)}")
        return False

def test_file_upload(test_image_path, backend_url='http://localhost:5000', language='hindi'):
    """Test image analysis with file upload endpoint"""
    print(f"\n{Colors.BOLD}4. Testing File Upload Endpoint{Colors.RESET}")
    
    if not Path(test_image_path).exists():
        print_status('error', f"Test image not found: {test_image_path}")
        return False
    
    try:
        print_status('info', f"Uploading: {test_image_path}")
        
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {'language': language}
            
            response = requests.post(
                f'{backend_url}/api/analyze-url',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                print_status('success', "File upload and analysis successful!")
                return True
            else:
                print_status('warn', f"Status: {result['status']}")
                return False
        else:
            print_status('error', f"Upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_status('error', f"Upload test failed: {str(e)}")
        return False

def find_test_images():
    """Find available test images"""
    test_dir = Path('test_images')
    if test_dir.exists():
        images = list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.png'))
        return images
    return []

def main():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{'='*50}")
    print("  KisanSeva Integration Test Suite")
    print(f"{'='*50}{Colors.RESET}\n")
    
    # Get backend URL
    backend_url = 'http://localhost:5000'
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
    
    print_status('info', f"Backend URL: {backend_url}")
    
    # Run tests
    results = {
        'Backend Connection': test_backend_connection(backend_url),
        'Models Loaded': test_models_loaded(backend_url),
    }
    
    # Test with images
    test_images = find_test_images()
    if test_images:
        print_status('info', f"Found {len(test_images)} test image(s)")
        
        # Use first image
        test_image = test_images[0]
        print(f"\n{Colors.BOLD}Image Analysis Tests{Colors.RESET}")
        print_status('info', f"Using: {test_image.name}")
        
        # Test base64 endpoint
        results['Base64 Analysis'] = test_image_analysis(str(test_image), backend_url, 'hindi')
        
        # Test file upload endpoint
        results['File Upload'] = test_file_upload(str(test_image), backend_url, 'hindi')
    else:
        print_status('warn', "No test images found in test_images/")
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*50}")
    print("  Test Summary")
    print(f"{'='*50}{Colors.RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_status('success', f"{test_name}: PASSED")
        else:
            print_status('error', f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print_status('success', "All tests passed! Ready for development.")
        return 0
    else:
        print_status('error', "Some tests failed. Check errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
