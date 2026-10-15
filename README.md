# FusionBrain Image Generator

This Python script generates AI-powered images from random quotes using the FusionBrain API. It fetches inspirational quotes and transforms them into visual art through stable diffusion technology.

## Features

- Fetches random quotes from an external API
- Generates high-quality images (1024x1024 by default) using AI
- Automatic retry logic for image generation
- Fallback mechanism for quote retrieval failures
- Robust error handling for API interactions
- Saves generated images to the fixed `daily_quote.jpg` filename

## Prerequisites

1. **FusionBrain API Access**:
   - Sign up at [FusionBrain](https://fusionbrain.ai/)
   - Obtain your API key and secret

2. **Python Requirements**:
   - Python 3.12+
   - Required packages are pinned with hashes in `requirements.lock`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fusionbrain-image-generator.git
cd fusionbrain-image-generator
```

2. Install dependencies:
```bash
pip install --require-hashes -r requirements.lock
```

3. Set your API credentials as environment variables:
```bash
export FUSIONBRAIN_API_KEY="your_api_key_here"
export FUSIONBRAIN_SECRET_KEY="your_secret_key_here"
```

## Usage

Run the script directly:
```bash
python main.py
```

The script will:
1. Fetch a random quote
2. Generate an AI image based on the quote
3. Save or replace `daily_quote.jpg` and update the image date in this README

## Daily Automation

The GitHub Actions workflow runs daily at 10:23 UTC and can also be started manually. Add `FUSIONBRAIN_API_KEY` and `FUSIONBRAIN_SECRET_KEY` under the repository's **Settings > Secrets and variables > Actions**. If image generation is unavailable, the README displays the quote as text instead. The workflow commits the image or quote and the updated date to the repository.

Example output:
```
Image generated successfully!
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

<!-- DAILY_IMAGE_START -->

<pre>Есть очень важный закон Вселенной: все, о чем мы думаем и говорим, умножается и растет, а то, что мы оставляем без внимания, - исчезает...</pre>

Last updated (UTC): 2026-10-15
<!-- DAILY_IMAGE_END -->

## Troubleshooting

1. **Authentication errors**:
   - Verify `FUSIONBRAIN_API_KEY` and `FUSIONBRAIN_SECRET_KEY`
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
