import os,sys,subprocess

def get_all_terraform_files():
   files_cmd = subprocess.Popen("find . -type f -name '*.tf'", shell=True, stdout=subprocess.PIPE) 
   return list(filter(None, files_cmd.stdout.read().decode('ascii').split('\n')))

if __name__ == "__main__":
    files = get_all_terraform_files() 
    for file in files:
        print('Working on [%s] file' % (file))
        source_path = os.path.dirname(file)
        module_name = source_path.split('/')[-1].split('-module')[0]
        readme_md = source_path + '/README.md'
        blocks = {}
        bigger_argument = 6 # source
        record_mode = 0
        lines_to_merge = []

        print(' 1. Reading .tf file')
        input_file = open(file, 'r').readlines()
        for number, line in enumerate(input_file):
            if 'variable' in line and '{' in line:
                record_mode += 1
                variable_name = line.split('"')[1].strip()
                blocks[variable_name] = {}
            elif 'validation {' in line and record_mode > 0:
                record_mode -= 1
            elif '}' in line and record_mode == 0:
                record_mode += 1
            elif '}' in line and record_mode > 0 and not '{}' in line:
                record_mode -= 1
            elif line.replace(' ', '') in ['\n', '\r\n']:
                pass
            elif record_mode > 0 and not 'validation {' in line:
                # For variables with default list(object({}))
                if 'default' in line and '= [\n' in line and '{' in input_file[number+1]:
                    for number_default, line_default in enumerate(input_file[number:]):
                        lines_to_merge.append(input_file[number_default+1])
                        if '}\n' in line_default and ']\n' in input_file[number_default]:
                            break
                # For variables type list(object({}))
                elif 'type' in line and '= list(object({\n' in line:
                    for number_type, line_type in enumerate(input_file[number:]):
                        lines_to_merge.append(input_file[number:][number_type])
                        if '}))\n' in line_type:
                            break
                if lines_to_merge:
                    argument = lines_to_merge[0].split('=')[0].strip()
                    lines_to_merge.pop(0)
                    if argument == 'default':
                        value = '[\n' + ''.join(str(item) for item in lines_to_merge)
                        value = value[:-1] + '\n  ]'
                    if argument == 'type':
                        value = 'list(object({\n' + ''.join(str(item) for item in lines_to_merge)
                        value = value[:-1]
                    blocks[variable_name][argument] = value
                    lines_to_merge = []
                elif ('type' in line or 'default' in line) and '=' in line:
                    argument_value = line.split('=')
                    argument = argument_value[0].strip()
                    value = argument_value[1].strip()
                    blocks[variable_name][argument] = value
                    if len(variable_name) > bigger_argument:
                        bigger_argument = len(variable_name)

        # Check if its a new file
        begin_line = True
        try:
            subprocess.check_output(['grep', 'BEGIN_TF_EXAMPLES', readme_md])
        except subprocess.CalledProcessError as e:
            begin_line = False
        if not begin_line:
            with open(readme_md, 'a') as readme:
                readme.write('\n<!-- BEGIN_TF_EXAMPLES -->')
                readme.write('\n<!-- END_TF_EXAMPLES -->')

        print(' 2. Reading .md file')
        original_readme = open(readme_md, 'r').readlines()
        record_mode = 0
        dict_original_lines = {}
        lines_to_delete = []
        for number, line in enumerate(original_readme):
            dict_original_lines[number] = line
            if 'BEGIN_TF_EXAMPLES' in line:
                record_mode = 1
                begin_line = number 
                dict_original_lines[number] = []
            elif 'END_TF_EXAMPLES' in line:
                record_mode = 0
            elif record_mode:
                lines_to_delete.append(number)
        for line in lines_to_delete:
            dict_original_lines.pop(line)
        dict_original_lines[begin_line].append('<!-- BEGIN_TF_EXAMPLES -->')
        dict_original_lines[begin_line].append('\n## Example')
        dict_original_lines[begin_line].append('\n```hcl')
        dict_original_lines[begin_line].append('\nmodule "%s" {' % (module_name)) 
        dict_original_lines[begin_line].append('\n  %s = %s\n' % ('source'.ljust(bigger_argument), source_path))
        for block in blocks:
           if 'default' in blocks[block]:
               if 'type' in blocks[block]:
                   dict_original_lines[begin_line].append('  %s = %s [%s]\n' % (block.ljust(bigger_argument), blocks[block]['type'], blocks[block]['default']))
               else:
                   dict_original_lines[begin_line].append('  %s = string [%s]\n' % (block.ljust(bigger_argument), blocks[block]['default']))
           else:
               if 'type' in blocks[block]:
                   dict_original_lines[begin_line].append('  %s = %s [__required__]\n' % (block.ljust(bigger_argument), blocks[block]['type']))
               else:
                   dict_original_lines[begin_line].append('  %s = string [__required__]\n' % (block.ljust(bigger_argument)))
        dict_original_lines[begin_line].append('}') 
        dict_original_lines[begin_line].append('\n```\n')

        print(' 3. Writing to .md file')
        with open(readme_md, 'w') as readme:
            for line in dict_original_lines:
                if line != begin_line:
                    readme.write(dict_original_lines[line])
                else:
                    for new_lines in dict_original_lines[line]:
                        readme.write(new_lines)
            print('Completed!\n')
