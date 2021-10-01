import os
from itertools import islice

if __name__ == "__main__":
    # Getting all *-module directories and its *.tf files
    # @return => {'./dir-module': ['file.tf', 'file.tf']}
    paths = {}
    for dir in [dir[0] for dir in os.walk('.') if dir[0].endswith('-module')]:
        files = [file for file in os.listdir(dir) if file.endswith('.tf')]
        if files:
            paths[dir] = []
            paths[dir] += files

    # Grouping all lines from all files in a directory
    # @return => {'readme': {'metadata': {'module': 'name', 'source': 'path'}},
    #                       {'data': ['line', 'line']}}
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

    # Remove all lines that don't belong to a variable block
    for readme in readmes:
        inside_block = False
        block_count = 0
        for line in readmes[readme]['data']:
            if line.startswith('variable'): 
                inside_block = True
            if inside_block:
                if '{' in line or '[' in line: block_count += 1
                if '}' in line or ']' in line: block_count -= 1
                if block_count == 0: inside_block = False
                print('1', line)
            else: 
                print(inside_block, block_count, line)
                readmes[readme]['data'].remove(line)

    exit()
    for readme in readmes:
        for i, line in enumerate(readmes[readme]['data']):
            print(line)
