const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Add cache-control headers for CSS files to prevent caching issues
app.use('/assets/css', (req, res, next) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
});

// Serve static files from the frontend directory
app.use(express.static(path.join(__dirname), {
  maxAge: 0,
  etag: false
}));

// Route for the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Route for pages
app.get('/pages/:page', (req, res) => {
  const page = req.params.page;
  const filePath = path.join(__dirname, 'pages', `${page}.html`);
  res.sendFile(filePath, (err) => {
    if (err) {
      res.status(404).send('Page not found');
    }
  });
});

// Chat endpoint (simplified without OpenAI for now)
app.use(express.json());
app.post('/api/chat', (req, res) => {
  const { message } = req.body;
  
  // Simple mock response for demo with factory-specific responses
  const responses = [
    "🏭 Production system monitoring active. All lines operational.",
    "📊 Current efficiency: Production Line A: 95%, Line B: 87%, Line C: 92%",
    "✅ Quality control metrics are within acceptable ranges.",
    "🔍 Computer vision analysis detected 23 objects in the last batch.",
    "⚠️ Minor vibration detected on Machine #3 - scheduling maintenance.",
    "📈 Today's output: 1,247 units produced, 98.3% quality rate.",
    "🤖 YOLO detection model is running optimally.",
    "💡 Suggestion: Consider increasing Line B speed by 5% for optimal throughput."
  ];
  
  const response = responses[Math.floor(Math.random() * responses.length)];
  
  res.json({ 
    response: response,
    timestamp: new Date().toISOString(),
    status: "success"
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: "healthy",
    server: "Simple Frontend Server",
    timestamp: new Date().toISOString(),
    css_cache: "disabled"
  });
});

app.listen(PORT, () => {
  console.log(`🌐 Frontend server running at http://localhost:${PORT}`);
  console.log(`💬 Chat API available at http://localhost:${PORT}/api/chat`);
  console.log(`💚 Health check at http://localhost:${PORT}/health`);
  console.log(`🎨 CSS cache disabled for development`);
  console.log(`---`);
});
