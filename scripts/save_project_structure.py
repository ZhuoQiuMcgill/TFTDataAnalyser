import os


def save_project_structure(root_dir, output_file):
    # List of directories to ignore
    ignore_dirs = ['venv', '.idea', '.git', 'cache']

    with open(output_file, 'w') as file:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Exclude directories based on ignore list and those starting with '__'
            if any(part in ignore_dirs or part.startswith('__') for part in dirpath.split(os.sep)):
                continue
            # Calculate indentation based on directory depth
            depth = dirpath.replace(root_dir, '').count(os.sep)
            indent = '    ' * depth
            # Write the directory name
            file.write(f'{indent}{os.path.basename(dirpath)}/\n')
            sub_indent = '    ' * (depth + 1)
            # Write all filenames in the directory, ignoring those starting with '__'
            for filename in filenames:
                if not filename.startswith('__'):
                    file.write(f'{sub_indent}{filename}\n')


if __name__ == '__main__':
    root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_path = os.path.join(root_directory, 'project_structure.txt')
    save_project_structure(root_directory, output_path)
    print(f'Project structure saved to {output_path}')
