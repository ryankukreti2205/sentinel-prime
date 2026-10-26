// 1. Load environment variables first
require('dotenv').config(); 

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();

// 2. Middleware - THE FIX FOR 403
// This tells the server to allow requests from any origin (Python/Browser)
app.use(cors()); 

// These allow the server to "read" the data Python sends
app.use(express.json()); 
app.use(express.urlencoded({ extended: true }));

// 3. Database Connection
mongoose.connect(process.env.MONGO_URI)
    .then(() => console.log("✅ Connected to MongoDB Atlas successfully"))
    .catch(err => {
        console.error("❌ Database connection error:", err.message);
        process.exit(1);
    });

// 4. Data Model (Schema)
const LogSchema = new mongoose.Schema({
    object: { type: String, required: true },
    confidence: { type: Number, required: true },
    timestamp: { type: Date, default: Date.now }
});
const Log = mongoose.model('Log', LogSchema);

// 5. API Routes

// Health Check Route
app.get('/', (req, res) => {
    res.send("Sentinel Backend is LIVE! 🚀");
});

// The Bridge Route: Where Python sends data
app.post('/api/logs', async (req, res) => {
    try {
        // This will print the incoming AI data in your Terminal!
        console.log("📥 Received from AI:", req.body); 

        const newLog = new Log({
            object: req.body.object,
            confidence: req.body.confidence
        });

        await newLog.save();
        
        // Sending 201 back to Python
        res.status(201).json({ message: "Log saved successfully!" });
    } catch (err) {
        console.error("❌ Error saving log:", err.message);
        res.status(500).json({ error: "Server Error", details: err.message });
    }
});

// Route for the Frontend (we'll use this in Sprint 3)
app.get('/api/logs', async (req, res) => {
    try {
        const logs = await Log.find().sort({ timestamp: -1 }).limit(10);
        res.json(logs);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 6. Start the Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 Sentinel Backend running at http://localhost:${PORT}`);
});