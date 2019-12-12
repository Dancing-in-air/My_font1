"""
利用matplotlib模块可以获取字体形状
"""

import matplotlib.pyplot as plt
import re

str = """"
    <TTGlyph name="uniF0BA" xMin="0" yMin="-43" xMax="529" yMax="697">
      <contour>
        <pt x="147" y="173" on="1"/>
        <pt x="147" y="103" on="0"/>
        <pt x="222" y="35" on="0"/>
        <pt x="278" y="35" on="1"/>
        <pt x="343" y="35" on="0"/>
        <pt x="381" y="84" on="1"/>
      </contour>
      <instructions/>
    </TTGlyph>
"""
x = [int(i) for i in re.findall(r'<pt x="(.*?)" y=', str)]
y = [int(i) for i in re.findall(r'y="(.*?)" on=', str)]
print(x)
print(y)
plt.plot(x, y)
plt.show()
# import tesserocr
# from PIL import Image
#
# img = Image.open("Figure_1.png")
# result = tesserocr.image_to_text(img)
# print(result)

# from fontTools.ttLib import TTFont
#
# font = TTFont("word_base.woff")
# ret = font.getGlyphOrder()
# print(ret)
# for i in ret[1:]:
#     ret2 = font["glyf"][i].coordinates
#     print(ret2)
