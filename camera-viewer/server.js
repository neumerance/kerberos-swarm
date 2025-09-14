const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for React development
app.use(cors({
  origin: 'http://localhost:3000', // React dev server
  credentials: true
}));

app.use(express.json());

// API endpoint to read config.yml
app.get('/api/config', (req, res) => {
  try {
    // Path to the root config.yml (one level up from camera-viewer)
    const configPath = path.join(__dirname, '..', 'config.yml');
    
    // Check if config file exists
    if (!fs.existsSync(configPath)) {
      return res.status(404).json({ 
        error: 'Configuration file not found',
        path: configPath 
      });
    }

    // Read and parse the YAML file
    const configData = fs.readFileSync(configPath, 'utf8');
    const config = yaml.load(configData);
    
    // Return the configuration
    res.json(config);
    
  } catch (error) {
    console.error('Error reading config file:', error);
    res.status(500).json({ 
      error: 'Failed to read configuration file',
      details: error.message 
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`API Server running on port ${PORT}`);
  console.log(`Config endpoint: http://localhost:${PORT}/api/config`);
});
