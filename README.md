# FPGA-Accelerated Dense Optical Flow using Pyramidal Horn-Schunck

**Authors:** Dumitrescu Alex-Cezar ; Serban Mihnea-Alexandru ; Morarasu Alexandru
**Institution:** UPB ACS
**Target Platform:** Xilinx Artix-7 FPGA
**Implementation Language:** PyMTL3 (Python to Verilog Translation)

## 1. Project Overview

This repository contains a hardware implementation of the Horn-Schunck algorithm for real-time dense optical flow estimation. Unlike sparse methods (e.g., Lucas-Kanade), this architecture computes a motion vector for every pixel in the frame.

The design utilizes a **Multi-Scale Pyramidal Approach** (2-Level) to handle large displacements effectively. The hardware architecture is based on a Stream Processing paradigm, utilizing internal line buffers to perform 3x3 window operations without requiring external frame storage (DRAM).

The implementation is written in PyMTL3, a Python-based Hardware Generation Framework, which allows for high-level modeling, bit-accurate simulation, and automatic translation to Verilog for synthesis.

## 2. System Architecture

The processing pipeline consists of the following hierarchical modules:

### 2.1. Pyramidal Top Level
The system splits the input video stream into two processing paths to improve accuracy:
* **Coarse Level (32x32):** The input image is downsampled. A preliminary flow field is computed to detect large movements.
* **Fine Level (64x64):** The result from the coarse level is upsampled and used as an "Initial Guess". The algorithm refines this guess to produce high-precision motion vectors.

### 2.2. Core Components
* **LineBuffer:** Implements a circular buffer to store 2 lines of video, creating a sliding 3x3 window for processing.
* **GradientUnit:** Computes spatial derivatives (Ix, Iy) using Sobel filters and temporal derivatives (It) in parallel.
* **HSCore:** The arithmetic engine that solves the Horn-Schunck global energy minimization equation using Q4.12 Fixed-Point arithmetic.
* **Downsampler/Upsampler:** Handles resolution scaling and vector projection between pyramid levels.

## 3. Directory Structure

project_root/
  src/
    pyramidal_of_top.py    # Top-level 2-Scale Architecture
    optical_flow_top.py    # Single-Scale Pipeline
    hs_core.py             # Math Engine (Q4.12 Fixed Point)
    gradient_unit.py       # Sobel & Time Derivatives
    line_buffer.py         # Memory Management
    downsampler.py         # 2x2 Averaging
    upsampler.py           # Vector Projection
  
  tests/
    test_system_pyramid.py # Full System Verification
    test_hs_core.py        # Math Unit Unit-Test
    ...

  golden_model/
    generate_test_data.py  # Synthetic Moving Square generation
    lucas_kanade_sw.py     # Software Baseline reference

  scripts/
    synth_all.ys           # Yosys Synthesis Script
    PyramidalOpticalFlow.v # Generated Verilog Source

## 4. Key Features & Specifications

* **Precision:** Q4.12 Signed Fixed-Point Arithmetic (1 sign bit, 3 integer bits, 12 fractional bits).
* **Throughput:** 1 pixel per clock cycle (after pipeline latency).
* **Memory Strategy:** Pure Stream Processing (No Frame Buffer required).
* **Algorithm:** Iterative Horn-Schunck with Global Smoothness Constraint (alpha=10 for coarse, alpha=5 for fine).

## 5. Simulation and Verification

The design was verified against a Python Golden Model using synthetic datasets (Moving Square Test).

To run the full system simulation:
  python tests/test_system_pyramid.py

**Verification Results:**
* Single Scale approach: ~0.5 magnitude recovery (slow convergence).
* Pyramidal approach: ~0.75 magnitude recovery (fast convergence).

## 6. Synthesis Results (Artix-7)

Synthesis was performed using Yosys Open Synthesis Suite targeting the Xilinx Artix-7 (xc7) architecture.

**Resource Utilization Summary:**

| Resource | Single Scale | Pyramidal (Dual Core) |
| :--- | :--- | :--- |
| Logic Cells (LCs) | ~12,800 | ~25,000 |
| Registers (FF) | ~1,100 | ~1,850 |
| DSP Blocks | 2 | 4 |

The significant increase in Logic Cells in the pyramidal version is justified by the duplication of the math core (HSCore), which allows for parallel processing of both resolution scales, resulting in a 50% improvement in motion detection accuracy.

## 7. Hardware vs. Software Trade-off

* **Horn-Schunck (FPGA):** Selected for hardware acceleration due to its iterative nature and global data dependency, which maps efficiently to deep pipelines.
* **Lucas-Kanade (Software):** Implemented in Python as a baseline. While LK is robust, its requirement for per-window matrix inversion (A^T * A) makes it computationally expensive for FPGA resources compared to the stream-friendly HS approach.

## 8. Build Instructions

1.  Install dependencies:
    pip install pymtl3 numpy pytest

2.  Generate Verilog:
    python scripts/linux_translate.py

3.  Run Synthesis:
    yosys scripts/synth_all.ys

## 9. License

This project is developed for educational purposes as part of the Computer Architecture course.