"""
Screenshot parser for extracting test cases from images using AI vision models.

This module provides functionality to upload screenshots to AI APIs and generate
test cases based on visual analysis and prompts.
"""

import base64
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from PIL import Image

from ...utils.logging import get_logger, log_api_call, log_file_operation
from ...utils.validators import validate_file_path
from ..models import TestCase, TestCaseType, Priority


class ScreenshotParser:
    """Parser for extracting test cases from screenshots using AI vision models."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the screenshot parser.
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config or {}
        self.logger = get_logger()
        
        # AI API configuration
        self.api_key = self.config.get('api_key')
        self.api_url = self.config.get('api_url', 'https://api.openai.com/v1/chat/completions')
        self.model = self.config.get('model', 'gpt-4-vision-preview')
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.temperature = self.config.get('temperature', 0.7)
        
        # Image processing settings
        self.max_image_size = self.config.get('max_image_size', (1024, 1024))
        self.supported_formats = self.config.get('supported_formats', ['png', 'jpg', 'jpeg', 'bmp', 'tiff'])
        self.quality = self.config.get('quality', 85)
    
    def encode_image(self, image_path: Union[str, Path]) -> str:
        """Encode image to base64 for API upload.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
            
        Raises:
            ValueError: If image format is not supported
            FileNotFoundError: If image file doesn't exist
        """
        image_path = Path(image_path)
        
        if not validate_file_path(image_path, must_exist=True):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Check file format
        file_extension = image_path.suffix.lower().lstrip('.')
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {file_extension}. "
                           f"Supported formats: {self.supported_formats}")
        
        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.size > self.max_image_size:
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                
                # Save to bytes
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=self.quality)
                buffer.seek(0)
                
                # Encode to base64
                image_data = buffer.getvalue()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                log_file_operation("encode_image", str(image_path), success=True)
                return base64_image
                
        except Exception as e:
            log_file_operation("encode_image", str(image_path), success=False)
            self.logger.error(f"Error encoding image {image_path}: {e}")
            raise
    
    def create_vision_prompt(self, test_types: List[str], additional_context: str = "") -> str:
        """Create a prompt for AI vision model to generate test cases.
        
        Args:
            test_types: List of test case types to generate
            additional_context: Additional context for the AI
            
        Returns:
            Formatted prompt string
        """
        test_types_str = ", ".join(test_types)
        
        prompt = f"""You are a test case generator. Analyze the provided screenshot and generate comprehensive test cases.

**Test Case Types to Generate:**
{test_types_str}

**Instructions:**
1. Identify all interactive elements (buttons, inputs, dropdowns, links, etc.)
2. Identify all data fields and their constraints
3. Identify user flows and navigation paths
4. Identify potential error states and edge cases
5. Generate test cases covering functional, boundary, negative, and security scenarios

**Output Format:**
For each test case, provide:
- Test Case ID (format: TC-XXX)
- Title (descriptive and specific)
- Test Type (FUNC/BOUND/NEG/PERM/SEC/PERF/A11Y)
- Priority (P0/P1/P2/P3)
- Preconditions (if any)
- Test Steps (numbered list)
- Expected Result
- Covered Elements (list of UI elements tested)

**Additional Context:**
{additional_context}

**Example Output:**
```
TC-001: User Login - Valid Credentials
Type: FUNC
Priority: P0
Preconditions: User is on login page
Steps:
1. Enter valid username in username field
2. Enter valid password in password field
3. Click login button
Expected Result: User is successfully logged in and redirected to dashboard
Covered Elements: username field, password field, login button
```

