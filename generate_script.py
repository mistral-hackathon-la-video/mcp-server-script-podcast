from openai import OpenAI
from typing import Literal, Any, List
# from  backend.schemas.script import generate_model_with_context_check, reconstruct_script
import instructor
from instructor.core.hooks import Hooks, HookName
import requests
import os
import logging
import traceback
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from enum import Enum


logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv()

# Access the variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OCR_MODEL = os.getenv("OCR_MODEL")
OCR_PROVIDER = os.getenv("OCR_PROVIDER")
OCR_COORDINATE_EXTRACTOR_MODEL = os.getenv("OCR_COORDINATE_EXTRACTOR_MODEL")
OCR_PARSING_MODEL = os.getenv("OCR_PARSING_MODEL")
OCR_FIGURE_DETECTOR_MODEL = os.getenv("OCR_FIGURE_DETECTOR_MODEL")
SCRIPGENETOR_MODEL = os.getenv("SCRIPGENETOR_MODEL")
GEMINI_SCRIP_MODEL = os.getenv("GEMINI_SCRIP_MODEL")

import re


class ScriptComponentType(str, Enum):
    TEXT = "Text"
    HEADLINE = "Headline"


class ScriptComponent(BaseModel):
    component_type: str = Field(
        ...,
        description="Type of script component - either 'Text' or 'Headline'"
    )
    content: str = Field(
        ...,
        description="""Content of the component. 
        For Headlines: Write as complete, natural sentences that could be spoken aloud. 
        Avoid title-case or abbreviated phrases. Use conversational, engaging language.
        For Text: Regular narrative content for the video script."""
    )
    position: int = Field(
        ...,
        description="Position of the component in the script"
    )


def reconstruct_script(script: BaseModel) -> str:
    """
    Reconstruct the script text from ArxflixScript model.
    
    Args:
        script (ArxflixScript): Validated script model
        
    Returns:
        str: Formatted script text
    
    Example:
        >>> script = ArxflixScript(
        ...     title="Understanding GPT-4",
        ...     paper_id="2405.11273",
        ...     target_duration_minutes=5.0,
        ...     components=[
        ...         ScriptComponent(component_type="Headline", content="Understanding GPT-4", position=0),
        ...         ScriptComponent(component_type="Text", content="Welcome to this review!", position=1)
        ...     ]
        ... )
        >>> print(reconstruct_script(script))
        \\Headline: Understanding GPT-4
        \\Text: Welcome to this review!
    """
    return '\n'.join(f"\\{comp.component_type.strip()}: {comp.content}" 
                    for comp in script.components)


