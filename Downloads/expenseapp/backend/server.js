// 1. Import necessary "Tools" (Libraries)
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const sequelize = require('./config/database'); // We will create this next!

// 2. Load Environment Variables (Secrets from your .env file)
dotenv.config();

// 3. Initialize the Express Application
const app = express();

// 4. Global Middleware
// Allow different websites (like your React frontend) to talk to this API
app.use(cors()); 
// Tell the server to understand JSON data sent in a request body
app.use(express.json()); 

// 5. Define Routes (The "Doors" of your server)
// Note: We will create these files in the next steps. 
// For now, we "Import" them here.
const authRoutes = require('./routes/authRoutes');
const transactionRoutes = require('./routes/transactionRoutes');

// Use the routes
app.use('/api/auth', authRoutes);
app.use('/api/transactions', transactionRoutes);

// 6. A "Welcome" Route
// If you visit http://localhost:5000/ in your browser, you'll see this.
app.get('/', (req, res) => {
    res.json({ message: "Welcome to Bellcorp Expense Tracker API!" });
});

// 7. Database Sync & Server Start
const PORT = process.env.PORT || 5000;

// This function checks if the Database is connected before starting the server
const startServer = async () => {
    try {
        // Authenticate connection to SQLite
        await sequelize.authenticate();
        console.log('✅ SQLite Database connected successfully.');

        // Sync Models (This creates the tables in your database automatically)
        await sequelize.sync({ force: false }); 
        console.log('✅ Database Tables Synced.');

        // Start listening for requests
        app.listen(PORT, () => {
            console.log(`🚀 Server is running on http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error('❌ Unable to connect to the database:', error);
    }
};

startServer();