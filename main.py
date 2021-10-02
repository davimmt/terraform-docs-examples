import os
from itertools import islice

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
     
    @return => {'readme': {'metadata': {'module': 'name', 'source': 'path'}}, {'data': ['line']}}
    """
    readmes = {}
    for path in paths:
        module = path.split('/')[-1].split('-module')[0]
        readme = path + '/README.md'
        
        readmes[readme] = {'metadata': {'module': module, 'source': path}, 'data': []}
        for file in [files for files in paths[path]]:
            for line in open('%s/%s' % (path, file), 'r').readlines():
                while '  ' in line: line = line.replace('  ', ' ').strip()
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
            if line.startswith('variable'): inside_block = True
            if inside_block:
                if '{' in line or '[' in line: block_count += 1
                if '}' in line or ']' in line: block_count -= 1
                if block_count == 0: inside_block = False
            else:
                lines_to_ignore[readme].append(i)

    """ Grouping separete variable blocks in lists
    
    @return => {'readme': {'metadata': {'module': 'name', 'source': 'path'}}, {'data': ['line']}}
    """
    blocks = {}
    for readme in readmes:
        blocks[readme] = {}
        blocks[readme]['data'] = []
        block = []
        for i, line in enumerate(readmes[readme]['data']):
            if i not in lines_to_ignore[readme]:
                if line.startswith('variable'): 
                    if len(block) > 0: blocks[readme]['data'].append(block)
                    block = [line]
                elif i + 1 == len(readmes[readme]['data']): blocks[readme]['data'].append(block)
                else: block.append(line)
    
    """ Getting the biggest variable name for HCL-like padding
    
    @return => {'readme': {'metadata': {'module': 'name', 'source': 'path', 'padding': 'padding'}}, {'data': ['line']}}
    """
    for readme in readmes:
        names = [name.split('"')[1].strip() for name in readmes[readme]['data'] if name.startswith('variable')]
        readmes[readme]['metadata']['padding'] = len(max(names, key = len))

    """ Substituting the first lines-based dictionary/list
        to a blocks-based dictionary/list
    
    @return => {'readme': {'metadata': {'module': 'name', 'source': 'path'}}, {'data': [['block_line']}}
    """ 
    for readme in readmes:
        readmes[readme]['data'] = []
        for block in blocks[readme]['data']:
            readmes[readme]['data'].append(block) 

    for readme in readmes:
        with open(readme, 'w') as file:
            file.write('<!-- BEGIN_TF_EXAMPLES -->')
            file.write('\nmodule "%s"' % (readmes[readme]['metadata']['module']))
            file.write('\n  %s = %s' % ('source', readmes[readme]['metadata']['source']))
            
            for block in readmes[readme]['data']:
                name = [name.split('"')[1].strip() for name in block if name.startswith('variable')][0]
                type = [type.split('=')[1].strip() for type in block if type.startswith('type')]
                default = [default.split('=')[1].strip() for default in block if default.startswith('default')]
                if not type: type = ["string"]
                if not default: default = ["__required__"]
                file.write('\n  %s = %s' % (name.ljust(readmes[readme]['metadata']['padding'], ' '), type[0]))

            file.write('\n}')
            file.write('\n<!-- END_TF_EXAMPLES -->')
