require("dotenv").config();
const express = require("express");
const { OpenAI } = require("openai");

const app = express();
app.use(express.json());
const cors = require("cors");
app.use(cors());

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

// Simulated backend functions
function get_machine_status() {
  return { status: "Running" };
}

function get_activity_log() {
  return {
    Log: `Machine 1: Stopped Tuesday 11:30 AM
Machine 1: Started working again Tuesday 3:30 PM
Machine 3: Stopped Tuesday 11:30 AM
Machine 2: Stopped Tuesday 11:30 AM`
  };
}

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message || "What machines have had running issues?";

  const functions = [
    {
      name: "get_machine_status",
      description: "Check if the machine is running",
      parameters: {
        type: "object",
        properties: {}
      }
    },
    {
      name: "get_activity_log",
      description: "Get the activity log of the machine",
      parameters: {
        type: "object",
        properties: {}
      }
    }
  ];

  const messages = [
    { role: "user", content: userMessage }
  ];

  try {
    const response = await openai.chat.completions.create({
      messages,
      functions,
      function_call: "auto",
      model: process.env.AZURE_DEPLOYMENT_NAME
    });

    const responseMessage = response.choices[0].message;

    if (responseMessage.function_call) {
      let functionResponse;

      if (responseMessage.function_call.name === "get_machine_status") {
        functionResponse = get_machine_status();
      } else if (responseMessage.function_call.name === "get_activity_log") {
        functionResponse = get_activity_log();
      }

      messages.push(responseMessage);
      messages.push({
        role: "function",
        name: responseMessage.function_call.name,
        content: JSON.stringify(functionResponse)
      });

      const finalResponse = await openai.chat.completions.create({
        messages,
        model: process.env.AZURE_DEPLOYMENT_NAME
      });

      res.json({ reply: finalResponse.choices[0].message.content });
    } else {
      res.json({ reply: responseMessage.content });
    }
  } catch (error) {
    console.error("Chat error:", error);
    res.status(500).json({ error: "Failed to get chat completion." });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});
