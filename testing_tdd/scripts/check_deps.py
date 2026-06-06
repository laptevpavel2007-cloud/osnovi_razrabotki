import ast
import sys
import os

IGNORE_MODULES = {
    'ast', 'sys', 'os', 'typing', 'collections', 'itertools', 'functools',
    'pathlib', 'json', 're', 'datetime', 'time', 'math', 'random',
    'ndfl' }

def get_imports(directories: list) -> set:
    imports = set()
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        try:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        imports.add(alias.name.split('.')[0])
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        imports.add(node.module.split('.')[0])
                        except SyntaxError:
                            print(f"Syntax error in {filepath}, skipping.")
    return imports

def get_requirements(req_file: str) -> set:
    reqs = set()
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg = line.split('[')[0].split('==')[0].split('>=')[0].split('<=')[0].strip()
                    reqs.add(pkg.lower())
    return reqs

if __name__ == '__main__':
    src_dirs = ['src', 'tests']
    req_file = 'requirements.txt'

    if not os.path.exists(req_file):
        print(f"Файл зависимостей {req_file} не найден.")
        sys.exit(1)

    raw_imports = get_imports(src_dirs)
    imports = {imp for imp in raw_imports if imp.lower() not in IGNORE_MODULES}
    reqs = get_requirements(req_file)

    missing = imports - reqs
    
    if missing:
        print(f"Ошибка: следующие импортируемые пакеты отсутствуют в {req_file}:")
        for pkg in sorted(missing):
            print(f"   - {pkg}")
        sys.exit(1)
    else:
        print("Проверка зависимостей пройдена: все импорты покрыты requirements.txt")
        sys.exit(0)