def generate_model_with_context_check(paper_id : str ,paper_content : str):
    class ArxflixScript(BaseModel):
        title: str = Field(
            ...,
            description="Title of the research paper",
            examples=[
                "Uni-MoE: Scaling Unified Multimodal LLMs with Mixture of Experts",
                "Attention Is All You Need",
                "BERT: Pre-training of Deep Bidirectional Transformers"
            ]
        )
        paper_id: str = Field(
            ...,
            description=f"ArXiv paper ID (e.g., '2405.11273')",
            examples=["2405.11273", "1706.03762", "1810.04805"]
        )
        target_duration_minutes: float = Field(
            ...,
            ge=0,
            le=6,
            description="Target video duration in minutes",
            examples=[5.0, 5.5, 6.0]
        )
        components: List[ScriptComponent] = Field(
            ...,
            description="List of script components",
            examples=[[
                {
                    "component_type": "Headline",
                    "content": "Let's explore how GPT-4 revolutionizes language modeling with advanced techniques",
                    "position": 0
                },
                {
                    "component_type": "Text",
                    "content": "Today we're diving deep into the revolutionary GPT-4 model and understanding what makes it so powerful.",
                    "position": 1
                },

            ]]
        )

        @model_validator(mode='after')
        def validate_script_structure(cls,values):
            errors = []
            logger.warning(f"Validating script structure for paper_id: {paper_id}")

            components = values.components

            

            if not components:
                errors.append(ValueError("Script must contain at least one component"))

            if paper_id != "paper_id" and values.paper_id != paper_id:
                logger.warning(f"Paper ID mismatch: expected {paper_id}, got {values.paper_id}, correcting")
                errors.append(ValueError(f"The paper id is {paper_id}, you wrote a wrong one, correct it everywhere"))
                
            else:
                sorted_components = sorted(components, key=lambda x: x.position)
                
                positions = [comp.position for comp in sorted_components]
                if positions != list(range(len(positions))):
                    errors.append(ValueError("Component positions must be consecutive integers starting from 0"))

                if sorted_components[0].component_type.strip() != ScriptComponentType.HEADLINE:
                    errors.append(ValueError("Script must start with a Headline component"))
                
                for i in range(1, len(sorted_components)):
                    if (sorted_components[i].component_type.strip() == sorted_components[i-1].component_type.strip() and 
                        sorted_components[i].component_type.strip() != ScriptComponentType.TEXT):
                        errors.append(ValueError(f"Consecutive {sorted_components[i].component_type.strip()} components are not allowed"))

                values.components = sorted_components
            

            for comp in values.components:
                # if comp.component_type.strip() == ScriptComponentType.FIGURE:
                #     # More lenient figure validation - only check if it looks like a URL
                #     if not (comp.content.startswith('http') or comp.content.startswith('/')): 
                #         errors.append(ValueError(f"Figure content should be a valid URL or file path: {comp.content}"))
                #     # Skip figure link accessibility check for now to avoid network issues
                    
                if comp.component_type.strip() not in ["Text",  "Headline"]:
                    errors.append(ValueError(f"""{comp.component_type.strip()} is not a valid component_type.
                             Type of autorized script component
                                    Only one of : 
                                    - Text 
                                    - Headline"""))
                    logger.info(errors[-1])
            if errors:
                print(errors)
                logger.info(errors)
                raise ValueError(errors)
            return values
    return ArxflixScript



def replace_keys_with_values(text, dict_list):
  """
  Replaces keys found in a text with their corresponding values from a list of dictionaries.

  Args:
    text: The input text string.
    dict_list: A list of dictionaries where keys are patterns to search for in the text 
               and values are the replacements.

  Returns:
    The modified text with keys replaced by values.
  """

  # Combine all dictionaries into a single dictionary for efficiency
  combined_dict = {}
  for d in dict_list:
    combined_dict.update(d)

  # Filter out empty keys to prevent KeyError
  combined_dict = {k: v for k, v in combined_dict.items() if k and k.strip()}
  
  # If no valid keys, return original text
  if not combined_dict:
    return text

  # Sort keys by length in descending order to handle overlapping keys correctly
  sorted_keys = sorted(combined_dict.keys(), key=len, reverse=True)

  # Build a regular expression pattern to match any of the keys
  # Escape special characters in keys for use in regex
  pattern = re.compile("|".join(map(re.escape, sorted_keys)))

  # Perform the replacement using re.sub with a lambda function
  modified_text = pattern.sub(lambda match: combined_dict.get(match.group(0), match.group(0)), text)

  return modified_text

def adjust_links(text_md : str, paper_id : str):

    def get_link(link, paper_id):
        # Handle empty or invalid links
        if not link or not link.strip():
            return link
            
        if 'ar5iv.labs.arxiv.org' in link:
            return '![]('+link.replace('![](','https://').replace(')','')+')'
        elif f'https:/arxiv.org/html/{paper_id}/'  in link:
            return '![]('+link.replace('![](',f'https://arxiv.org/html/{paper_id}/').replace(')','')+')'
        elif '(arxiv.org' in link:
            return '![]('+link.replace('![](arxiv.org',f'https://arxiv.org/html/{paper_id}').replace(')','')+')'
        else:
            return '![]('+link.replace('![](',f'https://arxiv.org/html/{paper_id}/').replace(')','')+')'

    # Filter out empty lines and only process valid image links
    lines_with_images = [line for line in text_md.split('\n') if line.strip() and '![](' in line]
    
    # Create dictionaries only for valid lines
    links = []
    for line in lines_with_images:
        try:
            processed_link = get_link(line, paper_id)
            # Only add to links if both original and processed are valid
            if line.strip() and processed_link.strip() and line != processed_link:
                links.append({line: processed_link})
        except Exception as e:
            # Log the error but continue processing
            print(f"Warning: Error processing link '{line}': {e}")
            continue

    output = replace_keys_with_values(text_md, links)

    return output

