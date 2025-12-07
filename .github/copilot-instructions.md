# GitHub Copilot Instructions

## Repository Overview

This repository contains coursework and projects for the GPU Programming Specialization from Johns Hopkins University. The focus is on parallel computing, GPU architecture, and high-performance computing using GPUs.

## Code Style and Conventions

### General Guidelines
- Write clean, well-documented code with clear comments explaining complex GPU operations
- Use descriptive variable names that reflect their purpose in parallel computing contexts
- Include performance metrics and benchmarking code where applicable

### CUDA/GPU Programming
- Always check for CUDA errors after kernel launches and API calls
- Use appropriate memory management (cudaMalloc, cudaFree, cudaMemcpy)
- Document kernel launch configurations (grid size, block size) and explain the reasoning
- Consider memory coalescing patterns for optimal performance
- Use shared memory when appropriate for performance optimization
- Always synchronize devices when necessary (cudaDeviceSynchronize)

### Performance Considerations
- Profile code to identify bottlenecks before optimizing
- Document expected performance characteristics and achieved speedups
- Compare GPU implementations with CPU baseline implementations
- Consider memory bandwidth limitations and computational intensity

## Documentation Standards

- Include README files for each assignment or project explaining:
  - Problem description
  - Approach and algorithm used
  - How to compile and run the code
  - Expected output and performance metrics
- Comment complex kernel code with:
  - Thread indexing calculations
  - Memory access patterns
  - Synchronization points

## Build and Testing

- Include compilation instructions for CUDA code (nvcc compiler flags)
- Specify required CUDA toolkit version and compute capability
- Provide sample inputs and expected outputs for validation
- Include instructions for running on different GPU architectures if applicable

## Learning Resources

- Reference relevant course materials and lectures when implementing concepts
- Link to CUDA programming guides and best practices documentation
- Note any specific GPU programming patterns or techniques being demonstrated

## Common Patterns

### Kernel Launch Template
```cuda
// Define block size (threads per block)
#define BLOCK_SIZE 256

// N is the total number of elements to process
// Calculate grid and block dimensions
dim3 blockDim(BLOCK_SIZE);
dim3 gridDim((N + BLOCK_SIZE - 1) / BLOCK_SIZE);

// Launch kernel
kernelName<<<gridDim, blockDim>>>(args);

// Check for launch errors
cudaError_t err = cudaGetLastError();
if (err != cudaSuccess) {
    fprintf(stderr, "Kernel launch failed: %s\n", cudaGetErrorString(err));
}
```

### Memory Management Pattern
```cuda
// Host arrays
float *h_data = (float*)malloc(size * sizeof(float));
float *h_result = (float*)malloc(size * sizeof(float));

// Allocate device memory
float *d_data, *d_result;
cudaMalloc(&d_data, size * sizeof(float));
cudaMalloc(&d_result, size * sizeof(float));

// Copy data to device
cudaMemcpy(d_data, h_data, size * sizeof(float), cudaMemcpyHostToDevice);

// [Perform GPU operations on d_data, store results in d_result]

// Copy results back to host
cudaMemcpy(h_result, d_result, size * sizeof(float), cudaMemcpyDeviceToHost);

// Free device memory
cudaFree(d_data);
cudaFree(d_result);

// Free host memory
free(h_data);
free(h_result);
```

## Academic Integrity

- This is coursework from an academic program
- Ensure all code submissions are original work
- Properly cite any external resources, libraries, or code snippets used
- Follow Johns Hopkins University's academic integrity policies
