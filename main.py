import os
import subprocess
import re


class IncludeCleaner:
    def __init__(self, project_root, compile_script):
        """
        Initialize the Include Cleaner

        :param project_root: Root directory of the project
        :param compile_script: Full path to the compilation script
        """
        self.project_root = os.path.abspath(project_root)
        self.compile_script = compile_script
        self.source_extensions = ['.c', '.cpp', '.h', '.hpp']

    def find_source_files(self):
        """
        Find all source files in the project

        :return: List of source file paths
        """
        source_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if any(file.endswith(ext) for ext in self.source_extensions):
                    source_files.append(os.path.join(root, file))
        return source_files

    def extract_includes(self, file_path):
        """
        Extract all include statements from a file

        :param file_path: Path to the source file
        :return: List of include statements
        """
        with open(file_path, 'r') as f:
            content = f.read()

        # Match both angle bracket and quote includes
        includes = re.findall(r'^\s*#include\s*[<"](.+?)[>"]', content, re.MULTILINE)
        return includes

    def remove_include(self, file_path, include_to_remove):
        """
        Remove a specific include from a file

        :param file_path: Path to the source file
        :param include_to_remove: Include statement to remove
        :return: Modified file content
        """
        with open(file_path, 'r') as f:
            content = f.read()

        # Remove the specific include
        modified_content = re.sub(
            fr'^\s*#include\s*[<"]({re.escape(include_to_remove)})[>"].*\n?',
            '',
            content,
            flags=re.MULTILINE
        )

        with open(file_path, 'w') as f:
            f.write(modified_content)

        return modified_content

    def restore_include(self, file_path, original_content):
        """
        Restore the original file content

        :param file_path: Path to the source file
        :param original_content: Original file content
        """
        with open(file_path, 'w') as f:
            f.write(original_content)

    def compile_project(self):
        """
        Compile the project using the specified compile script

        :return: True if compilation succeeds, False otherwise
        """
        try:
            result = subprocess.run(
                self.compile_script,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Compilation error: {e}")
            return False

    def clean_includes(self):
        """
        Main method to clean unnecessary includes
        """
        source_files = self.find_source_files()

        for file_path in source_files:
            # Skip if not a source or header file
            if not any(file_path.endswith(ext) for ext in self.source_extensions):
                continue

            # Get includes for this file
            includes = self.extract_includes(file_path)

            # Store original content for restoration
            with open(file_path, 'r') as f:
                original_content = f.read()

            # Try removing each include
            for include in includes:
                # Remove the include
                self.remove_include(file_path, include)

                # Try to compile
                if self.compile_project():
                    print(f"Removed unnecessary include: {include} from {file_path}")
                else:
                    # Compilation failed, restore the include
                    print(f"Keep include: {include} in {file_path}")
                    self.restore_include(file_path, original_content)

        print("Include cleanup complete!")


def main():
    # Example usage
    project_root = '/path/to/your/project'
    compile_script = './build.sh'  # Your specific compilation script

    cleaner = IncludeCleaner(project_root, compile_script)
    cleaner.clean_includes()


if __name__ == "__main__":
    main()
