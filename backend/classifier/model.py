import util as model_utils
from librosa import load, feature, core
from librosa import util as librosa_util
import logging
import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import distance 
from emd import emd
from os.path import join
from data_handler import fetch_signature, persist_signature, is_signature_cached, AUDIOCLIPS_FOLDER

'''
	The module closely follows the approach proposed in 'http://www.hpl.hp.com/techreports/Compaq-DEC/CRL-2001-2.pdf'
'''
FRAME_TIMESTEP = 250 * 0.001 # s
FRAME_START = 100
FRAME_TOTAL = 500
CLUSTERS_PER_SIGNATURE = 16
N_MFCCS = 20
MFCSS_OFFSET = 7
SAMPLE_RATE = 11025

GROUND_DISTANCES = {
	"euclidean": 0,
	"kullback-leibler": 1,
}

def calculate_distance_matrix(signature1, signature2, ground_distance = None, use_covar = False):

	dist_matrix = []
	for cluster1 in signature1:
		cl1_mean, cl1_covar, cl1_weight = get_cluster_params(cluster1)
		
		distance_row = []
		for cluster2 in signature2:
			cl2_mean, cl2_covar, cl2_weight = get_cluster_params(cluster2)

			if ground_distance == GROUND_DISTANCES["euclidean"]:
				distance_row.append(distance.euclidean(cl1_mean, cl2_mean))

			if ground_distance == GROUND_DISTANCES["kullback-leibler"]:
				distance_row.append(0)

		if ground_distance == GROUND_DISTANCES["kullback-leibler"]:
			logging.warn("Kullback-Leibler metric not implemented!")

		distance_row = np.array(distance_row)
		dist_matrix.append(distance_row)

	return np.array(dist_matrix)

# This right here ... is the sh*t. 
def calculate_emd(signature1, signature2):
	D = calculate_distance_matrix(signature1, signature2, ground_distance = GROUND_DISTANCES["euclidean"])

	signature1_points = [ cl[0] for cl in signature1]
	signature1_weights = [ cl[2] for cl in signature1 ]
	signature1_weights = np.array(map(lambda x: float(x)/sum(signature1_weights), signature1_weights))

	signature2_points = [ cl[0] for cl in signature2]
	signature2_weights = [ cl[2] for cl in signature2 ]
	signature2_weights = np.array(map(lambda x: float(x)/sum(signature2_weights), signature2_weights))

	return emd(
				signature1_points, signature2_points, 
				X_weights = signature1_weights, Y_weights = signature2_weights, 
			  	distance = 'precomputed', D = D
			)


def compute_spectral_signature(song_id, cached = True, use_covar = True):

	if cached and is_signature_cached(song_id):
		return fetch_signature(song_id)

	audioclip_path = join(AUDIOCLIPS_FOLDER, "{0}.mp3".format(song_id))
	waveform, sample_rate, frame_length, frames = None, None, None, None
	try:
		waveform, sample_rate = load(audioclip_path, sr=SAMPLE_RATE)
		frame_length = core.time_to_samples(np.arange(0, 2, FRAME_TIMESTEP), sr = sample_rate)[1]
		frames = librosa_util.frame(y = waveform, frame_length = frame_length, hop_length = frame_length)
	except Exception as e:
		logging.warn("Couldn't preprocess audioclip '{0}': {1}".format(audioclip_path, str(e)))
		return None

	# The 'frames' array has shape (<frame_length>, <number_of_frames>)
	# hence, we transpose it. This holds true for every call to the librosa library that returns an array.
	frames = frames.T

	spectrograms = []
	for frame in frames[FRAME_START: FRAME_START + FRAME_TOTAL]:
		spectrogram = feature.mfcc(y = frame, sr = frame_length).T
		to_add = [ entry[MFCSS_OFFSET : MFCSS_OFFSET+N_MFCCS] for entry in spectrogram ]
		spectrograms += to_add
	
	spectrograms = np.array(spectrograms)
	clusters = KMeans(n_clusters = CLUSTERS_PER_SIGNATURE)
	model = clusters.fit(spectrograms)

	# A song's "signature" is an array [ ( u_i, s_i, w_i ) ... ]. Where 0 <= i < CLUSTERS_PER_SIGNATURE
	# The triple (u_i, s_i, w_i) contains these variables:
	# 	u_i : Mean for Cluster i
	#	s_i : Covariance for Cluster i
	#	w_i : Weight for Cluster i
	
	signature = []
	for label in xrange(CLUSTERS_PER_SIGNATURE):
		indexes = [ index for index, element in enumerate(model.labels_) if element == label ]
		cluster_points = [ spectrograms[i] for i in indexes ]

		mean = model.cluster_centers_[label]
		covariance = np.cov(cluster_points) if use_covar else []
		weight = len(cluster_points)
		cluster_params = (mean, covariance, weight)

		signature.append(cluster_params)

	persist_signature(song_id, signature)
	
	return signature

def get_cluster_params(cluster):
	return cluster[0], cluster[1], cluster[2]