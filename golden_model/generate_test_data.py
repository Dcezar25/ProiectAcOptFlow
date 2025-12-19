import numpy as np
import cv2
import matplotlib.pyplot as plt
from horn_schunck_ref import horn_schunck_optical_flow

def create_moving_square(size=64, shift_x=1, shift_y=1):
    img1 = np.zeros((size, size), dtype=np.uint8)
    img2 = np.zeros((size, size), dtype=np.uint8)
    
    # Desenam un patrat in centrul imaginii 1
    cv2.rectangle(img1, (20, 20), (44, 44), 255, -1)
    
    # Desenam acelasi patrat in imaginea 2, dar deplasat
    cv2.rectangle(img2, (20+shift_x, 20+shift_y), (44+shift_x, 44+shift_y), 255, -1)
    
    return img1, img2

def visualize_flow(img, u, v):
    # Functie pentru a desena vectorii de miscare (Quiver plot)
    y, x = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title("Frame 1")
    
    plt.subplot(1, 2, 2)
    # Afisam doar 1 din 2 vectori pentru claritate
    step = 2
    plt.quiver(x[::step, ::step], y[::step, ::step], 
               u[::step, ::step], -v[::step, ::step], color='r')
    plt.imshow(img, cmap='gray', alpha=0.5)
    plt.title("Optical Flow Field (Horn-Schunck)")
    
    plt.show()

if __name__ == "__main__":
    # 1. Genereaza date sintetice
    print("Generating synthetic frames...")
    im1, im2 = create_moving_square(size=64, shift_x=1, shift_y=0)
    
    # 2. Ruleaza Golden Model
    print("Running Horn-Schunck Reference...")
    # alpha mic = regularizare slaba (bun pentru contururi nete)
    # alpha mare = flow foarte neted
    u, v = horn_schunck_optical_flow(im1, im2, alpha=0.5, iterations=50)
    
    # 3. Verifica rezultatele
    print(f"Max U (asteptat aprox 1.0): {np.max(u):.4f}")
    print(f"Max V (asteptat aprox 0.0): {np.max(v):.4f}")
    
    # 4. Salveaza datele pentru testbench-ul hardware (Pasul urmator)
    np.save("golden_model/ref_u.npy", u)
    np.save("golden_model/ref_v.npy", v)
    
    # 5. Vizualizeaza
    visualize_flow(im1, u, v)