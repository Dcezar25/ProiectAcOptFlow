import numpy as np
import cv2
from scipy.signal import convolve2d

def compute_derivatives(im1, im2):
    """
    Calculeaza Ix, Iy, It folosind filtre Sobel si diferente finite.
    Conform documentatiei.
    """
    # Kernels Sobel 3x3
    kernel_x = np.array([[-1, 0, 1], 
                         [-2, 0, 2], 
                         [-1, 0, 1]]) / 8.0
                         
    kernel_y = np.array([[-1, -2, -1], 
                         [ 0,  0,  0], 
                         [ 1,  2,  1]]) / 8.0
    
    # Netezire Gaussiană prealabilă (recomandat pentru stabilitate [cite: 89])
    im1 = cv2.GaussianBlur(im1, (3, 3), 0)
    im2 = cv2.GaussianBlur(im2, (3, 3), 0)

    # Derivatele spatiale (Ix, Iy) - aplicam pe prima imagine sau media lor
    fx = convolve2d(im1, kernel_x, mode='same', boundary='symm')
    fy = convolve2d(im1, kernel_y, mode='same', boundary='symm')
    
    # Derivata temporala (It)
    ft = im2 - im1
    
    return fx, fy, ft

def horn_schunck_optical_flow(im1, im2, alpha=1.0, iterations=100):
    """
    Implementarea iterativa a algoritmului Horn-Schunck.
    Referinta formule:.
    """
    im1 = im1.astype(np.float32)
    im2 = im2.astype(np.float32)
    
    Ix, Iy, It = compute_derivatives(im1, im2)
    
    # Initializare vectori u, v cu zero
    u = np.zeros_like(im1)
    v = np.zeros_like(im1)
    
    # Kernel pentru media vecinilor (Average velocity)
    # [0 1/4 0; 1/4 0 1/4; 0 1/4 0] este o aproximare Laplaciană comuna
    avg_kernel = np.array([[0, 1, 0],
                           [1, 0, 1],
                           [0, 1, 0]]) / 4.0
    
    for _ in range(iterations):
        # Calculeaza mediile locale u_bar si v_bar
        u_avg = convolve2d(u, avg_kernel, mode='same', boundary='symm')
        v_avg = convolve2d(v, avg_kernel, mode='same', boundary='symm')
        
        # Termenul de actualizare (numitorul comun)
        # P = (Ix * u_avg + Iy * v_avg + It) / (alpha^2 + Ix^2 + Iy^2)
        P = (Ix * u_avg + Iy * v_avg + It) / (alpha**2 + Ix**2 + Iy**2 + 1e-6)
        
        # Actualizare iterativa u si v [cite: 38]
        u = u_avg - Ix * P
        v = v_avg - Iy * P
        
    return u, v

if __name__ == "__main__":
    print("Acesta este un modul de biblioteca. Ruleaza 'generate_test_data.py' pentru test.")