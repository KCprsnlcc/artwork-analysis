# Artwork Analysis Tool

A command-line tool for evaluating student submissions related to cybersecurity and data privacy. This tool analyzes images containing both artwork/posters and written explanations, providing comprehensive feedback and scoring.

## Features

- **Artwork Analysis**: Evaluates visual elements, theme representation, creativity, technical execution, and message clarity of the artwork.
- **Essay Extraction and Analysis**: Extracts the written explanation from the image and analyzes it for theme understanding, interpretation depth, clarity, and conceptual thinking.
- **Rubric-Based Scoring**: Combines both analyses to provide a final score (0-100) and letter grade based on a detailed rubric.
- **Comprehensive Reporting**: Generates detailed reports that can be displayed in the terminal or saved to a file.

## Prerequisites

- Python 3.6 or higher
- [Ollama](https://ollama.ai/) running locally with the following models:
  - `llava` (for vision-based analysis)
  - `llama3` (for text analysis and scoring)

## Installation

1. Clone this repository or download the script
2. Install required dependencies:

```bash
pip install requests
```

3. Ensure Ollama is running locally with the required models

## Usage

Basic usage:

```bash
python artwork_analysis.py path/to/student_submission.jpg
```

Save the evaluation to a file:

```bash
python artwork_analysis.py path/to/student_submission.jpg --output evaluation_report.txt
```

## Evaluation Process

The tool performs a three-step evaluation process:

1. **Artwork Analysis**: Uses the llava vision model to analyze the visual components of the submission
2. **Essay Extraction and Analysis**: Extracts and evaluates the written explanation from the image
3. **Final Scoring**: Uses the llama3 model to score the work based on a comprehensive rubric

## Rubric

Submissions are evaluated on a scale of 0-100 with corresponding letter grades:

- **90-100% (A)**: Exceptional work
- **80-89% (B)**: Solid work
- **70-79% (C)**: Satisfactory work
- **60-69% (D)**: Below average work
- **Below 60% (F)**: Unsatisfactory work

Evaluation criteria include:
- Theme relevance and understanding
- Creativity and originality
- Technical quality and execution
- Narrative depth and insight
- Overall coherence between artwork and explanation

## Sample Files

The repository includes a sample image file for testing:
- `artworksub_sample2.jpg` 