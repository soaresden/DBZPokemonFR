import glob, sys
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + '_*.png')); ims = [Image.open(f) for f in fs]
W, H = ims[0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (W * cols, H * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * W, (i // cols) * H))
sheet.save(sys.argv[1] + '_sheet.png'); print(len(ims))
