FROM python:3-slim

# Install basic data science packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib
    # scipy

# Set working directory
WORKDIR /app

# Copy your application code
COPY . .

# Change CMD to run bash instead of python
CMD ["/bin/bash"]

# Usage instructions in comments
# docker build -t my_datascience .
# docker run -it -v $(pwd):/app my_datascience
