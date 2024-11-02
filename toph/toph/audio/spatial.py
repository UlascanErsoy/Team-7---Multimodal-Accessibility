"""
Copyright (3d-Audio-Panner)
=====================
Copyright (c) 2020 Francisco Rotea

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import itertools
import os
from typing import Optional

import numpy as np
import numpy.linalg
import scipy.io
import scipy.signal
import scipy.spatial

from toph.audio.distance import BaseDistanceModel, IPLDistanceModel
from toph.audio.effect import Effect
from toph.audio.playable import Playable

CIPIC_BASE_PATH = os.getenv("CIPIC_PATH")

# Values of azimuth and elevation angles measured in the CIPIC database.
# See ´CIPIC_hrtf_database/doc/hrir_data_documentation.pdf´ for
# information about the coordinate system and measurement procedure.

AZIMUTH_ANGLES = [
    -80,
    -65,
    -55,
    -45,
    -40,
    -35,
    -30,
    -25,
    -20,
    -15,
    -10,
    -5,
    0,
    5,
    10,
    15,
    20,
    25,
    30,
    35,
    40,
    45,
    55,
    65,
    80,
]

# TRANSFER_FUNCTION (Emperical / Recorded / Measured)

ELEVATION_ANGLES = -45 + 5.625 * np.arange(0, 50)

POINTS = np.array(list(itertools.product(AZIMUTH_ANGLES, ELEVATION_ANGLES)))

# Get indexes from angles.

AZ = dict(zip(AZIMUTH_ANGLES, np.arange(len(AZIMUTH_ANGLES))))
EL = dict(zip(ELEVATION_ANGLES, np.arange(len(ELEVATION_ANGLES))))

# L = Window size.
# M = Length of impulse response.
# N = Size of the DFT. Since the length of the convolved signal will be
#     L+M-1, it is rounded to the nearest power of 2 for efficient fft
#     calculation.

L = 1024
M = 200
N = int(2 ** np.ceil(np.log2(np.abs(L + M - 1))))

L = N - M + 1

# Preallocate interpolated impulse responses.

interp_hrir_l = np.zeros(M)
interp_hrir_r = np.zeros(M)

# Radius of the azimuth and elevation circles (RADIUS_1) and radius of
# the circular trajectory in which they move (RADIUS_2). Both in pixels.

RADIUS_1 = 10
RADIUS_2 = 130


def butter_lp(cutoff, fs, order):
    """Design of a digital Butterworth low pass filter with a
    second-order section format for numerical stability."""

    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    sos = scipy.signal.butter(N=order, Wn=normal_cutoff, btype="lowpass", output="sos")

    return sos


def butter_lp_filter(signal, cutoff, fs=Playable.FRAME_RATE, order=1):
    """Filter a signal with the filter designed in ´butter_lp´.

    Filfilt applies the linear filter twice, once forward and once
    backwards, so that he combined filter has zero phase delay."""

    sos = butter_lp(cutoff=cutoff, fs=fs, order=order)
    out = scipy.signal.sosfiltfilt(sos, signal)

    return out


def butter_hp(cutoff, fs, order):
    """Design of a digital Butterworth high pass filter with a
    second-order section format for numerical stability."""

    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    sos = scipy.signal.butter(N=order, Wn=normal_cutoff, btype="highpass", output="sos")

    return sos


def butter_hp_filter(signal, cutoff, fs=Playable.FRAME_RATE, order=1):
    """Filter a signal with the filter designed in ´butter_hp´.

    Filfilt applies the linear filter twice, once forward and once
    backwards, so that he combined filter has zero phase delay."""

    sos = butter_hp(cutoff=cutoff, fs=fs, order=order)
    out = scipy.signal.sosfiltfilt(sos, signal)

    return out


def create_triangulation(points):
    """Generate a triangular mesh from HRTF measurement points (azimuth,
    elevation) using the Delaunay triangulation algorithm."""

    triangulation = scipy.spatial.Delaunay(points)

    return triangulation


def calculate_T_inv(triang, points):
    """Performs the calculation of the inverse of matrix T for all
    triangles in the triangulation and stores it in an array.

    Matrix T is defined as:

        T = [[A - C],
             [B - C]]

    where A, B and C are vertices of the triangle.

    Since T is independent of source position X, the precalculation of T
    allows to reduce the operational counts for finding the
    interpolation weights.

    For a more comprehensive explanation of this procedure, refer to:

    Gamper, H., Head-related transfer function interpolation in azimuth,
    elevation, and distance, J. Acoust. Soc. Am. 134 (6), December 2013.

    """

    A = points[triang.simplices][:, 0, :]
    B = points[triang.simplices][:, 1, :]
    C = points[triang.simplices][:, 2, :]

    T = np.empty((2 * A.shape[0], A.shape[1]))

    T[::2, :] = A - C
    T[1::2, :] = B - C

    T = T.reshape(-1, 2, 2)

    T_inv = np.linalg.inv(T)

    return T_inv


def interp_hrir(triang, points, T_inv, hrir_l, hrir_r, azimuth, elevation):
    """Estimate a HRTF for any point X lying inside the triangular mesh
    calculated.

    This is done by interpolating the vertices of the triangle enclosing
    X. Given a triangle with vertices A, B and C, any point X inside the
    triangle can be represented as a linear combination of the vertices:

    X = g_1 * A + g_2 * B + g_3 * C

    where g_i are scalar weights. If the sum of the weights is equal to
    1, these are barycentric coordinates of point X. Given a desired
    source position X, barycentric interpolation weights are calculated
    as:

    [g_1, g_2] = (X - C) * T_inv
    g_ 3 = 1 - g_1 - g_2

    Barycentric coordinates are used as interpolation weights for
    estimating the HRTF at point X as the weighted sum of the HRTFs
    measured at A, B and C, respectively.

    One of the main advantages of this interpolation approach is that
    it does not cause discontinuities in the interpolated HRTFs: for a
    source moving smoothly from one triangle to another, the HRTF
    estimate changes smoothly, even at the crossing point.

    For a more comprehensive explanation of the interpolation algorithm,
    please refer to:

    Gamper, H., Head-related transfer function interpolation in azimuth,
    elevation, and distance, J. Acoust. Soc. Am. 134 (6), December 2013.

    """

    position = [azimuth, elevation]
    triangle = triang.find_simplex(position)
    vert = points[triang.simplices[triangle]]

    X = position - vert[2]
    g = np.dot(X, T_inv[triangle])

    g_1 = g[0]
    g_2 = g[1]
    g_3 = 1 - g_1 - g_2

    if g_1 >= 0 and g_2 >= 0 and g_3 >= 0:
        interp_hrir_l[:] = (
            g_1 * hrir_l[AZ[vert[0][0]]][EL[vert[0][1]]][:]  # noqa
            + g_2 * hrir_l[AZ[vert[1][0]]][EL[vert[1][1]]][:]  # noqa
            + g_3 * hrir_l[AZ[vert[2][0]]][EL[vert[2][1]]][:]  # noqa
        )

        interp_hrir_r[:] = (
            g_1 * hrir_r[AZ[vert[0][0]]][EL[vert[0][1]]][:]  # noqa
            + g_2 * hrir_r[AZ[vert[1][0]]][EL[vert[1][1]]][:]  # noqa
            + g_3 * hrir_r[AZ[vert[2][0]]][EL[vert[2][1]]][:]  # noqa
        )

    return interp_hrir_l, interp_hrir_r


def get_circle_coords(angle, offset_x, offset_y):
    """Generate coordinates to create and move a circle in tkinter.

    (x0, y0): top left corner.
    (x1, y1): bottom right corner.

    """

    x_center = RADIUS_2 * np.cos(angle) + offset_x
    y_center = RADIUS_2 * np.sin(angle) + offset_y

    x0 = x_center - RADIUS_1
    y0 = y_center - RADIUS_1
    x1 = x_center + RADIUS_1
    y1 = y_center + RADIUS_1

    return (x0, y0, x1, y1)


TRI = create_triangulation(points=POINTS)
T_INV = calculate_T_inv(triang=TRI, points=POINTS)


class SpatialPanner(Effect):
    """Main page of the application."""

    def __init__(
        self,
        azimuth: float,
        elevation: float,
        distance: float = 1.0,
        distance_model: Optional[BaseDistanceModel] = None,
    ):
        """
        :param azimuth: azimuth of the direction angles (think l / r)
        :type azimuth: float
        :param elevation: elevation of the direction in angles
        :type azimuth: float
        :param distance: distance of the source in 1r 2r etc
        :type distance: float
        """
        # maybe implement a sensible auto-download for a default
        if not CIPIC_BASE_PATH:
            raise Exception("Please set CIPIC_BASE_PATH to your HRTF file")

        hrir = scipy.io.loadmat(CIPIC_BASE_PATH)

        self.azimuth: float = azimuth
        self.elevation: float = elevation
        self.distance: float = distance

        self._dist_model: BaseDistanceModel = distance_model or IPLDistanceModel()

        self.buffer_OLAP = np.zeros(M - 1)

        self.hrir_l: np.ndarray = np.array(hrir["hrir_l"])
        self.hrir_r: np.ndarray = np.array(hrir["hrir_r"])

    def apply(self, data: np.ndarray) -> np.ndarray:
        """Apply spatial effect"""
        output, cursor = [], 0

        # TODO: more efficient
        while cursor < len(data):
            output.append(self._apply_chunk(data[cursor : cursor + L]))
            cursor += L

        # TODO: think about keyframing in the future
        d = self._dist_model(self.distance)
        return d * np.hstack(output)

    def _apply_chunk(self, x: np.ndarray) -> np.ndarray:
        """Initialize the audio stream in callback mode and performs
        real-time convolution between the audio signal and the HRIR.

        The callback function is called in a separate thread whenever
        there's new audio data to play. This callback function performs
        the convolution between the audio signal and the interpolated
        HRIR at the specified position. In order to perform convolution
        in real time, the overlap-save method is implemented. This
        method consists on breaking the input audio signal into chunks
        of size L, transform the chunks into the frequency domain with
        the FFT and multiply it by the impulse response's DFT (i.e.
        convolution in time domain), transform back to the time domain
        and lop on the last L samples from the resulting L+M-1 chunk.

        For a detailed explanation of the algorithm, please refer to:

        Oppenheim, A. V. and Schafer, R. W., Discrete-Time Signal
        Processing, Second Edition, Prentice Hall, Chapter 8,
        pp. 582-588.

        """

        # Buffer to save overlap in each iteration (last M-1 samples are
        # appended to the start of each block).

        # Interpolate to get the HRIR at the position selected.

        hrir_l, hrir_r = interp_hrir(
            triang=TRI,
            points=POINTS,
            T_inv=T_INV,
            hrir_l=self.hrir_l,
            hrir_r=self.hrir_r,
            azimuth=self.azimuth,
            elevation=self.elevation,
        )

        x_l = np.convolve(x[0::2], hrir_l, mode="valid")
        x_r = np.convolve(x[0::2], hrir_r, mode="valid")

        nx = np.vstack((x_l, x_r)).T

        return nx.flatten()
