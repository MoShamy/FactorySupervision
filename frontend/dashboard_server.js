require("dotenv").config();
const express = require("express");
const { OpenAI } = require("openai");
const path = require("path");

const app = express();
app.use(express.json());
const cors = require("cors");
app.use(cors());

// Serve static files from the current directory
app.use(express.static(path.join(__dirname)));

// Azure OpenAI config
const openai = new OpenAI({
  apiKey: process.env.AZURE_API_KEY,
  baseURL: `${process.env.AZURE_ENDPOINT}/openai/deployments/${process.env.AZURE_DEPLOYMENT_NAME}`,
  defaultQuery: {
    "api-version": process.env.AZURE_API_VERSION
  },
  defaultHeaders: {
    "api-key": process.env.AZURE_API_KEY
  }
});

// Health check endpoint
app.get("/health", async (req, res) => {
  const health = {
    status: "healthy", 
    timestamp: new Date().toISOString(),
    services: {
      openai: process.env.AZURE_API_KEY ? "configured" : "missing_config",
      fastapi_backend: "checking..."
    }
  };
  
  // Check FastAPI backend connectivity
  try {
    const response = await fetch('http://localhost:8000/status', { 
      method: 'GET',
      timeout: 3000 
    });
    health.services.fastapi_backend = response.ok ? "connected" : "error";
    health.services.backend_status = response.ok ? await response.text() : "unavailable";
  } catch (error) {
    health.services.fastapi_backend = "disconnected";
    health.services.backend_error = error.message;
  }
  
  res.json(health);
});

// Serve the dashboard
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "factory_dashboard.html"));
});

// Real backend functions integrated with FastAPI backend
async function get_machine_status() {
  try {
    // Call FastAPI backend for real status
    const response = await fetch('http://localhost:8000/status');
    if (response.ok) {
      const data = await response.json();
      return {
        status: data.status,
        timestamp: new Date().toISOString(),
        system_health: data.status === "Running" ? "Normal" : "Alert",
        production_line: data.status === "Running" ? "Active" : "Inactive",
        source: "FastAPI Backend"
      };
    } else {
      throw new Error(`FastAPI responded with ${response.status}`);
    }
  } catch (error) {
    console.error("Error connecting to FastAPI backend:", error);
    
    // Fallback: Read direct from status file
    try {
      const fs = require('fs');
      const path = require('path');
      const statusPath = path.join(__dirname, '../config/system_status.py');
      
      if (fs.existsSync(statusPath)) {
        const statusContent = fs.readFileSync(statusPath, 'utf8');
        const functioningMatch = statusContent.match(/functioning\s*=\s*(True|False)/);
        const functioning = functioningMatch ? functioningMatch[1] === 'True' : true;
        
        return {
          status: functioning ? "Running" : "Stopped",
          timestamp: new Date().toISOString(),
          system_health: functioning ? "Normal" : "Alert",
          production_line: functioning ? "Active" : "Inactive",
          source: "Direct File Access (Fallback)",
          backend_error: error.message
        };
      }
    } catch (fallbackError) {
      console.error("Fallback also failed:", fallbackError);
    }
    
    return { 
      status: "Unknown", 
      error: `Backend unavailable: ${error.message}`,
      timestamp: new Date().toISOString(),
      source: "Error State"
    };
  }
}

async function get_activity_log() {
  try {
    const fs = require('fs');
    const path = require('path');
    const logPath = path.join(__dirname, '../logs/production_status.log');
    
    if (fs.existsSync(logPath)) {
      const logContent = fs.readFileSync(logPath, 'utf8');
      const lines = logContent.split('\n').filter(line => line.trim()).slice(-15); // Last 15 entries
      
      return {
        Log: lines.join('\n') || "No recent activity recorded",
        entries_count: lines.length,
        last_updated: new Date().toISOString(),
        source: "Production Log File"
      };
    }
    
    // If no log file, generate a meaningful default
    return {
      Log: `Production System Status Log:
${new Date().toLocaleString()}: System monitoring active
${new Date(Date.now() - 1800000).toLocaleString()}: Computer vision analysis running  
${new Date(Date.now() - 3600000).toLocaleString()}: YOLO detection model loaded
${new Date(Date.now() - 5400000).toLocaleString()}: FastAPI backend started
${new Date(Date.now() - 7200000).toLocaleString()}: Motion detection system initialized`,
      note: "Production log file not found - showing system status",
      source: "Generated Status Log"
    };
  } catch (error) {
    console.error("Error reading activity log:", error);
    return {
      Log: "Error accessing production logs",
      error: error.message,
      timestamp: new Date().toISOString(),
      source: "Error State"
    };
  }
}

