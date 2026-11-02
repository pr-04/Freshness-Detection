/** Send the selected image and user-chosen fruit to Express/FastAPI. */
export const analyzeImage = async (file, fruit) => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
  const endpoint = `${baseUrl}/api/scans`;

  try {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('fruit', fruit);

    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData,
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error('The analysis server returned an invalid response. Please try again.');
    }

    if (!response.ok || !data.success) {
      throw new Error(data.message || 'Analysis request failed.');
    }

    const prediction = data.prediction?.prediction;
    if (!data.scan || !prediction || typeof prediction.freshness !== 'string') {
      throw new Error('The analysis server returned an invalid prediction. Please try again.');
    }
    return { scan: data.scan, prediction };
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the Express analysis server. Please check that it is running.');
    }
    throw error;
  }
};