Please analyze the screenshot and generate test cases following this format."""

        return prompt
    
    def call_vision_api(self, image_base64: str, prompt: str) -> str:
        """Call AI vision API to analyze image and generate test cases.
        
        Args:
            image_base64: Base64 encoded image
            prompt: Prompt for the AI model
            
        Returns:
            AI response text
            
        Raises:
            requests.RequestException: If API call fails
            ValueError: If API key is not configured
        """
        if not self.api_key:
            raise ValueError("API key not configured for vision model")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        try:
            log_api_call("OpenAI Vision", self.api_url, "POST")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            log_api_call("OpenAI Vision", self.api_url, "POST", response.status_code)
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.RequestException as e:
            self.logger.error(f"API call failed: {e}")
            raise
        except KeyError as e:
            self.logger.error(f"Unexpected API response format: {e}")
            raise
    
    def parse_test_cases_from_response(self, response_text: str) -> List[TestCase]:
        """Parse AI response text into TestCase objects.
        
        Args:
            response_text: Raw response from AI API
            
        Returns:
            List of TestCase objects
        """
        test_cases = []
        lines = response_text.split('\n')
        
        current_case = {}
        current_steps = []
        in_steps = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TC-'):
                # Save previous test case if exists
                if current_case:
                    test_case = self._create_test_case_from_dict(current_case, current_steps)
                    if test_case:
                        test_cases.append(test_case)
                
                # Start new test case
                current_case = {'id': line}
                current_steps = []
                in_steps = False
                
            elif line.startswith('Title:'):
                current_case['title'] = line.replace('Title:', '').strip()
                
            elif line.startswith('Type:'):
                current_case['type'] = line.replace('Type:', '').strip()
                
            elif line.startswith('Priority:'):
                current_case['priority'] = line.replace('Priority:', '').strip()
                
            elif line.startswith('Preconditions:'):
                current_case['preconditions'] = line.replace('Preconditions:', '').strip()
                
            elif line.startswith('Steps:'):
                in_steps = True
                
            elif line.startswith('Expected Result:'):
                current_case['expected_result'] = line.replace('Expected Result:', '').strip()
                in_steps = False
                
            elif line.startswith('Covered Elements:'):
                current_case['covered_elements'] = line.replace('Covered Elements:', '').strip()
                
            elif in_steps and line and line[0].isdigit():
                # Extract step number and description
                step_text = line.split('.', 1)[1].strip() if '.' in line else line
                current_steps.append(step_text)
        
        # Add the last test case
        if current_case:
            test_case = self._create_test_case_from_dict(current_case, current_steps)
            if test_case:
                test_cases.append(test_case)
        
        self.logger.info(f"Parsed {len(test_cases)} test cases from AI response")
        return test_cases
    
    def _create_test_case_from_dict(self, case_dict: Dict[str, Any], steps: List[str]) -> Optional[TestCase]:
        """Create a TestCase object from parsed dictionary.
        
        Args:
            case_dict: Dictionary with test case data
            steps: List of test steps
            
        Returns:
            TestCase object or None if invalid
        """
        try:
            # Map test type string to enum
            type_mapping = {
                'FUNC': TestCaseType.FUNC,
                'BOUND': TestCaseType.BOUND,
                'NEG': TestCaseType.NEG,
                'PERM': TestCaseType.PERM,
                'SEC': TestCaseType.SEC,
                'PERF': TestCaseType.PERF,
                'A11Y': TestCaseType.A11Y
            }
            
            # Map priority string to enum
            priority_mapping = {
                'P0': Priority.P0,
                'P1': Priority.P1,
                'P2': Priority.P2,
                'P3': Priority.P3
            }
            
            test_type = type_mapping.get(case_dict.get('type', 'FUNC'), TestCaseType.FUNC)
            priority = priority_mapping.get(case_dict.get('priority', 'P2'), Priority.P2)
            
            return TestCase(
                id=case_dict.get('id', ''),
                title=case_dict.get('title', ''),
                test_type=test_type,
                priority=priority,
                preconditions=[case_dict.get('preconditions', '')] if case_dict.get('preconditions') else [],
                steps=steps,
                expected_result=case_dict.get('expected_result', ''),
                metadata={
                    'covered_elements': case_dict.get('covered_elements', ''),
                    'source': 'screenshot_ai'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating test case from dict: {e}")
            return None
    
    def generate_test_cases_from_screenshot(
        self, 
        image_path: Union[str, Path], 
        test_types: List[str] = None,
        additional_context: str = ""
    ) -> List[TestCase]:
        """Generate test cases from a screenshot using AI vision.
        
        Args:
            image_path: Path to the screenshot
            test_types: List of test case types to generate
            additional_context: Additional context for the AI
            
        Returns:
            List of generated TestCase objects
        """
        if test_types is None:
            test_types = ['FUNC', 'BOUND', 'NEG', 'PERM', 'SEC']
        
        try:
            self.logger.info(f"Generating test cases from screenshot: {image_path}")
            
            # Encode image
            image_base64 = self.encode_image(image_path)
            
            # Create prompt
            prompt = self.create_vision_prompt(test_types, additional_context)
            
            # Call AI API
            response = self.call_vision_api(image_base64, prompt)
            
            # Parse response into test cases
            test_cases = self.parse_test_cases_from_response(response)
            
            self.logger.info(f"Generated {len(test_cases)} test cases from screenshot")
            return test_cases
            
        except Exception as e:
            self.logger.error(f"Error generating test cases from screenshot: {e}")
            raise
    
    def generate_test_cases_from_multiple_screenshots(
        self, 
        image_paths: List[Union[str, Path]], 
        test_types: List[str] = None,
        additional_context: str = ""
    ) -> List[TestCase]:
        """Generate test cases from multiple screenshots.
        
        Args:
            image_paths: List of screenshot paths
            test_types: List of test case types to generate
            additional_context: Additional context for the AI
            
        Returns:
            List of generated TestCase objects
        """
        all_test_cases = []
        
        for image_path in image_paths:
            try:
                test_cases = self.generate_test_cases_from_screenshot(
                    image_path, test_types, additional_context
                )
                all_test_cases.extend(test_cases)
            except Exception as e:
                self.logger.error(f"Error processing screenshot {image_path}: {e}")
                continue
        
        self.logger.info(f"Generated {len(all_test_cases)} total test cases from {len(image_paths)} screenshots")
        return all_test_cases