async function get_computer_vision_data() {
  try {
    // Try to get data from FastAPI backend first
    const newVideosResponse = await fetch('http://localhost:8000/new-videos');
    let backendData = null;
    
    if (newVideosResponse.ok) {
      backendData = await newVideosResponse.json();
    }
    
    // Also check local file system for comprehensive data
    const fs = require('fs');
    const path = require('path');
    
    const resultsPath = path.join(__dirname, '../Results/Processed_Videos');
    const analysisPath = path.join(__dirname, '../Results/Analysis_Reports');
    const modelsPath = path.join(__dirname, '../Our_Models/Best_Models');
    
    let videoFiles = [];
    let analysisFiles = [];
    let modelFiles = [];
    
    if (fs.existsSync(resultsPath)) {
      videoFiles = fs.readdirSync(resultsPath).filter(f => f.endsWith('.mp4'));
    }
    
    if (fs.existsSync(analysisPath)) {
      analysisFiles = fs.readdirSync(analysisPath).filter(f => f.endsWith('.txt'));
    }
    
    if (fs.existsSync(modelsPath)) {
      modelFiles = fs.readdirSync(modelsPath).filter(f => f.endsWith('.pt'));
    }
    
    return {
      // FastAPI backend data
      new_videos_detected: backendData?.new_videos?.length || 0,
      recent_detections: backendData?.new_videos || [],
      
      // File system data
      total_processed_videos: videoFiles.length,
      analysis_reports: analysisFiles.length,
      available_models: modelFiles.length,
      last_processed: videoFiles.length > 0 ? videoFiles[videoFiles.length - 1] : "None",
      latest_analysis: analysisFiles.length > 0 ? analysisFiles[analysisFiles.length - 1] : "None",
      
      // System status
      backend_connected: backendData !== null,
      yolo_model_active: modelFiles.includes('bestdet.pt'),
      motion_detection: backendData !== null,
      
      timestamp: new Date().toISOString(),
      source: "Integrated FastAPI + File System"
    };
  } catch (error) {
    console.error("Error getting computer vision data:", error);
    return {
      error: "Computer vision system not accessible",
      details: error.message,
      timestamp: new Date().toISOString(),
      source: "Error State"
    };
  }
}

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message || "What machines have had running issues?";
  const context = req.body.context || "general";
  
  console.log(`💬 Chat request: "${userMessage}" [${context}]`);

  const functions = [
    {
      name: "get_machine_status",
      description: "Check if the production line and machines are running, including system health status",
      parameters: {
        type: "object",
        properties: {}
      }
    },
    {
      name: "get_activity_log",
      description: "Get the recent activity log and production history",
      parameters: {
        type: "object",
        properties: {}
      }
    },
    {
      name: "get_computer_vision_data",
      description: "Get computer vision system status, processed videos, and YOLO detection analytics",
      parameters: {
        type: "object",
        properties: {}
      }
    }
  ];

  const systemPrompt = `You are an AI assistant for a factory supervision system. You help with:
- Production monitoring and machine status
- Alert analysis and troubleshooting  
- Performance metrics and reports
- Safety and compliance guidance

Keep responses concise, helpful, and focused on factory operations. Use technical language appropriate for factory supervisors and engineers.`;

  const messages = [
    { role: "system", content: systemPrompt },
    { role: "user", content: userMessage }
  ];

  try {
    console.log("🤖 Sending request to Azure OpenAI...");
    
    const response = await openai.chat.completions.create({
      messages,
      functions,
      function_call: "auto",
      model: process.env.AZURE_DEPLOYMENT_NAME,
      temperature: 0.7,
      max_tokens: 500
    });

    const responseMessage = response.choices[0].message;
    console.log("✅ Received response from OpenAI");

    if (responseMessage.function_call) {
      console.log(`🔧 Function called: ${responseMessage.function_call.name}`);
      let functionResponse;

      if (responseMessage.function_call.name === "get_machine_status") {
        functionResponse = await get_machine_status();
      } else if (responseMessage.function_call.name === "get_activity_log") {
        functionResponse = await get_activity_log();
      } else if (responseMessage.function_call.name === "get_computer_vision_data") {
        functionResponse = await get_computer_vision_data();
      }

      messages.push(responseMessage);
      messages.push({
        role: "function",
        name: responseMessage.function_call.name,
        content: JSON.stringify(functionResponse)
      });

      const finalResponse = await openai.chat.completions.create({
        messages,
        model: process.env.AZURE_DEPLOYMENT_NAME,
        temperature: 0.7,
        max_tokens: 500
      });

      console.log("✅ Function response processed");
      res.json({ 
        reply: finalResponse.choices[0].message.content,
        function_used: responseMessage.function_call.name,
        timestamp: new Date().toISOString()
      });
    } else {
      console.log("💭 Direct response provided");
      res.json({ 
        reply: responseMessage.content,
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    console.error("❌ Chat error:", error);
    
    let errorMessage = "I'm experiencing technical difficulties. ";
    if (error.code === 'ENOTFOUND') {
      errorMessage += "Cannot connect to Azure OpenAI service.";
    } else if (error.status === 401) {
      errorMessage += "Authentication failed - check API key configuration.";
    } else if (error.status === 429) {
      errorMessage += "Service is busy, please try again in a moment.";
    } else {
      errorMessage += "Please try again or contact support.";
    }
    
    res.status(500).json({ 
      error: errorMessage,
      timestamp: new Date().toISOString(),
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🏭 Factory Dashboard Server Started`);
  console.log(`📡 Server: http://localhost:${PORT}`);
  console.log(`🤖 Chat API: http://localhost:${PORT}/chat`);
  console.log(`💚 Health: http://localhost:${PORT}/health`);
  console.log(`🔑 OpenAI: ${process.env.AZURE_API_KEY ? '✅ Configured' : '❌ Missing'}`);
  console.log(`---`);
});
