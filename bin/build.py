import os
import glob
import shutil

def main():
  if os.path.exists("dist/") and os.path.isdir("dist/"):
    print("removing previous dist/ directory")
    shutil.rmtree("dist/")
  if not os.path.exists("dist/"):
    print("dist does not exist, making it.")
    os.mkdir("dist/")
  files = glob.glob("public/*")
  print(f"copying files: {files}")
  for file in files:
    shutil.copy(file, "dist/")
  
if __name__ == "__main__":
  try:
    main()
  except Exception as ex:
    print(str(ex))
