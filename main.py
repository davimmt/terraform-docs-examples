import os
from itertools import islice

def write_to_readme(readme):
    """ Actually writing final output to file

    This function is called at the end of the script.
    """
    source = 'source'.ljust(readme['metadata']['padding'], ' ')
    if not readme['metadata']['markers']['begin']: file.write('\n<!-- BEGIN_TF_EXAMPLES -->\n')
    file.write('## Example')
    file.write('\n```hcl')
    file.write('\nmodule "%s" {' % (readme['metadata']['module']))
    file.write('\n  %s = "%s"' % (source, readme['metadata']['source']))
    
    for block in readme['data']:
        name = [name.split('"')[1].strip() for name in block if " ".join(name.split()).startswith('variable "')][0]
        name = name.ljust(readme['metadata']['padding'], ' ')
        type = [type.split('=')[1].strip() for type in block if type.strip().startswith('type')]
        default = [default.split('=')[1].strip() for default in block if default.strip().startswith('default')]

        # Checking for complex types
        if not type: type = ["string"]
        elif type[0].count('{') > type[0].count('}') or type[0].count('[') > type[0].count(']'):
            inside_block = False
            block_count = 0
            for line in block:
                if ' type ' in line: inside_block = True
                if inside_block:
                    if '{' in line or '[' in line: block_count += 1
                    if '}' in line or ']' in line: block_count -= 1
                    if block_count == 0: inside_block = False
                    if not ' type ' in line: type[0] += '\n' + line
        
        # Checking for complex defaults
        if not default: default = ["__required__"]
        elif default[0].count('{') > default[0].count('}') or default[0].count('[') > default[0].count(']'):
            inside_block = False
            block_count = 0
            for line in block:
                if ' default ' in line: inside_block = True
                if inside_block:
                    if '{' in line or '[' in line: block_count += 1
                    if '}' in line or ']' in line: block_count -= 1
                    if block_count == 0: inside_block = False
                    if not ' default ' in line: default[0] += '\n' + line

        file.write('\n  %s = %s | %s' % (name, type[0], default[0]))

    file.write('\n}')
    file.write('\n```\n')
    if not readme['metadata']['markers']['begin']: file.write('<!-- END_TF_EXAMPLES -->\n')

if __name__ == "__main__":
    """ Getting all *-module directories and its *.tf files
    
    @return => {'./dir-module': ['file.tf']}
    """
    paths = {}
    for dir in [dir[0] for dir in os.walk('.') if dir[0].endswith('-module')]:
        files = [file for file in os.listdir(dir) if file.endswith('.tf')]
        if files:
            paths[dir] = []
            paths[dir] += files

    """ Grouping all lines from all files in a directory
        to its respective README.md
     
    @return => {'readme': {'metadata': {'module': string, 'source': string}}, {'data': [string]}}
    """
    readmes = {}
    for path in paths:
        module = path.split('/')[-1].split('-module')[0]
        readme = path + '/README.md'
        
        readmes[readme] = {'metadata': {'module': module, 'source': path}, 'data': []}
        for file in [files for files in paths[path]]:
            for line in open('%s/%s' % (path, file), 'r').readlines():
                #while '  ' in line: line = line.replace('  ', ' ').strip()
                while '\n' in line: line = line.replace('\n', '')
                if line: readmes[readme]['data'].append(line)

    """ Tagging all lines that don't belong to a variable block
    
    @return => {'readme': {'data': [line_number]}}
    """
    lines_to_ignore = {}
    for readme in readmes:
        lines_to_ignore[readme] = []
        inside_block = False
        block_count = 0
        for i, line in enumerate(readmes[readme]['data']):
            if " ".join(line.split()).startswith('variable "'): inside_block = True
            if inside_block:
                if '{' in line or '[' in line: block_count += 1
                if '}' in line or ']' in line: block_count -= 1
                if block_count == 0: inside_block = False
            else:
                lines_to_ignore[readme].append(i)

    """ Grouping separete variable blocks in lists
    
    @return => {'readme': {'metadata': {'module': string, 'source': string}}, {'data': [string]}}
    """
    blocks = {}
    for readme in readmes:
        blocks[readme] = {}
        blocks[readme]['data'] = []
        block = []
        previous_block_name = ""
        for i, line in enumerate(readmes[readme]['data']):
            if i not in lines_to_ignore[readme]:
                # Separating blocks
                if " ".join(line.split()).startswith('variable "'):
                    block = [line]
                else: block.append(line)

                # Appending to dict
                if " ".join(line.split()).startswith('variable "') and line != previous_block_name:
                    blocks[readme]['data'].append(block)
                    previous_block_name = line

    """ Getting the biggest variable name for HCL-like padding
    
    @return => {'readme': {'metadata': {'module': string, 'source': string, 'padding': int}}, {'data': [string]}}
    """
    for readme in readmes:
        names = [name.split('"')[1].strip() for name in readmes[readme]['data'] if " ".join(name.split()).startswith('variable "')]
        readmes[readme]['metadata']['padding'] = len(max(names, key = len))

    """ Substituting the first lines-based dictionary/list
        to a blocks-based dictionary/list
    
    @return => {'readme': {'metadata': {'module': string, 'source': string, 'padding': int}}, {'data': [[string]]}}
    """ 
    for readme in readmes:
        readmes[readme]['data'] = []
        for block in blocks[readme]['data']:
            readmes[readme]['data'].append(block) 

    """ Checking if README.md file exists
    
    @return => {'readme': {'metadata': {'module': string, 'source': string, 'padding': int, 'exists': bool, 'markers': {'begin': [int], 'end': [int]}}, {'data': [[string]]}, {'existing_data': [string]}}
    """ 
    for readme in readmes:
        try:
            readmes[readme]['existing_data'] = open(readme, 'r').readlines()
            readmes[readme]['metadata']['exists'] = True
        except:
            readmes[readme]['metadata']['exists'] = False
        
        if readmes[readme]['metadata']['exists']:
            readmes[readme]['metadata']['markers'] = {}
            readmes[readme]['metadata']['markers']['begin'] = [i for i, line in enumerate(readmes[readme]['existing_data']) if line.strip() == '<!-- BEGIN_TF_EXAMPLES -->']
            readmes[readme]['metadata']['markers']['end'] = [i for i, line in enumerate(readmes[readme]['existing_data']) if line.strip() == '<!-- END_TF_EXAMPLES -->']

    """ Writing final output to file

    Here will be "decided" if it's a file creation (no previous README.md),
    a block creation (README.md exists, but doesn't have this script markers) or
    a block update (README.md exists as well as the script's markers).

    For each of these situations, the function write_to_readme() is called differently.
    """
    for readme in readmes:
        with open(readme, 'w') as file:
            # If README.md does not exists
            if not readmes[readme]['metadata']['exists']: write_to_readme(readmes[readme])

            # If README.md exists
            else:
                for i, line in enumerate(readmes[readme]['existing_data']):
                    # Update
                    if readmes[readme]['metadata']['markers']['begin']:
                        if i > readmes[readme]['metadata']['markers']['begin'][0] and i < readmes[readme]['metadata']['markers']['end'][0]: 
                            if i == (readmes[readme]['metadata']['markers']['begin'][0] + 1): write_to_readme(readmes[readme])
                        else: file.write(line)

                    # Create
                    else: file.write(line)
                # Create
                if not readmes[readme]['metadata']['markers']['begin']: write_to_readme(readmes[readme])