SYSTEM_PROMPT = r"""
<context>
You're Arxflix an AI Researcher and Content Creator on Youtube who specializes in summarizing academic papers.
The video will be uploaded on YouTube and is intended for a research-focused audience of academics, students, and professionals of the field of deep learning. 
</context>

<goal>
Generate a script for a mid-short video (5-6 minutes or less than 6000 words) on the research paper you will receve.
</goal>


<style_instructions>
The script should be engaging, clear, and concise, effectively communicating the content of the paper. 
The video should give a good overview of the paper in the least amount of time possible, with short sentences that fit well for a dynamic Youtube video.
The overall goal of the video is to make research papers more accessible and understandable to a wider audience, while maintaining academic rigor.
</style_instructions>

<format_instructions>
The script sould be formated following the followings rules below:
- Your ouput is a JSON with the following keys :
    - title: The title of the video.
    - paper_id: The id of the paper (e.g., '2405.11273') explicitly mensionned in the paper
    - target_duration_minutes : The target duration of the video
    - components : a list of component (component_type, content, position)
        - You should follow this format for each component: Text and Headline
        - The only autorized component_type are : Text,  and Headline
        - The Text will be spoken by a narrator and caption in the video.
        - For Headlines: Write complete, conversational sentences that sound natural when spoken. Avoid title-case phrases, abbreviations, or technical jargon. Use engaging, accessible language like "Let's explore how...", "Now we'll discover...", "Here's why this approach...", etc.
        - Avoid markdown listing (1., 2., or - dash) at all cost. Use full sentences that are easy to understand in spoken language.
        - Don't hallucinate figures.
        - Don't forget to maintain https:// as it is in the link.
</format_instructions>

Attention : 
- The paper_id in the precedent instruction are just exemples. Don't confuse it with the correct paper ID you ll receve.
- Only extract figure that are present in the paper. Don't use the exemple links. 
- keep the full link of the figure in the figure content value
- Do not forget 'https://' a the start of the figure link.
- Always include at least one figure if present in the text. Viewers like when the video is animated and well commented. 3blue1brown Style


Here is an example of what you need to produce for paper id 2405.11273: 
<exemple>
{
    "title": "Uni-MoE: Scaling Unified Multimodal LLMs with Mixture of Experts",
    "paper_id": "2405.11273",
    "target_duration_minutes": 5.5,
    "components": [
        {
            "component_type": "Headline",
            "content": "Today we're exploring how Uni-MoE creates a revolutionary approach to multimodal AI architectures",
            "position": 0
        },
        {
            "component_type": "Text",
            "content": "Welcome back to Arxflix! Today, we’re diving into an exciting new paper titled "Uni-MoE: Scaling Unified Multimodal LLMs with Mixture of Experts". This research addresses the challenge of efficiently scaling multimodal large language models (MLLMs) to handle a variety of data types like text, images, audio, and video.",
            "position": 1
        },
        {
            "component_type": "Text",
            "content": "Here’s a snapshot of the Uni-MoE model, illustrating its ability to handle multiple modalities using the Mixture of Experts (MoE) architecture. Let’s break down the main points of this paper.",
            "position": 3
        },
        {
            "component_type": "Headline",
            "content": "Let's understand why traditional scaling methods create significant computational challenges",
            "position": 4
        },
        {
            "component_type": "Text",
            "content": "Scaling multimodal models traditionally incurs high computational costs. Conventional models process each input with all model parameters, leading to dense and inefficient computations.",
            "position": 5
        },
        {
            "component_type": "Text",
            "content": "Enter the Mixture of Experts (MoE). Unlike dense models, MoE activates only a subset of experts for each input. This sparse activation reduces computational overhead while maintaining performance.",
            "position": 6
        },
        {
            "component_type": "Text",
            "content": "Previous works have used MoE in text and image-text models but limited their scope to fewer experts and modalities. This paper pioneers a unified MLLM leveraging MoE across multiple modalities.",
            "position": 7
        },
        ...
    ]
}
</exemple>


Your output is a JSON with the following structure : 

{
    "title": "...",
    "paper_id": "...",
    "target_duration_minutes": ...,
    "components": [
        {
            "component_type": "...",
            "content": "...",
            "position": ...
        },
        ...
    ]
}

"""

