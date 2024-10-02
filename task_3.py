import pandas as pd

class Solution:
    def __init__(self, excel_file_path, task1_output_sheet_name, task2_output_sheet_name, markdown_file_path):
        self.excel_file_path = excel_file_path
        self.task1_output_sheet_name = task1_output_sheet_name
        self.task2_output_sheet_name = task2_output_sheet_name
        self.markdown_file_path = markdown_file_path
        self.task1_df = pd.read_excel(self.excel_file_path, sheet_name=self.task1_output_sheet_name)
        self.task2_df = pd.read_excel(self.excel_file_path, sheet_name=self.task2_output_sheet_name, header=None)

    def convert_to_markdown(self, df, title):
        md_table = df.to_markdown(index=False)
        return f"## {title}\n\n{md_table}\n"

    def generate_markdown_file(self):
        task1_md = self.convert_to_markdown(self.task1_df, "Task 1 Results")
        task2_md = self.convert_to_markdown(self.task2_df, "Task 2 Results")

        # Combine markdown content
        combined_md = task1_md + "\n" + task2_md

        # Write to a single Markdown file
        with open(self.markdown_file_path, 'w') as f:
            f.write(combined_md)

def main():
    solution = Solution(
        excel_file_path='Avengers_vs_Invaders_Challenge.xlsx',
        task1_output_sheet_name='Task1',
        task2_output_sheet_name='Task2',
        markdown_file_path='tasks_3_results.md'
    )

    solution.generate_markdown_file()

if __name__ == "__main__":
    main()
