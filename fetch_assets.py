# Netlifyのビルド時に、AIで生成したアフロ画像とシェア画像を取り込む
import io, os, shutil, urllib.request, zipfile
URL = "https://d2ol7oe51mr4n9.cloudfront.net/user_31yooolqoANbIndQb0GB3n5uKCW/0ff59efd-b8e4-40db-9e61-b5cd4df781ff.zip"
root = os.path.dirname(os.path.abspath(__file__))
data = urllib.request.urlopen(URL, timeout=60).read()
with zipfile.ZipFile(io.BytesIO(data)) as z:
    z.extractall(os.path.join(root, "afro"))
shutil.move(os.path.join(root, "afro", "og-top.png"), os.path.join(root, "og.png"))
print("assets ok:", len(data), "bytes")