SYSTEM_PROMPT_NO_LINK = r"""
<context>
You're Arxflix an AI Researcher and Content Creator on Youtube who specializes in summarizing academic papers.
The video will be uploaded on YouTube and is intended for a research-focused audience of academics, students, and professionals of the field of deep learning. 
</context>

<goal>
Generate a script for a mid-short video (5-6 minutes or less than 6000 words) on the research paper you will receve.
</goal>


<style_instructions>
The script should be engaging, clear, and concise, effectively communicating the content of the paper. 
The video should give a good overview of the paper in the least amount of time possible, with short sentences that fit well for a dynamic Youtube video.
The overall goal of the video is to make research papers more accessible and understandable to a wider audience, while maintaining academic rigor.
</style_instructions>

<format_instructions>
The script sould be formated following the followings rules below:
- Your ouput is a JSON with the following keys :
    - title: The title of the video.
    - paper_id: The id of the paper (e.g., '2405.11273') explicitly mensionned in the paper
    - target_duration_minutes : The target duration of the video
    - components : a list of component (component_type, content, position)
        - You should follow this format for each component: Text, and Headline
        - The only autorized component_type are : Text, and Headline
        - The Text will be spoken by a narrator and caption in the video.
        - For Headlines: Write complete, conversational sentences that sound natural when spoken. Avoid title-case phrases, abbreviations, or technical jargon. Use engaging, accessible language like "Let's explore how...", "Now we'll discover...", "Here's why this approach...", etc.
        - Avoid markdown listing (1., 2., or - dash) at all cost. Use full sentences that are easy to understand in spoken language.
        - Don't hallucinate figures.
        - Don't forget to keep the full path of the figure in the figure content value.
</format_instructions>

Attention : 


Here is an example of what you need to produce for paper id 2405.11273: 
<exemple>
{
    "title": "Uni-MoE: Scaling Unified Multimodal LLMs with Mixture of Experts",
    "paper_id": "2405.11273",
    "target_duration_minutes": 5.5,
    "components": [
        {
            "component_type": "Headline",
            "content": "Today we're exploring how Uni-MoE creates a revolutionary approach to multimodal AI architectures",
            "position": 0
        },
        {
            "component_type": "Text",
            "content": "Welcome back to Arxflix! Today, we’re diving into an exciting new paper titled "Uni-MoE: Scaling Unified Multimodal LLMs with Mixture of Experts". This research addresses the challenge of efficiently scaling multimodal large language models (MLLMs) to handle a variety of data types like text, images, audio, and video.",
            "position": 1
        },
        {
            "component_type": "Text",
            "content": "Here’s a snapshot of the Uni-MoE model, illustrating its ability to handle multiple modalities using the Mixture of Experts (MoE) architecture. Let’s break down the main points of this paper.",
            "position": 3
        },
        {
            "component_type": "Headline",
            "content": "Let's understand why traditional scaling methods create significant computational challenges",
            "position": 4
        },
        {
            "component_type": "Text",
            "content": "Scaling multimodal models traditionally incurs high computational costs. Conventional models process each input with all model parameters, leading to dense and inefficient computations.",
            "position": 5
        },
        {
            "component_type": "Text",
            "content": "Enter the Mixture of Experts (MoE). Unlike dense models, MoE activates only a subset of experts for each input. This sparse activation reduces computational overhead while maintaining performance.",
            "position": 6
        },
        {
            "component_type": "Text",
            "content": "Previous works have used MoE in text and image-text models but limited their scope to fewer experts and modalities. This paper pioneers a unified MLLM leveraging MoE across multiple modalities.",
            "position": 7
        },
        ...
    ]
}
</exemple>


Your output is a JSON with the following structure : 

{
    "title": "...",
    "paper_id": "...",
    "target_duration_minutes": ...,
    "components": [
        {
            "component_type": "...",
            "content": "...",
            "position": ...
        },
        ...
    ]
}

"""




