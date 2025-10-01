I'll help you set up your project with uv, which is a fast Python package manager. Here's a complete setup:

1. Install uv
First, install uv if you haven't already:

bash
Copy code
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
2. Initialize Your Project
Navigate to your repo and initialize the project:

bash
Copy code
cd spending-money-on-apis

# Initialize a new Python project with uv
uv init

# This creates a pyproject.toml file
3. Set Up pyproject.toml
Edit the generated pyproject.toml:

toml
Copy code
[project]
name = "spending-money-on-apis"
version = "0.1.0"
description = "Examples of using paid APIs"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
4. Create Project Structure
bash
Copy code
# Create directory structure
mkdir -p src/spending_money_on_apis
mkdir -p tests
mkdir -p examples

# Create __init__.py files
touch src/spending_money_on_apis/__init__.py
touch tests/__init__.py

# Move your code to the appropriate location
touch src/spending_money_on_apis/google_maps.py
5. Update Your Code Structure
Move the Google Maps code to src/spending_money_on_apis/google_maps.py:

python
Copy code
# src/spending_money_on_apis/google_maps.py
import os
import requests
from pathlib import Path
from urllib.parse import urlencode
from typing import Optional, List, Dict, Union

class GoogleStaticMaps:
    """Client for Google Static Maps API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("API key required. Set GOOGLE_MAPS_API_KEY or pass api_key parameter")
        self.base_url = "https://maps.googleapis.com/maps/api/staticmap"
    
    def get_map(
        self,
        center: Optional[str] = None,
        zoom: int = 13,
        size: str = "600x400",
        maptype: str = "roadmap",
        markers: Optional[List[Dict[str, str]]] = None,
        path: Optional[str] = None,
        save_as: Optional[Union[str, Path]] = None
    ) -> Union[bytes, bool]:
        """Fetch a static map from Google Maps API"""
        
        params = {
            'key': self.api_key,
            'size': size,
            'maptype': maptype,
            'zoom': zoom
        }
        
        if center:
            params['center'] = center
        
        if markers:
            marker_strings = []
            for marker in markers:
                marker_parts = []
                for key in ['color', 'label', 'size']:
                    if key in marker:
                        marker_parts.append(f"{key}:{marker[key]}")
                if 'location' in marker:
                    marker_parts.append(marker['location'])
                marker_strings.append('|'.join(marker_parts))
            params['markers'] = marker_strings
        
        if path:
            params['path'] = path
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        if save_as:
            save_path = Path(save_as)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(response.content)
            return True
        
        return response.content
    
    def get_map_url(self, **kwargs) -> str:
        """Generate a URL for a static map"""
        params = {k: v for k, v in kwargs.items() if v is not None}
        params['key'] = self.api_key
        return f"{self.base_url}?{urlencode(params)}"
6. Create an Example Script
Create examples/google_maps_example.py:

python
Copy code
#!/usr/bin/env python3
from pathlib import Path
from dotenv import load_dotenv
from spending_money_on_apis.google_maps import GoogleStaticMaps

# Load environment variables
load_dotenv()

def main():
    # Initialize client
    maps = GoogleStaticMaps()
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Example 1: Simple map
    maps.get_map(
        center="Times Square, New York, NY",
        zoom=15,
        save_as=output_dir / "times_square.png"
    )
    print("✓ Saved Times Square map")
    
    # Example 2: Map with markers
    maps.get_map(
        center="San Francisco, CA",
        zoom=12,
        markers=[
            {'color': 'red', 'label': 'G', 'location': 'Golden Gate Bridge, San Francisco, CA'},
            {'color': 'blue', 'label': 'A', 'location': 'Alcatraz Island, San Francisco, CA'}
        ],
        save_as=output_dir / "sf_landmarks.png"
    )
    print("✓ Saved San Francisco landmarks map")
    
    # Example 3: Get URL only
    url = maps.get_map_url(
        center="Grand Canyon, AZ",
        zoom=11,
        maptype="satellite"
    )
    print(f"✓ Generated URL: {url[:50]}...")

if __name__ == "__main__":
    main()
7. Install Dependencies with uv
bash
Copy code
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the project and dependencies
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"
8. Create a Simple Test
Create tests/test_google_maps.py:

python
Copy code
import pytest
from spending_money_on_apis.google_maps import GoogleStaticMaps

def test_api_key_required():
    """Test that API key is required"""
    with pytest.raises(ValueError):
        GoogleStaticMaps(api_key=None)

def test_url_generation():
    """Test URL generation"""
    maps = GoogleStaticMaps(api_key="test_key")
    url = maps.get_map_url(center="New York, NY", zoom=10)
    assert "center=New+York%2C+NY" in url
    assert "zoom=10" in url
    assert "key=test_key" in url
9. Update .gitignore
bash
Copy code
# .gitignore
.env
*.png
*.jpg
output/
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.ruff_cache/
10. Create README.md
markdown
Copy code
# Spending Money on APIs

Examples of using paid APIs with Python.

## Setup

1. Install uv: https://github.com/astral-sh/uv
2. Clone this repo
3. Create `.env` file with your API keys
4. Install dependencies: `uv pip install -e .`

## Examples

### Google Static Maps

```bash
python examples/google_maps_example.py
