import re
import os
import yaml

def process_pipeline_file(input_file):
    # Define regular expressions to find markers/tags
    start_tag_pattern = r'#:::(\w+)-start:::'
    end_tag_pattern = r'#:::(\w+)-end:::'

    # Read the input pipeline file
    with open(input_file, 'r', encoding='utf-8') as f:
        pipeline_content = f.read()

    # Parse the YAML content
    pipeline_data = yaml.safe_load(pipeline_content)

    # Check for allowed tags
    allowed_tags = ['title', 'about', 'example', 'outputs', 'code']
    found_tags = re.findall(r'#:::(\w+)-start:::', pipeline_content)

    for found_tag in found_tags:
        if found_tag not in allowed_tags:
            print(f"Found misspelled start tag: #:::{found_tag}-start:::")
            print("Allowed tags are:", ', '.join(allowed_tags))
            return

    # Check for end tags
    found_end_tags = re.findall(end_tag_pattern, pipeline_content)

    for found_end_tag in found_end_tags:
        if found_end_tag not in allowed_tags:
            print(f"Found misspelled end tag: #:::{found_end_tag}-end:::")
            print("Allowed tags are:", ', '.join(allowed_tags))
            return

    # Check for tag mismatches
    start_tags = re.findall(start_tag_pattern, pipeline_content)
    end_tags = re.findall(end_tag_pattern, pipeline_content)
    if len(start_tags) != len(end_tags):
        print("Tag mismatch error: Number of start tags does not match the number of end tags.")
        print(f"Start tags: {start_tags}")
        print(f"End tags: {end_tags}")
        return

    for start_tag, end_tag in zip(start_tags, end_tags):
        if start_tag != end_tag:
            print(f"Tag mismatch error: Start tag #{start_tag} does not match end tag #{end_tag}.")
            return

    # Extract content between markers and remove leading '#' characters
    title = re.search(r'#:::title-start:::(.*?)#:::title-end:::', pipeline_content, re.DOTALL)
    about = re.search(r'#:::about-start:::(.*?)#:::about-end:::', pipeline_content, re.DOTALL)
    example = re.search(r'#:::example-start:::(.*?)#:::example-end:::', pipeline_content, re.DOTALL)
    outputs = re.search(r'#:::outputs-start:::(.*?)#:::outputs-end:::', pipeline_content, re.DOTALL)
    code = re.search(r'#:::code-start:::(.*?)#:::code-end:::', pipeline_content, re.DOTALL)

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

    if 'parameters' in pipeline_data:
        markdown_content += '## Parameters\n\n'
        for param_info in pipeline_data['parameters']:
            param_name = param_info['name']
            param_type = param_info['type']
            markdown_content += f'**{param_name} ({param_type})**:\n\n'

    if example:
        # Remove leading '#' characters from the example content
        example_text = example.group(1).strip()
        example_text = re.sub(r'^# ', '', example_text, flags=re.MULTILINE)
        markdown_content += '## Example\n\n```yaml\n'
        markdown_content += example_text + '\n```\n\n'

    if code:
        # Remove leading '#' characters from the code content
        code_text = code.group(1).strip()
        code_text = re.sub(r'^# ', '', code_text, flags=re.MULTILINE)
        markdown_content += '## Code\n\n```yaml\n'
        markdown_content += code_text + '\n```\n\n'

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