def create_logging_hooks(tag: str = "instructor") -> Hooks:
    """Create hooks that log each failed attempt (completion + parse errors)."""
    hooks = Hooks()
    state: dict[str, Any] = {"kwargs": None, "response": None}

    def on_kwargs(*args: Any, **kwargs: Any) -> None:
        try:
            state["kwargs"] = {
                "model": kwargs.get("model"),
                "messages": kwargs.get("messages")
                or kwargs.get("contents")
                or kwargs.get("chat_history"),
                "temperature": kwargs.get("temperature"),
                "top_p": kwargs.get("top_p"),
                "stream": kwargs.get("stream"),
            }
        except Exception:
            pass

    def on_response(response: Any) -> None:
        state["response"] = response

    def extract_text_from_response(resp: Any) -> str | None:
        try:
            if hasattr(resp, "choices") and resp.choices:
                choice0 = resp.choices[0]
                if hasattr(choice0, "message") and getattr(choice0.message, "content", None):
                    return str(choice0.message.content)
                if hasattr(choice0, "text") and getattr(choice0, "text", None):
                    return str(choice0.text)
        except Exception:
            return None
        return None

    def on_parse_error(error: Exception) -> None:
        model = None
        messages = None
        if isinstance(state.get("kwargs"), dict):
            model = state["kwargs"].get("model")
            messages = state["kwargs"].get("messages")
        raw_text = extract_text_from_response(state.get("response"))

        logger.error(f"[{tag}] Parse error: {error}")
        if model:
            logger.error(f"[{tag}] Model: {model}")
        if messages:
            try:
                user_prompt = None
                for m in messages:
                    if isinstance(m, dict) and m.get("role") == "user":
                        user_prompt = m.get("content")
                if user_prompt:
                    excerpt = str(user_prompt)
                    logger.error(f"[{tag}] Prompt excerpt: {excerpt[:1000]}")
            except Exception:
                pass
        if raw_text:
            logger.error(f"[{tag}] Raw completion excerpt: {raw_text[:1000]}")

    def on_completion_error(error: Exception) -> None:
        logger.error(f"[{tag}] Completion error: {error}")

    def on_last_attempt(error: Exception) -> None:
        logger.error(f"[{tag}] Last attempt failed: {error}")

    hooks.on(HookName.COMPLETION_KWARGS, on_kwargs)
    hooks.on(HookName.COMPLETION_RESPONSE, on_response)
    hooks.on(HookName.PARSE_ERROR, on_parse_error)
    hooks.on(HookName.COMPLETION_ERROR, on_completion_error)
    hooks.on(HookName.COMPLETION_LAST_ATTEMPT, on_last_attempt)
    return hooks


def _correct_result_link(script: str, url: str) -> str:
    """Correct generated links in a research paper script.

    Parameters:
    - script: str
        The script of a research paper.
    - url: str
        The base URL of the research paper (can contain "/html/").

    Returns:
    - str
        The corrected script with valid image links.
    """
    # handle non-arXiv links
    if "ar5iv" not in url:
        tmp_url = url.split("/")
        url = (
            "https://ar5iv.labs.arxiv.org/html/" + tmp_url[-1]
            if tmp_url[-1] != ""
            else "https://ar5iv.labs.arxiv.org/html/" + tmp_url[-2]
        )

    split_script = script.split("n")

    for line_idx, line in enumerate(split_script):
        if r"Figure: " in line and not line.startswith("https"):
            tmp_line = line.replace(r"Figure: ", "")

            # Construct the potential figure URL
            if "/html/" in tmp_line:
                modified_base_url = url.split("/html/")[0]
                figure_url = f"{modified_base_url}{tmp_line}"
            else:
                figure_url = f"{url if url.endswith('/') else url+'/'}{tmp_line if tmp_line[0] != '/' else tmp_line[1:]}"

            try:
                # Check if the URL leads to an image (PNG)
                response = requests.head(figure_url)
                if response.status_code == 200 and "image/png" in response.headers.get(
                    "Content-Type", ""
                ):
                    split_script[line_idx] = r"Figure: " + figure_url
                else:
                    # Remove "ar5iv.labs." and try again
                    figure_url = figure_url.replace("ar5iv.labs.", "")
                    response = requests.head(figure_url)
                    if (
                        response.status_code == 200
                        and "image/png" in response.headers.get("Content-Type", "")
                    ):
                        split_script[line_idx] = r"Figure: " + figure_url
            except requests.exceptions.RequestException:
                # If the request fails, leave the link as is (or handle the error as you prefer)
                pass

    return "n".join(split_script)


