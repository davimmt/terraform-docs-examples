import os,sys,subprocess
from itertools import islice

def get_all_terraform_files():
    """Returns a list with path/name of the chosen files.

    Uses the Unix 'find' package to recursivly search the
    specified files in the defined scope.
    """
    files_cmd = subprocess.Popen("find . -type f -name '*.tf'", shell=True, stdout=subprocess.PIPE) 
    return list(filter(None, files_cmd.stdout.read().decode('ascii').split('\n')))

def remove_whitespaces(string):
    """Returns a string completly stripped.

    Replaces all whitespaces between chars with only one whitespace,
    and removes all trailling whitespaces.
    """
    while '  ' in string: string = string.replace('  ', ' ')
    return string.strip()

def get_raw_lines(file_lines):
    """Returns a list of all the lines.

    Reads all the lines and uses the remove_whitespaces()
    for each string, and stores in a list.
    """
    raw_lines = []
    for line in file_lines:
        line = remove_whitespaces(line)
        if line != '': raw_lines.append(line)
    return raw_lines

def get_block(i, lines):
    """Returns a list of lines to work with.

    Reads all the lines below the defined string (in the main), and
    stores all the line numbers that are inside that block in a list.
    In this case, it returns all lines from a variable block.
    """
    child_i = i
    lines_to_get = [lines[child_i]]
    bracket_count = 0
    for line in islice(lines, i, None):
        if '{' in line: bracket_count += 1
        if '}' in line: bracket_count -= 1
        if bracket_count != 0:
            child_i += 1
            if lines[child_i].startswith('default = ') or \
            lines[child_i].startswith('type = '): # or \
            #(bracket_count == 1 and lines[child_i] == '}'):
                lines_to_get.append(lines[child_i])
        else:
            break 
    return lines_to_get

if __name__ == "__main__":
    files = get_all_terraform_files() 

    readme_dict = {}
    metadata_dict = {}
    for file in files:
        print('Working on [%s] file' % (file))
        source_path = os.path.dirname(file)
        module_name = source_path.split('/')[-1].split('-module')[0]
        readme_md = source_path + '/README.md'
        metadata_dict[readme_md] = {'source': source_path, 'module': module_name}

        print('  Grouping file to its path README.md')
        if not readme_md in readme_dict: readme_dict[readme_md] = {'files': [], 'lines': []}
        readme_dict[readme_md]['files'].append(file)

    print('\nGrouping all lines from the files to their path README.md\n')
    for readme_md in readme_dict: 
        for file in readme_dict[readme_md]['files']:
            lines = get_raw_lines(open(file, 'r').readlines())
            
            for i, line in enumerate(lines):
                if line.startswith('variable "') and line.endswith('" {'): 
                   readme_dict[readme_md]['lines'].append(get_block(i, lines))

    output_dict = {}
    for readme_md in readme_dict:
        output_dict[readme_md] = []
        for line_block in readme_dict[readme_md]['lines']: 
            var_name = line_block[0].split('"')[1]
            var_type = "string"
            var_default = "__required__"

            default = [x for x in line_block if x.startswith('default =')]
            type_ = [x for x in line_block if x.startswith('type =')]
            if len(default) > 0: var_default = default[0].split('=', 1)[1].strip()
            if len(type_) > 0: var_type = type_[0].split('=', 1)[1].strip()
            
            output_dict[readme_md].append({'name': var_name, 'type': var_type, 'default': var_default}) 

    for file in output_dict:
        # Check if has BEGIN_TF_EXAMPLES
        try:
            subprocess.check_output(['grep', 'BEGIN_TF_EXAMPLES', file])
        except subprocess.CalledProcessError as e:
            with open(file, 'a') as readme_md:
                readme_md.write('\n<!-- BEGIN_TF_EXAMPLES -->')
                readme_md.write('\n<!-- END_TF_EXAMPLES -->')

        # Find bigger string length for HCL-padding
        names = []
        for line_block in output_dict[file]: names.append(line_block['name'])
        padding = len(max(names, key=len))

        print('Writing [%s] file' % file)
        #print(file)
        #print('module "%s" {' % metadata_dict[file]['module'])
        #print('  %s = "%s"' % ('source'.ljust(padding, ' '), metadata_dict[file]['source']))
        #for line_block in output_dict[file]:
            #print('  %s = %s [%s]' % (line_block['name'].ljust(padding, ' '), line_block['type'], line_block['default']))
        #print('}')
