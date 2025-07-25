# FusionBrain Image Generator

This Python script generates AI-powered images from random quotes using the FusionBrain API. It fetches inspirational quotes and transforms them into visual art through stable diffusion technology.

## Features

- Fetches random quotes from an external API
- Generates high-quality images (1024x1024 by default) using AI
- Automatic retry logic for image generation
- Fallback mechanism for quote retrieval failures
- Robust error handling for API interactions
- Saves generated images with quote-based filenames

## Prerequisites

1. **FusionBrain API Access**:
   - Sign up at [FusionBrain](https://fusionbrain.ai/)
   - Obtain your API key and secret

2. **Python Requirements**:
   - Python 3.8+
   - Required packages: `requests`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fusionbrain-image-generator.git
cd fusionbrain-image-generator
```

2. Install dependencies:
```bash
pip install requests
```

3. Configure your API credentials:
```python
# In the script file:
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"
```

## Usage

Run the script directly:
```bash
python image_generator.py
```

The script will:
1. Fetch a random quote
2. Generate an AI image based on the quote
3. Save the image as `[quote].jpg` in the current directory

Example output:
```
Image generated successfully!
Saved as: Life-is-what-happens-when-youre-busy-making-other-plans.jpg
```

## Configuration Options

You can customize the script by modifying these parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `width` | 1024 | Image width in pixels |
| `height` | 1024 | Image height in pixels |
| `num_images` | 1 | Number of images to generate |
| `max_attempts` | 10 | Max status check attempts |
| `delay` | 10 | Seconds between status checks |

Example customization:
```python
# In generate_image() call:
uuid = api.generate_image(
    quote, 
    pipeline_id,
    num_images=2,
    width=768,
    height=768
)
```

## Error Handling

The script handles various error scenarios:
- Network failures during API calls
- Invalid API credentials
- Image generation failures
- Empty quote responses
- Timeouts during processing

Example error messages:
```
API request failed: 401 Client Error: Unauthorized
Processing error: Image generation failed
```

## Example Output

![Example Generated Image](Life-is-what-happens-when-youre-busy-making-other-plans.jpg)

*Example image generated from the quote: "Life is what happens when you're busy making other plans"*

## Troubleshooting

1. **Authentication errors**:
   - Verify your API_KEY and SECRET_KEY
   - Ensure your FusionBrain account is active

2. **Long processing times**:
   - Increase `max_attempts` and `delay` parameters
   - Check FusionBrain service status

3. **Empty quote fallback**:
   - The quote API might be temporarily unavailable
   - Script will use "Sun in sky" as default prompt

## License

This project is provided as-is without license. Please respect FusionBrain's API terms of service.

## Credits

- Quote API: [quotes.to.digital](https://quotes.to.digital)
- Image Generation: [FusionBrain AI](https://fusionbrain.ai/)
