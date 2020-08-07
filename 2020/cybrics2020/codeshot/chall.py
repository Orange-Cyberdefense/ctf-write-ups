from helpers import apply_blur_filter

app = Flask (__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = '__________9ftys7dfstf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 # 500Kb

Bootstrap (app)
db = SQLAlchemy (app)

def apply_blur_filter(im, start=(0, 0), end=(1, 1), PIXELIZATION=8):
	def make_one_square(img, old, row, col, size):
		try:
			npix = []
			for ni in range(row - PIXELIZATION, row + PIXELIZATION):
				for nj in range(col - PIXELIZATION, col + PIXELIZATION):

					if ni == col and nj == col: continue
					if ni < 0 or nj < 0: continue
					if ni >= size[1] or nj >= size[0]: continue

					npix.append(old[nj, ni])

			av_r = 0
			av_g = 0
			av_b = 0
			for r, g, b in npix:
				av_r += r
				av_g += g
				av_b += b
			av_r //= len(npix)
			av_g //= len(npix)
			av_b //= len(npix)
			img[col, row] = (av_r, av_g, av_b)
		except Exception as e:
			logging.error (e)
			logging.error (row)
			logging.error (col)
			logging.error (size)

	new_image = im.copy()
	old_image_pix = im.load()
	new_image_pix = new_image.load()

	for i in range(10 + start[0] * 42, 10 + end[0] * 42):
		for j in range(10 + start[1] * 10, 10 + end[1] * 10):
			make_one_square (new_image_pix, old_image_pix, i, j, size=new_image.size)
	return new_image