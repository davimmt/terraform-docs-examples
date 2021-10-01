import os,sys,subprocess
from itertools import islice

def get_all_terraform_files():
    """Returns a list with path/name of the chosen files.

    Uses the Unix 'find' package to recursivly search the
    specified files in the defined scope.
    """
    files_cmd = subprocess.Popen("find . -type f -wholename '*-module/*.tf'", shell=True, stdout=subprocess.PIPE) 
    return list(filter(None, files_cmd.stdout.read().decode('ascii').split('\n')))

if __name__ == "__main__":
    files = get_all_terraform_files() 

    output_content = {}
    metadata = {}
    for file in files:
        print('Working on [%s] file' % (file))
        source_path = os.path.dirname(file)
        module_name = source_path.split('/')[-1].split('-module')[0]
        output_file = source_path + '/README.md'
        metadata[output_file] = {'source': source_path, 'module': module_name}

        print('  Grouping file to its path README.md')
        if not output_file in output_content: output_content[output_file] = {'files': [], 'lines': []}
        output_content[output_file]['files'].append(file)

    print('\nGrouping all lines from the files to their path README.md\n')
    for output_file in output_content: 
        for file in output_content[output_file]['files']:
            lines = open(file, 'r').readlines()
            
            # Getting all variable blocks
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                variable_blocks = []
                if stripped_line.startswith('variable') and stripped_line.endswith('{'): 
                    variable_blocks.append(line)
                    indentation = 0
                    for line_ in islice(lines, i, None): 
                        # Gambiarra aqui
                        if '[]' in line_ or '{}' in line_: variable_blocks.append(line_)
                        
                        if '}' in line_ or ']' in line_: indentation -= 1
                        if indentation != 0: variable_blocks.append(line_)
                        if '{' in line_ or '[' in line_: indentation += 1
                        
                        if indentation == 0: break
                    output_content[output_file]['lines'].append(variable_blocks)

        # Grouping all variables together
        names = []
        examples = []
        for blocks in output_content[output_file]['lines']:
            var_name = [line for line in blocks if line.strip().startswith('variable')][0].split('"')[1]
            var_default = [line for line in blocks if line.strip().startswith('default')]
            var_type = [line for line in blocks if line.strip().startswith('type')]
            
            # For getting bigger name
            names.append(var_name)

            # In case the default attribute is not a one-liner
            default_block = []
            for i, line in enumerate(blocks):
                if 'default' in line and ('{' in line or '[' in line) and not ('{}' in line or '[]' in line):
                    for line_ in islice(blocks, i, None):
                        if '{' in line_ or '[' in line_: bracket_count += 1
                        if '}' in line_ or ']' in line_: bracket_count -= 1
                        if bracket_count == 0: break
                        else: default_block.append(line_)

            # In case the type attribute is not a one-liner
            type_block = []
            bracket_count = 0
            for i, line in enumerate(blocks):
                if 'type' in line and ('{' in line or '[' in line):
                    for line_ in islice(blocks, i, None):
                        if '{' in line_ or '[' in line_: bracket_count += 1
                        if '}' in line_ or ']' in line_: bracket_count -= 1
                        if bracket_count == 0: break
                        else: type_block.append(line_)
            
            if len(default_block) != 0: 
                var_default = ''.join(default_block).split('=', 1)[1].strip()
                var_default = var_default.replace('list(', '[').replace('object(', '')
                if var_default[-1] != '}' or var_type[-1] != ']':
                    if '[' in var_default: var_default += '\n  ]'
                    if '{' in var_default: var_default += '\n  }'
            elif len(var_default) == 1: var_default = var_default[0].split('=', 1)[1].strip()
            else: var_default = "__required__"

            if len(type_block) != 0: 
                var_type = ''.join(type_block).split('=', 1)[1].strip()
                var_type = var_type.replace('list(', '[').replace('object(', '')
                if var_type[-1] != '}' or var_type[-1] != ']':
                    if '[' in var_type and not '{' in var_type: var_type += '\n  ]'
                    if '{' in var_type and not '[' in var_type: var_type += '\n  }'
            elif len(var_type) == 1: var_type = var_type[0].split('=', 1)[1].strip()
            else: var_type = "string"

            examples.append([{'name': var_name, 'default': var_default, 'type': var_type}])
            padding = len(max(names, key=len))

        with open(output_file, 'w') as out_file:
            out_file.write('<!-- BEGIN_TF_EXAMPLES -->\n')
            out_file.write('```hcl\n')
            out_file.write('module "%s" {\n' % metadata[output_file]['module'])
            out_file.write('  %s = %s\n' % ('source'.ljust(padding, ' '), metadata[output_file]['source']))
            for block in examples:
                for example in block:
                    out_file.write('  %s = %s [%s]\n' % (example['name'].ljust(padding, ' '), example['type'], example['default']))
            out_file.write('}\n')
            out_file.write('```\n')
            out_file.write('<!-- END_TF_EXAMPLES -->\n')
