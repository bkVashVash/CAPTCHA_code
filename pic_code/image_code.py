import tesserocr
from PIL import Image

image = Image.open('code2.jpg')

'''转化为灰度图像'''
image = image.convert('L')
threshold = 127
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
# print(table)
'''指定二值化阀值'''
image = image.point(table, '1')
image.show()

result = tesserocr.image_to_text(image)
print(result)