import re
import os

def process_pipeline_file(input_file):
    # Define regular expressions to find markers/tags
    title_pattern = r'#:::title-start:::(.*?)#:::title-end:::'
    about_pattern = r'#:::about-start:::(.*?)#:::about-end:::'
    example_pattern = r'#:::example-start:::(.*?)#:::example-end:::'
    outputs_pattern = r'#:::outputs-start:::(.*?)#:::outputs-end:::'

    # Read the input pipeline file
    with open(input_file, 'r') as f:
        pipeline_content = f.read()

    # Extract content between markers and remove leading '#' characters
    title = re.search(title_pattern, pipeline_content, re.DOTALL)
    about = re.search(about_pattern, pipeline_content, re.DOTALL)
    example = re.search(example_pattern, pipeline_content, re.DOTALL)
    outputs = re.search(outputs_pattern, pipeline_content, re.DOTALL)

    # Create Markdown documentation
    markdown_content = ''

    if title:
        # Remove leading '#' character from the title
        title_text = title.group(1).strip()
        title_text = re.sub(r'^# ', '', title_text)
        markdown_content += f'# {title_text}\n\n'

    if about:
        # Remove leading '#' character from the about text
        about_text = about.group(1).strip()
        about_text = re.sub(r'^# ', '', about_text)
        markdown_content += f'{about_text}\n\n'

    if example:
        # Remove leading '#' characters from the example content
        example_text = example.group(1).strip()
        example_text = re.sub(r'^# ', '', example_text, flags=re.MULTILINE)
        markdown_content += '## Example\n\n```yaml\n'
        markdown_content += example_text + '\n```\n\n'

    if outputs:
        # Remove leading '#' characters from the outputs content
        outputs_text = outputs.group(1).strip()
        outputs_text = re.sub(r'^# ', '', outputs_text, flags=re.MULTILINE)
        outputs_text = re.sub(r'^\s*#', '', outputs_text, flags=re.MULTILINE)
        markdown_content += '## Outputs\n\n'
        markdown_content += outputs_text + '\n\n'

    # Construct the output file path in the current directory
    output_file = os.path.basename(input_file).replace(".yml", ".md")

    # Write the Markdown content to the output file
    with open(output_file, 'w') as f:
        f.write(markdown_content)

if __name__ == "__main__":
    input_file = "test-pipe.yml"  # Replace with your input YAML file

    process_pipeline_file(input_file)
