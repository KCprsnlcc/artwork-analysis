import base64
import requests
import json
import sys
import os
import argparse
import threading
import time

# Ollama endpoint configuration
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
VISION_MODEL = "llava" 
TEXT_MODEL = "llama3"   

# Loader spinner globals
_loader_running = False
_loader_thread = None

def _loader_spinner(message="Loading"):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while _loader_running:
        print(f"\r{message}... {spinner[idx % len(spinner)]}", end='', flush=True)
        idx += 1
        time.sleep(0.1)
    print("\r" + " " * (len(message) + 5) + "\r", end='', flush=True)

def start_loader(message="Loading"):
    global _loader_running, _loader_thread
    _loader_running = True
    _loader_thread = threading.Thread(target=_loader_spinner, args=(message,))
    _loader_thread.start()

def stop_loader():
    global _loader_running, _loader_thread
    _loader_running = False
    if _loader_thread:
        _loader_thread.join()
        _loader_thread = None

def encode_image_to_base64(image_path):
    """Encodes an image file to base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded
    except Exception as e:
        raise Exception(f"Error encoding image: {e}")

def query_ollama_model(model_name, prompt, image_path=None, loader_message=None):
    """Generic function to query Ollama models with optional image support and loader."""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    # Add image if provided (for vision models)
    if image_path:
        try:
            image_base64 = encode_image_to_base64(image_path)
            payload["images"] = [image_base64]
        except Exception as e:
            return f"Image encoding failed: {e}"
    
    if loader_message:
        start_loader(loader_message)
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response text returned.")
    except requests.RequestException as e:
        return f"Request failed: {e}"
    finally:
        if loader_message:
            stop_loader()

def step1_analyze_artwork(image_path):
    """Step 1: Analyze the student's artwork using llava model."""
    print("=== STEP 1: ANALYZING ARTWORK ===")
    
    artwork_prompt = """
    Analyze this student submission for a cybersecurity and data privacy assignment. This image contains both the artwork/poster and the student's written explanation.
    
    Please examine and describe the VISUAL ARTWORK portion:
    1. VISUAL ELEMENTS: What visual elements, symbols, colors, and composition techniques are used in the poster/artwork?
    2. THEME REPRESENTATION: How does the artwork represent cybersecurity and data privacy concepts?
    3. CREATIVITY & ORIGINALITY: What creative approaches or unique interpretations are evident?
    4. TECHNICAL EXECUTION: Assess the technical quality and presentation of the artwork.
    5. MESSAGE CLARITY: How clearly does the artwork communicate its intended message?
    
    Focus only on analyzing the visual artwork/poster portion. Do not analyze the text explanation yet - that will be done separately.
    """
    
    artwork_analysis = query_ollama_model(VISION_MODEL, artwork_prompt, image_path, loader_message="Analyzing artwork")
    print("Artwork Analysis:")
    print(artwork_analysis)
    print("\n" + "="*50 + "\n")
    
    return artwork_analysis

def step2_extract_and_analyze_essay(image_path):
    """Step 2: Extract and analyze the student's essay using llava model."""
    print("=== STEP 2: EXTRACTING AND ANALYZING ESSAY ===")
    
    essay_prompt = """
    From this student submission image, please:
    
    FIRST: Extract the complete text of the student's written explanation/essay (usually found in the "Explanation:" section).
    
    THEN: Analyze the extracted essay content for:
    1. THEME UNDERSTANDING: How well does the student understand cybersecurity and data privacy concepts?
    2. INTERPRETATION DEPTH: Does the explanation show deep insight into their artistic choices?
    3. CLARITY OF EXPRESSION: How clearly does the student communicate their ideas?
    4. CONNECTION TO ARTWORK: How well does the narrative connect to and explain the visual work?
    5. CONCEPTUAL THINKING: What level of conceptual thinking is demonstrated?
    
    Please format your response as:
    EXTRACTED ESSAY TEXT: [the exact text from the explanation section]
    
    ESSAY ANALYSIS: [your detailed analysis of the written component]
    """
    
    essay_analysis = query_ollama_model(VISION_MODEL, essay_prompt, image_path, loader_message="Extracting and analyzing essay")
    print("Essay Extraction and Analysis:")
    print(essay_analysis)
    print("\n" + "="*50 + "\n")
    
    return essay_analysis

