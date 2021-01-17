import cv2
import imutils
import csv
import numpy as np

class ColorDescriptor:
	def __init__(self, bins):
		# store the number of bins for the 3D histogram
		self.bins = bins

	def describe(self, image):
		# convert the image to the HSV color space and initialize
		# the features used to quantify the image
		image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		features = []

		# grab the dimensions and compute the center of the image
		(h, w) = image.shape[:2]
		(cX, cY) = (int(w * 0.5), int(h * 0.5))

		# divide the image into four rectangles/segments (top-left,
		# top-right, bottom-right, bottom-left)
		segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h),
			(0, cX, cY, h)]

		# construct an elliptical mask representing the center of the
		# image
		(axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
		ellipMask = np.zeros(image.shape[:2], dtype = "uint8")
		cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)

		# loop over the segments
		for (startX, endX, startY, endY) in segments:
			# construct a mask for each corner of the image, subtracting
			# the elliptical center from it
			cornerMask = np.zeros(image.shape[:2], dtype = "uint8")
			cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
			cornerMask = cv2.subtract(cornerMask, ellipMask)

			# extract a color histogram from the image, then update the
			# feature vector
			hist = self.histogram(image, cornerMask)
			features.extend(hist)

		# extract a color histogram from the elliptical region and
		# update the feature vector
		hist = self.histogram(image, ellipMask)
		features.extend(hist)

		# return the feature vector
		return features

	def histogram(self, image, mask):
		# extract a 3D color histogram from the masked region of the
		# image, using the supplied number of bins per channel
		hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins,
			[0, 180, 0, 256, 0, 256])

		# normalize the histogram if we are using OpenCV 2.4
		if imutils.is_cv2():
			hist = cv2.normalize(hist).flatten()

		# otherwise handle for OpenCV 3+
		else:
			hist = cv2.normalize(hist, hist).flatten()

		# return the histogram
		return hist



class Searcher:
	def __init__(self, indexPath, dist_type = 'city_block'):
    	# store our index path
		self.indexPath = indexPath
		self.dist_type = dist_type

	def search(self, queryFeatures, limit = 10):
    # initialize our dictionary of results  
		results = {}

		# open the index file for reading
		with open(self.indexPath, 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				features = np.array([float(x) for x in row[1:]])
				d = 0
				if self.dist_type == "chi_square":
					d = self.chi2_distance(features, queryFeatures)
				elif self.dist_type == "city_block":
					d = self.city_block(features, queryFeatures)

				results[row[0]] = d

		f.close()
		results = sorted([(v, k) for (k, v) in results.items()])

		# return our (limited) results
		return results[:limit]

	def chi2_distance(self, histA, histB, eps = 1e-10):
		# compute the chi-squared distance
		d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
		for (a, b) in zip(histA, histB)])
		return d
  
	def city_block(self, histA, histB):
		return np.sum(np.absolute(histA - histB))





def search_image(query_path, index_path="D:/web_dev/engine/beta_index_color.csv"):
	cd = ColorDescriptor((8,12,3))

	query = cv2.imread(query_path)

	features = cd.describe(query)
	features = np.array(features)

	searcher = Searcher(index_path)
	results = searcher.search(features)
	results = [(k, _) for _, k in results]
	return results

# path = 'D:/Web_dev/engine/queries/'
# query = '103100.png'
# results = search_image(path + query)
# print(f'Query {query}: {results}')