def _process_script_openrouter(paper: str, paper_id: str) -> str:
    """Generate a video script using OpenRouter (OpenAI-compatible API).

    Uses the OpenAI SDK pointed to the OpenRouter base URL.
    """
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("SCRIPGENETOR_MODEL", "qwen/qwen3-235b-a22b-thinking-2507")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    if not OPENROUTER_API_KEY:
        raise ValueError("You need to set the OPENROUTER_API_KEY environment variable.")

    try:
        openrouter_client = instructor.from_openai(
            OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL),
            mode=instructor.Mode.OPENROUTER_STRUCTURED_OUTPUTS if "gpt" not in OPENROUTER_MODEL else instructor.Mode.JSON_SCHEMA,
            hooks=create_logging_hooks("openrouter"),
        )
        
        # Try with reduced validation first
        response,raw = openrouter_client.chat.completions.create_with_completion(
            model=OPENROUTER_MODEL,
            messages=
            [
                {"role": "system", "content": SYSTEM_PROMPT_NO_LINK if paper_id == "paper_id" else SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Here is the paper I want you to generate a script from, its paper_id is {paper_id} : "
                    + paper,
                },
            ],
            response_model=generate_model_with_context_check(paper_id, paper),
            temperature=0.1,  # Slightly higher temperature to avoid getting stuck
            max_retries=2,    # Reduced retries to fail faster
            max_tokens=8000,
        )
        
        if not response:
            raise ValueError("Empty response received from model")
            
    except Exception as e:
        print(f"Error during script generation: {e}")
        # Try with a simpler prompt if the structured one fails
        raise ValueError(f"Script generation failed: {e}")

    try:
        result = reconstruct_script(response)
    except Exception as e:
        print(e)
        raise ValueError(f"The model failed the script generation:  {e}, {traceback.format_exc()}")
    return result



def process_script(method: Literal["openrouter"], paper_markdown: str, paper_id : str, from_pdf: bool=False) -> str:
    """Generate a video script for a research paper.

    Parameters
    ----------
    paper_markdown : str
        A research paper in markdown format.

    Returns
    -------
    str
        The generated video script.

    Raises
    ------
    ValueError
        If no result is returned from OpenAI.
    """
    if not from_pdf:
        pd_corrected_links = adjust_links(paper_markdown , paper_id )
    else:
        pd_corrected_links = paper_markdown
        paper_id = "paper_id"
    if method == "openai":
        return _process_script_gpt(pd_corrected_links,paper_id)
    if method == "local":
        return _process_script_open_source(pd_corrected_links, paper_id, end_point_base_url)
    if method == "gemini":
        return _process_script_open_gemini(pd_corrected_links, paper_id, end_point_base_url)
    if method == "groq":
        return _process_script_groq(pd_corrected_links,paper_id)
    if method == "openrouter":
        return _process_script_openrouter(pd_corrected_links, paper_id)
    else:
        raise ValueError("Invalid method. Please choose 'openai'.")


def _fetch_paper_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX, 5XX)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


def main():
    # Example usage
    url = "https://ar5iv.labs.arxiv.org/html/1706.03762"
    paper_markdown = _fetch_paper_html(url)

    paper_id = "1706.03762"
    method = "openrouter"  # Change this to test other methods

    try:
        script = process_script(method=method, paper_markdown=paper_markdown, paper_id=paper_id, from_pdf=False)
        print("Generated script:\n", script)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