def step3_score_combined_work(artwork_analysis, essay_analysis):
    """Step 3: Score the combined work using the rubric with llama3 model."""
    print("=== STEP 3: SCORING USING RUBRIC ===")
    
    scoring_prompt = f"""
    Based on the following analyses, score this student's cybersecurity and data privacy project using the official rubric.
    
    ARTWORK ANALYSIS:
    {artwork_analysis}
    
    ESSAY EXTRACTION AND ANALYSIS:
    {essay_analysis}
    
    ASSIGNMENT THEME: Cybersecurity and Data Privacy
    
    SCORING RUBRIC:
    
    **90-100% (A): Exceptional work**
    Artwork and narrative excellently represent the theme with strong, original visuals and ideas. The narrative provides deep insight, and both are well-executed and clearly presented. Shows exceptional effort and completeness.
    
    **80-89% (B): Solid work**
    Artwork and narrative mostly reflect the theme with creativity and clear ideas. Narrative explains the meaning well. Both are generally well-executed with minor issues. Good effort and mostly complete.
    
    **70-79% (C): Satisfactory work**
    Artwork and narrative somewhat relate to the theme but lack clarity or consistency. Narrative provides a basic explanation. Some technical or clarity problems present. Adequate effort but some parts are incomplete or weak.
    
    **60-69% (D): Below average work**
    Artwork and narrative show limited connection to the theme and lack originality. Narrative is unclear or lacks insight. Significant technical flaws or poor presentation. Minimal effort; incomplete work.
    
    **Below 60% (F): Unsatisfactory work**
    Artwork and narrative do not represent the theme or ideas. Narrative is missing or irrelevant. Poor execution and presentation with major problems. Fails to meet assignment objectives.
    
    EVALUATION CRITERIA:
    1. Theme relevance and understanding of cybersecurity/data privacy
    2. Creativity and originality in visual presentation
    3. Technical quality and execution
    4. Narrative depth and insight
    5. Overall coherence between artwork and explanation
    
    Please provide:
    1. A detailed evaluation addressing each criterion
    2. Specific strengths and areas for improvement
    3. A final numerical score (0-100) and letter grade
    4. Justification for the assigned grade based on the rubric
    
    Format your response clearly with the final score prominently displayed.
    """
    
    final_evaluation = query_ollama_model(TEXT_MODEL, scoring_prompt, loader_message="Scoring combined work")
    print("Final Evaluation and Score:")
    print(final_evaluation)
    
    return final_evaluation

def validate_inputs(image_path, essay_text):
    """Validate that required inputs are provided and accessible."""
    errors = []
    
    if not image_path or not os.path.isfile(image_path):
        errors.append(f"Image file not found or invalid: {image_path}")
    
    if not essay_text or len(essay_text.strip()) < 10:
        errors.append("Essay text is missing or too short (minimum 10 characters required)")
    
    return errors

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate student cybersecurity artwork and essay from a single image file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python artwork_analysis.py student_submission.jpg
  python artwork_analysis.py cedrick_poster.jpg --output evaluation_report.txt
        """
    )
    
    parser.add_argument("image_path", help="Path to the student's submission image (contains both artwork and essay)")
    parser.add_argument("--output", help="Save evaluation results to specified file")
    
    args = parser.parse_args()
    
    # Validate image file exists
    if not os.path.isfile(args.image_path):
        print(f"Error: The file '{args.image_path}' does not exist or is not a file.")
        sys.exit(1)
    
    print("CYBERSECURITY & DATA PRIVACY ARTWORK EVALUATION")
    print("=" * 60)
    print(f"Student Submission: {args.image_path}")
    print("Analyzing integrated artwork and essay from single image...")
    print("=" * 60)
    
    try:
        # Execute the 3-step evaluation process
        artwork_analysis = step1_analyze_artwork(args.image_path)
        essay_analysis = step2_extract_and_analyze_essay(args.image_path)
        final_score = step3_score_combined_work(artwork_analysis, essay_analysis)
        
        # Compile full results
        full_results = f"""
CYBERSECURITY & DATA PRIVACY ARTWORK EVALUATION REPORT
=====================================================
Student Submission: {args.image_path}
Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STEP 1 - ARTWORK ANALYSIS:
{artwork_analysis}

STEP 2 - ESSAY EXTRACTION & ANALYSIS:
{essay_analysis}

STEP 3 - FINAL EVALUATION & SCORE:
{final_score}
        """
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(full_results)
                print(f"\nFull evaluation saved to: {args.output}")
            except Exception as e:
                print(f"Warning: Could not save to file: {e}")
    
    except Exception as e:
        print(f"Evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()