cimport numpy as np
import numpy as np
cimport cython

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef np.ndarray[np.int_t, ndim=1, mode='c'] findOptimalSeam(np.ndarray[np.float64_t, ndim=2, mode='c'] s, stopFunc=None): 
    """
    Finds optimal adjacent pixels in every row.
    These pixels minimize the energy s.
    @param s The energy function (a numpy array)
    @param stopFunc Function, stopFunc()==True stops the algorithm.
    @return A vector M. The size of its elements are equal to the size of s rows.
            The value M[i] gives the best column of the pixel at the row i.
            If it is impossible to return a seam that has not the energy infinity or if
            the algorithm has stopped, None will be returned.
    """
    cdef np.int_t c, r
    cdef np.int_t M,N, left, right, j, minCol
    cdef np.ndarray[np.int_t, ndim=3, mode='c'] Pointer
    cdef np.ndarray[np.int_t, ndim=1] minPointer, seam
    cdef np.int_t prevR, row
    cdef np.ndarray[np.float64_t, ndim=2, mode='c'] C

    M, N = s.shape[:2]

    C = np.zeros((M, N), dtype=np.float64)
    Pointer = np.zeros((M, N, 2), dtype=np.int)
    # Fill first row with 0
    for c in range(0, N):
        C[0, c] = s[0, c]
    # Then compute for every column in every row the best neighbor above
    for r in range(1, M):
        for c in range(N):
            if stopFunc and stopFunc():
                return None
            left = max(c - 1, 0)
            right = min(N - 1, c + 1)
            j = left + np.argmin(C[r - 1, left:right + 1])
            # Set the energy
            C[r, c] = C[r - 1, j] + s[r, c]
            # Set the neighbor
            Pointer[r, c, 0] = r-1
            Pointer[r, c, 1] = j
    # Find the way with the lowest energy
    minCol = np.argmin(C[M - 1, :])
    if C[M - 1, minCol] == np.inf:
        return None
    # Creating the result
    seam = np.zeros(M, dtype=np.int)
    seam[M - 1] = minCol
    minPointer = Pointer[M - 1, minCol]
    for y in range(-M + 1, 0):
        prevR, row = minPointer
        seam[prevR] = row
        minPointer = Pointer[prevR, row]
    return seam
