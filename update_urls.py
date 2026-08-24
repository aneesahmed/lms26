import os
import glob

def replace_urls():
    frontend_dir = r"C:\working\AI26\lms26\frontend\src"
    
    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            if file.endswith((".tsx", ".ts")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                if "http://localhost:8000/" in content:
                    new_content = content.replace("http://localhost:8000/", "/api/")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {file_path}")

if __name__ == "__main__":
    replace_urls()
